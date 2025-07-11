import os
import torch
import yaml
import jiwer
import argparse
import pandas as pd

from tqdm import tqdm
import torchaudio.compliance.kaldi as kaldi
from pydub import AudioSegment
from contextlib import nullcontext

from model.utils.init_model import init_model
from model.utils.checkpoint import load_checkpoint
from model.utils.file_utils import read_symbol_table
from model.utils.ctc_utils import get_output_with_timestamps, get_output


def init_model_and_dict(model_checkpoint, device):
    config_path = os.path.join(model_checkpoint, "config.yaml")
    checkpoint_path = os.path.join(model_checkpoint, "pytorch_model.bin")
    vocab_path = os.path.join(model_checkpoint, "vocab.txt")

    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    model = init_model(config, config_path)
    model.eval()
    load_checkpoint(model, checkpoint_path)
    model.encoder = model.encoder.to(device)
    model.ctc = model.ctc.to(device)

    symbol_table = read_symbol_table(vocab_path)
    char_dict = {v:k for k,v in symbol_table.items()}
    return model, char_dict


def load_audio(audio_path):
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_frame_rate(16000).set_sample_width(2).set_channels(1)
    samples = torch.as_tensor(audio.get_array_of_samples(), dtype=torch.float32).unsqueeze(0)
    return samples


def decode_stream(audio_path, model, char_dict, args, write_timestamps=False):

    def get_max_input_context(c, r, n): return r + max(c, r) * (n - 1)
    device = next(model.parameters()).device
    subsamp = model.encoder.embed.subsampling_factor
    conv_order = model.encoder.cnn_module_kernel // 2
    cs, lc, rc = args.chunk_size, args.left_context_size, args.right_context_size

    max_ctx = int((args.total_batch_duration // 0.01)) // 2
    n = max_ctx // cs // subsamp
    trunc_size = cs * n
    rel_rc = get_max_input_context(cs, max(rc, conv_order), model.encoder.num_blocks) * subsamp

    waveform = load_audio(audio_path)
    xs = kaldi.fbank(waveform, num_mel_bins=80, frame_length=25,
                     frame_shift=10, dither=0.0, energy_floor=0.0,
                     sample_frequency=16000).unsqueeze(0)
    offset = torch.zeros(1, dtype=torch.int, device=device)
    att_cache = torch.zeros((model.encoder.num_blocks, lc, model.encoder.attention_heads,
                             model.encoder._output_size*2//model.encoder.attention_heads), device=device)
    cnn_cache = torch.zeros((model.encoder.num_blocks, model.encoder._output_size, conv_order), device=device)

    hyps = []
    step = trunc_size * subsamp
    for start in range(0, xs.shape[1], step):
        end = min(start + step + rel_rc, xs.shape[1])
        x = xs[:, start:end]
        x_len = torch.tensor([x.shape[1]], device=device)
        outs, outs_len, _, att_cache, cnn_cache, offset = model.encoder.forward_parallel_chunk(
            xs=x, xs_origin_lens=x_len,
            chunk_size=cs, left_context_size=lc, right_context_size=rc,
            att_cache=att_cache, cnn_cache=cnn_cache,
            truncated_context_size=trunc_size, offset=offset
        )
        outs = outs.reshape(1, -1, outs.shape[-1])[:, :outs_len]
        hyp = model.encoder.ctc_forward(outs).squeeze(0)
        hyps.append(hyp)
        offset = offset - outs_len + outs.shape[1]
        if device.type == "cuda": torch.cuda.empty_cache()
        if start + step + rel_rc >= xs.shape[1]: break

    hyps = torch.cat(hyps)
    if write_timestamps:
        segments = get_output_with_timestamps([hyps], char_dict)[0]
        return segments
    else:
        text = get_output([hyps], char_dict)
        return " ".join(text).lower()


def batch_decode_list(audio_list, model, char_dict, args):
    df = pd.read_csv(audio_list, sep="\t")
    decodes = []
    for path in tqdm(df['wav'].tolist()):
        decodes.append(decode_stream(path, model, char_dict, args, write_timestamps=False))
    df['decode'] = decodes
    if 'txt' in df:
        wer = jiwer.wer(df['txt'].tolist(), decodes)
        print(f"WER: {wer:.2f}")
    df.to_csv(audio_list, sep="\t", index=False)


def folder_decode(audio_dir, output_dir, model, char_dict, args):
    os.makedirs(output_dir, exist_ok=True)
    for fname in tqdm(os.listdir(audio_dir)):
        if not fname.lower().endswith(('.wav','.flac','.mp3','.m4a')): continue
        in_path = os.path.join(audio_dir, fname)
        transcript = decode_stream(in_path, model, char_dict, args, write_timestamps=False)
        out_name = os.path.splitext(fname)[0] + '.txt'
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
    print("Folder transcription complete.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_checkpoint", type=str, required=True)
    parser.add_argument("--audio_list", type=str, help="TSV with 'wav' column for batch decode")
    parser.add_argument("--long_form_audio", type=str, help="Single audio file for streaming decode")
    parser.add_argument("--audio_dir", type=str, help="Folder of audio files to decode to txts")
    parser.add_argument("--output_dir", type=str, help="Folder to save transcripts")
    parser.add_argument("--total_batch_duration", type=int, default=1800)
    parser.add_argument("--chunk_size", type=int, default=64)
    parser.add_argument("--left_context_size", type=int, default=128)
    parser.add_argument("--right_context_size", type=int, default=128)
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--autocast_dtype", type=str, choices=["fp32","bf16","fp16"], default=None)
    parser.add_argument("--timestamps", action="store_true", help="Include timestamps when streaming decode")
    args = parser.parse_args()

    device = torch.device(args.device)
    dtype = { 'fp32': torch.float32, 'bf16': torch.bfloat16, 'fp16': torch.float16 }.get(args.autocast_dtype, None)

    model, char_dict = init_model_and_dict(args.model_checkpoint, device)
    with torch.autocast(device.type, dtype) if dtype else nullcontext():
        if args.audio_dir and args.output_dir:
            folder_decode(args.audio_dir, args.output_dir, model, char_dict, args)
        elif args.long_form_audio:
            segments = decode_stream(args.long_form_audio, model, char_dict, args, write_timestamps=args.timestamps)
            if args.timestamps:
                for seg in segments:
                    print(f"{seg['start']}-{seg['end']}: {seg['decode']}")
            else:
                print(segments)
        elif args.audio_list:
            batch_decode_list(args.audio_list, model, char_dict, args)
        else:
            raise ValueError("Must specify one of --audio_dir, --long_form_audio, or --audio_list")

if __name__ == '__main__':
    main()
