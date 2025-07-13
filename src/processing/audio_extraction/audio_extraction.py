import os
import argparse
from pathlib import Path
from moviepy import VideoFileClip
from pydub import AudioSegment
import glob

def extract_audio(video_path, output_path, sample_rate=16000):
    video = VideoFileClip(str(video_path))
    audio = video.audio
    if audio is None:
        print(f"No audio in {video_path}")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    temp_wav = output_path.with_suffix('.temp.wav')
    final_wav = output_path.with_suffix('.wav')

    audio.write_audiofile(str(temp_wav), fps=sample_rate, codec='pcm_s16le', logger=None)

    audio_segment = AudioSegment.from_wav(temp_wav)
    audio_segment = (
        audio_segment.set_channels(1)
        .set_frame_rate(sample_rate)
        .set_sample_width(2)
    )
    audio_segment.export(final_wav, format="wav")
    os.remove(temp_wav) 
    print(f"Extracted: {final_wav}")

def batch_extract_audio(input_dir, output_dir, sample_rate=16000, extensions=None):
    input_dir = Path(input_dir).resolve()
    output_dir = Path(output_dir).resolve()
    extensions = extensions or [".mp4", ".mkv", ".mov", ".avi"]

    for ext in extensions:
        pattern = str(input_dir / f"**/*{ext}")
        for video_path in glob.glob(pattern, recursive=True):
            video_path = Path(video_path).resolve()
            rel_path = video_path.relative_to(input_dir)

            parts = list(rel_path.parts)
            if "video" in parts:
                parts.remove("video")

            output_rel_path = Path(*parts).with_suffix('.wav')
            output_path = output_dir / output_rel_path

            extract_audio(video_path, output_path, sample_rate)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract audio from videos and convert to mono WAV.")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory containing video files.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save extracted .wav files.")
    parser.add_argument("--sample_rate", type=int, default=16000, help="Target sample rate (default: 16000)")
    args = parser.parse_args()

    batch_extract_audio(args.input_dir, args.output_dir, args.sample_rate)
