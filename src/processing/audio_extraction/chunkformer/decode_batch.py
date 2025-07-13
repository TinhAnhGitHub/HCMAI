import os
import torch
import yaml
import json
import argparse
from tqdm import tqdm
import glob 
import cv2
from pathlib import Path
from tqdm import tqdm
from colorama import Fore, Style
import torchaudio.compliance.kaldi as kaldi
from model.utils.init_model import init_model
from model.utils.checkpoint import load_checkpoint
from model.utils.file_utils import read_symbol_table
from model.utils.ctc_utils import get_output_with_timestamps
from contextlib import nullcontext
from pydub import AudioSegment



def extract_fps(video_path: str) -> float:
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    return fps



def find_video(video_files: list[str], filename: str):
    return next(
        filter(lambda x: os.path.basename(os.path.splitext(x)[0]) == filename, video_files)    
    )


def time_to_frames(time_str: str, fps: float):
    """Convert HH:MM:SS:ms to frame number"""
    h, m, s, ms = map(int, time_str.replace(':', ' ').split())
    total_seconds = h * 3600 + m * 60 + s + ms / 1000.0
    return int(
        round(total_seconds * fps)
    )

def time_transform(decode_dict: list[dict[str, str]], video_path: str) -> None:
    fps = extract_fps(video_path)

    for sample in decode_dict:
        start_frame = time_to_frames(sample['start'], fps)
        end_frame = time_to_frames(sample['end'], fps)

        sample['start_frame'] = f"{start_frame:08d}"
        sample['end_frame'] = f"{end_frame:08d}"
    
@torch.no_grad()
def init(model_checkpoint, device):

    config_path = os.path.join(model_checkpoint, "config.yaml")
    checkpoint_path = os.path.join(model_checkpoint, "pytorch_model.bin")
    symbol_table_path = os.path.join(model_checkpoint, "vocab.txt")

    with open(config_path, 'r') as fin:
        config = yaml.load(fin, Loader=yaml.FullLoader)
    model = init_model(config, config_path)
    model.eval()
    load_checkpoint(model , checkpoint_path)

    model.encoder = model.encoder.to(device)
    model.ctc = model.ctc.to(device)
    # print('the number of encoder params: {:,d}'.format(num_params))

    symbol_table = read_symbol_table(symbol_table_path)
    char_dict = {v: k for k, v in symbol_table.items()}

    return model, char_dict

def load_audio(audio_path):
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_frame_rate(16000)
    audio = audio.set_sample_width(2)  # set bit depth to 16bit
    audio = audio.set_channels(1)  # set to mono
    audio = torch.as_tensor(audio.get_array_of_samples(), dtype=torch.float32).unsqueeze(0)
    return audio




@torch.no_grad()
def endless_decode(args, model, char_dict):    
    def get_max_input_context(c, r, n):
        return r + max(c, r) * (n-1)
    
    device = next(model.parameters()).device
    source_base = Path(args.main_folder)
    destination_base = Path(args.destination_folder)
    video_base = Path(args.video_folder)

    wav_files = glob.glob(str(source_base / "**/*.wav"), recursive=True)
    video_files = glob.glob(str(video_base / "**/*.mp4"), recursive=True)

    
    subsampling_factor = model.encoder.embed.subsampling_factor
    chunk_size = args.chunk_size
    left_context_size = args.left_context_size
    right_context_size = args.right_context_size
    conv_lorder = model.encoder.cnn_module_kernel // 2
    max_length_limited_context = args.total_batch_duration
    max_length_limited_context = int((max_length_limited_context // 0.01))//2 # in 10ms second
    multiply_n = max_length_limited_context // chunk_size // subsampling_factor
    truncated_context_size = chunk_size * multiply_n # we only keep this part for text decoding

    # get the relative right context size
    rel_right_context_size = get_max_input_context(chunk_size, max(right_context_size, conv_lorder), model.encoder.num_blocks)
    rel_right_context_size = rel_right_context_size * subsampling_factor


    for audio_path in tqdm(wav_files, desc=f"{Fore.CYAN}🔊 Processing audio files", unit="file", ncols=100, colour="cyan"):
        waveform = load_audio(audio_path)
        offset = torch.zeros(1, dtype=torch.int, device=device)
        xs = kaldi.fbank(waveform,
                            num_mel_bins=80,
                            frame_length=25,
                            frame_shift=10,
                            dither=0.0,
                            energy_floor=0.0,
                            sample_frequency=16000).unsqueeze(0)

        hyps = []
        att_cache = torch.zeros((model.encoder.num_blocks, left_context_size, model.encoder.attention_heads, model.encoder._output_size * 2 // model.encoder.attention_heads)).to(device)
        cnn_cache = torch.zeros((model.encoder.num_blocks, model.encoder._output_size, conv_lorder)).to(device)    # print(context_size)
        for idx, _ in tqdm(list(enumerate(range(0, xs.shape[1], truncated_context_size * subsampling_factor)))):
            start = max(truncated_context_size * subsampling_factor * idx, 0)
            end = min(truncated_context_size * subsampling_factor * (idx+1) + 7, xs.shape[1])

            x = xs[:, start:end+rel_right_context_size]
            x_len = torch.tensor([x[0].shape[0]], dtype=torch.int).to(device)

            encoder_outs, encoder_lens, _, att_cache, cnn_cache, offset = model.encoder.forward_parallel_chunk(xs=x, 
                                                                        xs_origin_lens=x_len, 
                                                                        chunk_size=chunk_size,
                                                                        left_context_size=left_context_size,
                                                                        right_context_size=right_context_size,
                                                                        att_cache=att_cache,
                                                                        cnn_cache=cnn_cache,
                                                                        truncated_context_size=truncated_context_size,
                                                                        offset=offset
                                                                        )
            encoder_outs = encoder_outs.reshape(1, -1, encoder_outs.shape[-1])[:, :encoder_lens]
            if chunk_size * multiply_n * subsampling_factor * idx + rel_right_context_size < xs.shape[1]:
                encoder_outs = encoder_outs[:, :truncated_context_size]  # (B, maxlen, vocab_size) # exclude the output of rel right context
            offset = offset - encoder_lens + encoder_outs.shape[1]


            hyp = model.encoder.ctc_forward(encoder_outs).squeeze(0)
            hyps.append(hyp)
            if device.type == "cuda":
                torch.cuda.empty_cache()
            if chunk_size * multiply_n * subsampling_factor * idx + rel_right_context_size >= xs.shape[1]:
                break
        hyps = torch.cat(hyps)
        decode = get_output_with_timestamps([hyps], char_dict)[0]

        relative_audio_path = Path(audio_path).relative_to(source_base)
        output_path = (destination_base / relative_audio_path).with_suffix('.json')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        stem_name = Path(audio_path).stem

        video_path = find_video(video_files, stem_name)
        time_transform(decode, video_path)

        
        with open(str(output_path), 'w', encoding='utf-8') as f:
            json.dump(decode, f, indent=4, ensure_ascii=False)

        

def main():
    parser = argparse.ArgumentParser(
        description="Batch decode all .wav files under a folder and write .json outputs."
    )

    # Model & device
    parser.add_argument(
        "--model_checkpoint",
        type=str,
        required=True,
        help="Path to the model checkpoint directory (must contain config.yaml, pytorch_model.bin, vocab.txt)"
    )
    parser.add_argument(
        "--device",
        type=torch.device,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Torch device to run the model on (default: cuda if available else cpu)"
    )
    parser.add_argument(
        "--autocast_dtype",
        type=str,
        choices=["fp32", "bf16", "fp16"],
        default=None,
        help="Dtype for torch.autocast; leave unset to disable mixed precision"
    )

    # Decoding parameters
    parser.add_argument(
        "--total_batch_duration",
        type=int,
        default=1800,
        help="Total audio duration (in seconds) per batch for GPU memory (default: 1800)"
    )
    parser.add_argument(
        "--chunk_size",
        type=int,
        default=64,
        help="Chunk size for streaming encoder (default: 64)"
    )
    parser.add_argument(
        "--left_context_size",
        type=int,
        default=128,
        help="Left context size for streaming encoder (default: 128)"
    )
    parser.add_argument(
        "--right_context_size",
        type=int,
        default=128,
        help="Right context size for streaming encoder (default: 128)"
    )

    # I/O folders
    parser.add_argument(
        "--main_folder",
        type=str,
        required=True,
        help="Root folder containing .wav files to decode (recursive)"
    )
    parser.add_argument(
        "--destination_folder",
        type=str,
        required=True,
        help="Root folder where decoded .json files will be written"
    )

    parser.add_argument(
        "--video_folder",
        type=str,
        required=True,
        help="The video folder, to convert timestamp -> frame number range "
    )

    

    args = parser.parse_args()

    # Print settings
    print(f"Model checkpoint:     {args.model_checkpoint}")
    print(f"Device:               {args.device}")
    print(f"Autocast dtype:       {args.autocast_dtype or 'none'}")
    print(f"Total batch duration: {args.total_batch_duration} s")
    print(f"Chunk size:           {args.chunk_size}")
    print(f"Left context size:    {args.left_context_size}")
    print(f"Right context size:   {args.right_context_size}")
    print(f"Input folder:         {args.main_folder}")
    print(f"Output folder:        {args.destination_folder}")
    print(f"Video  folder:        {args.video_folder}")


    assert os.path.isdir(args.main_folder), f"Input folder not found: {args.main_folder}"
    os.makedirs(args.destination_folder, exist_ok=True)

    device = torch.device(args.device)
    dtype = {
        "fp32": torch.float32,
        "bf16": torch.bfloat16,
        "fp16": torch.float16
    }.get(args.autocast_dtype, None)

    model, char_dict = init(args.model_checkpoint, device)

    with torch.autocast(device.type, dtype) if dtype is not None else nullcontext():
        endless_decode(args, model, char_dict)


if __name__ == "__main__":
    main()