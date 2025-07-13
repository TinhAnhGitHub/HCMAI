import numpy as np
import ffmpeg
from typing import Optional, List, Iterator




def get_frames(video_file_path: str, width: int = 48, height: int = 27) -> np.ndarray:
    """
    Extract frames from video 
    Args:
        video_file_path (str): Path to the video file.
        width (int): Width of the extracted frame. Default is 48
        height (int): Height of the extracted frames. Default is 27
    Returns:
        np.ndarray: Array of video frames
    """
    try:
        out, _ = (
             ffmpeg
            .input(video_file_path)
            .output('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{width}x{height}')
            .run(capture_stdout=True, capture_stderr=True)
        )
        video = np.frombuffer(out, np.uint8).reshape([-1, height, width, 3])
        return video
    except ffmpeg.Error as e:
        print(f"ffmpeg error: {e.stderr.decode()}")
        raise
    except Exception as e:
        print(f"Error in get_frames: {str(e)}")
        raise




def get_batches(
    frames: np.ndarray
) -> Iterator[np.ndarray]:
    
    if len(frames) == 0:
        return

    remainder = 50 - (len(frames) % 50)
    if remainder == 50:
        remainder = 0
    
    pad_start = 25
    pad_end = remainder + 25

    padded_frames = np.concatenate(
        [
            np.repeat(frames[:1], pad_start, axis=0),
            frames,
            np.repeat(frames[-1:], pad_end, axis=0)
        ], axis=0   
    )

    batchsize = 100
    stride = 50 
    for i in range(
        0, len(padded_frames) - stride, stride
    ):
        batch = padded_frames[i:i + batchsize]
        if len(batch) < batchsize:
            padded = batchsize - len(batch)
            batch = np.concatenate(
                [
                    batch,
                    np.repeat(batch[-1:], repeats=padded, axis=0    )
                ], axis=0   
            )
        yield batch.transpose(
            (
                1, 2, 3, 0 #* height, width, color, frames
            )
        )



