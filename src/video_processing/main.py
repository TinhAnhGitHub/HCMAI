import os
import cv2
import numpy as np
from typing import List, Iterator, Tuple, Dict, Any
import logging
from tqdm import tqdm
from pathlib import Path
import argparse

from remove_duplicate import DDTNearDuplicateRemoval
from autoshot import AutoShot


class KeyFrameExtractor:
    def __init__(self, keyframe_dir: str, verbose: bool = False):
        """
        Initialize the KeyFrameExtractor.

        Args:
            keyframe_dir (str): Directory to save extracted keyframes.
        """
        self.keyframe_dir = keyframe_dir
        self.duplicate_detector = DDTNearDuplicateRemoval(threshold=0.90, hash_size=8, verbose=verbose)
        os.makedirs(self.keyframe_dir, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO if verbose else logging.WARNING)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def sample_frames_from_shot(self, start: int, end: int, num_samples: int = 4) -> List[int]:
        """
        Sample frame indices from a shot.

        Args:
            start (int): Start frame of the shot.
            end (int): End frame of the shot.
            num_samples (int): Number of samples to take.

        Returns:
            List[int]: List of sampled frame indices.
        """
        return [start + i * (end - start) // (num_samples - 1) for i in range(num_samples)]

    def save_frame(self, frame: np.ndarray, filename: str) -> bool:
        """
        Save a frame to disk.

        Args:
            frame (np.ndarray): Frame to save.
            filename (str): Filename to save the frame as.

        Returns:
            bool: True if save was successful, False otherwise.
        """
        return cv2.imwrite(filename, frame, [int(cv2.IMWRITE_WEBP_QUALITY), 100])

    def extract_keyframes(self, video_path: str, scenes: List[List[int]], output_prefix: str) -> Iterator[Tuple[int, np.ndarray]]:
        """
        Extract keyframes from a video, removing near-duplicates.

        Args:
            video_path (str): Path to the video file.
            scenes (List[List[int]]): List of scenes, each containing start and end frame indices.
            output_prefix (str): Prefix for output filenames.

        Yields:
            Tuple[int, np.ndarray]: Tuple of frame index and frame data for unique frames.
        """
        self.logger.info(f"Processing video: {video_path}")
        cap = cv2.VideoCapture(video_path)
        unique_frames = []
        total_frames = 0
        total_unique_frames = 0
        total_duplicate_groups = 0
        total_removed_frames = 0
        try:
            for scene_idx, (start, end) in enumerate(scenes):
                sample_frames = self.sample_frames_from_shot(start, end)
                for frame_idx in sample_frames:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, float(frame_idx))
                    ret, frame = cap.read()
                    if ret:
                        unique_frames.append((frame_idx, frame))
                        if len(unique_frames) >= 50:
                            unique_indices = self.duplicate_detector.remove_near_duplicate([f for _, f in unique_frames])
                            duplicate_groups = self.duplicate_detector.find_duplicates()
                            total_duplicate_groups += len(duplicate_groups)
                            removed_frames = len(unique_frames) - len(unique_indices)
                            total_removed_frames += removed_frames
                            total_unique_frames += len(unique_indices)
                            for idx in unique_indices:
                                yield unique_frames[idx]
                            unique_frames = []
                    else:
                         self.logger.warning(f"Failed to read frame {frame_idx} for video {output_prefix}")

    
            if unique_frames:
                unique_indices = self.duplicate_detector.remove_near_duplicate([f for _, f in unique_frames])
                duplicate_groups = self.duplicate_detector.find_duplicates()
                total_duplicate_groups += len(duplicate_groups)
                removed_frames = len(unique_frames) - len(unique_indices)
                total_removed_frames += removed_frames
                total_unique_frames += len(unique_indices)
                for idx in unique_indices:
                    yield unique_frames[idx]

        finally:
            cap.release()
            self.logger.info(f"Finished processing {video_path}:")
            self.logger.info(f"Total frames processed: {total_frames}")
            self.logger.info(f"Total unique frames: {total_unique_frames}")
            self.logger.info(f"Total duplicate groups: {total_duplicate_groups}")
            self.logger.info(f"Total frames removed: {total_removed_frames}")

    def save_keyframes(self, video_path: str, scenes: List[List[int]], output_prefix: str) -> List[str]:
        """
        Extract keyframes from a video, remove near-duplicates, and save them to disk.

        Args:
            video_path (str): Path to the video file.
            scenes (List[List[int]]): List of scenes, each containing start and end frame indices.
            output_prefix (str): Prefix for output filenames.

        Returns:
            List[str]: List of saved keyframe filenames.
        """
        video_keyframe_dir = os.path.join(self.keyframe_dir, output_prefix)
        os.makedirs(video_keyframe_dir, exist_ok=True)
        
        saved_frames = []
        for frame_idx, frame in self.extract_keyframes(video_path, scenes, output_prefix):
            keyframe_filename = f"{frame_idx:08d}.webp"
            keyframe_path = os.path.join(video_keyframe_dir, keyframe_filename)
            
            if self.save_frame(frame=frame, filename=keyframe_path):
                saved_frames.append(keyframe_path)
            else:
                print(f"Failed to save frame {frame_idx} for video {output_prefix}")
        self.logger.info(f"Saved {len(saved_frames)} keyframes for {video_path}")
        return saved_frames



def process_single_video(video_path: str, shot_detector: AutoShot, keyframe_extractor: KeyFrameExtractor) -> Dict[str, Any]:
    """
    Process a single video file.

    Args:
        video_path (str): Path to the video file.
        shot_detector (AutoShot): Instance of AutoShot
        keyframe_extractor (KeyFrameExtractor): Instance of KeyFrameExtractor

    Returns:
        Dict[str, Any]: A dictionary containing processing results.
    """
    result = {"video_path": video_path, "status": "success", "scenes": None, "keyframes": None}

    
    scenes = shot_detector.process_video(video_path=video_path)
    result["scenes"] = scenes

    if scenes:
        relative_path = os.path.relpath(video_path, os.path.dirname(video_path))
        keyframes = keyframe_extractor.save_keyframes(video_path, scenes, relative_path)
        result["keyframes"] = keyframes
    else:
        logging.warning(f"No scenes detected in video: {video_path}")


    return result



def get_video_paths(input_dir: str) -> Iterator[str]:

    video_extensions = ('*.mp4', '*.avi', '*.mov', '*.mkv')
    path = Path(input_dir)
    for ext in video_extensions:
        for video_path in path.rglob(ext):
            yield str(video_path)


def process_videos(input_dir: str, pretrained_model_path: str, keyframe_dir: str) -> Dict[str, Dict[str, Any]]:


    os.makedirs(keyframe_dir, exist_ok=True)
    
        
    shot_detector = AutoShot(pretrained_model_path)
    keyframe_extractor = KeyFrameExtractor(keyframe_dir)
    results = {}
    video_paths = get_video_paths(input_dir)

    logging.info(f"Starting to process videos")

    for video_path in tqdm(video_paths, desc="Overall Progress", unit="video"):
        relative_path = os.path.relpath(video_path, input_dir)
        logging.info(f"Processing: {relative_path}")

        result = process_single_video(video_path, shot_detector, keyframe_extractor)
        results[relative_path] = result

    return results


def save_results_to_file(results: dict, output_file: str) -> None:
    with open(output_file, 'w') as f:
        for video_file, result in results.items():
            f.write(f"{video_file}: {result}\n")
    





def main(args: argparse.ArgumentParser):

    model_path = args.model_path
    input_dirs = args.input_dirs
    keyframe_dirs = args.keyframe_dirs


    if len(input_dirs) != len(keyframe_dirs):
        raise ValueError("The number of input directories must match the number of keyframe directories.")


    for input_dir, keyframe_dir in zip(input_dirs, keyframe_dirs):
        os.makedirs(keyframe_dir, exist_ok=True)

        results = process_videos(input_dir, model_path, keyframe_dir)

        output_file = os.path.join(keyframe_dir, "results.txt")
        save_results_to_file(results, output_file)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process videos to extract keyframes.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the model file.")
    parser.add_argument("--input_dirs", type=str, nargs='+', required=True, help="List of directories containing input videos.")
    parser.add_argument("--keyframe_dirs", type=str, nargs='+', required=True, help="List of directories to save extracted keyframes.")

    args = parser.parse_args()

    main(args)
    




