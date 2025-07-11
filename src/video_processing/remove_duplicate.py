import numpy as np
import cv2
from collections import defaultdict
from typing import List, Tuple
from PIL import Image
import imagehash
import logging
from joblib import Parallel, delayed

class DDTNearDuplicateRemoval:
    def __init__(self, threshold: float = 0.80, hash_size: int = 8, verbose: bool = False, n_jobs: int = -1):
        """
        Initialize the DDTNearDuplicateRemoval class for detecting and removing near-duplicate images.

        Args:
            threshold (float, optional): Similarity threshold for considering images as near-duplicates. Default is 0.8.
            hash_size (int, optional): Size of the perceptual hash. Default is 8.
            verbose (bool, optional): Enable detailed logging. Default is False.
            n_jobs (int, optional): Number of jobs to run in parallel. Default is -1, which uses all available cores.
        """
        self.threshold = threshold
        self.hash_size = hash_size
        self.hash_function = imagehash.phash
        self.image_hashes: list = []
        self.n_jobs = n_jobs

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO if verbose else logging.WARNING)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.logger.info(f"Initialized DDTNearDuplicateRemoval with threshold: {threshold}, hash_size: {hash_size}, n_jobs: {n_jobs}")

    def preprocess_image(self, frame: np.ndarray) -> Image.Image:
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        self.logger.debug(f"Preprocessed image, shape: {frame.shape}")
        return pil_image

    def compute_hash_for_frame(self, idx: int, frame: np.ndarray) -> Tuple[int, imagehash.ImageHash]:
        pil_image = self.preprocess_image(frame)
        image_hash = self.hash_function(pil_image, hash_size=self.hash_size)
        return (idx, image_hash)

    def compute_hashes(self, *, keyframes: List[np.ndarray]) -> None:
        """Index the keyframes using perceptual hashing with parallel processing."""
        self.image_hashes = []
        self.logger.info(f"Computing hashes for {len(keyframes)} keyframes using {self.n_jobs} jobs")

        results = Parallel(n_jobs=self.n_jobs)(
            delayed(self.compute_hash_for_frame)(i, frame) for i, frame in enumerate(keyframes)
        )

        self.image_hashes = results
        self.logger.info(f"Finished computing {len(self.image_hashes)} hashes")

    def find_duplicates(self) -> List[List[int]]:
        """Find near-duplicate frames using perceptual hashing."""
        duplicates = defaultdict(list)
        self.logger.info(f"Finding duplicates among {len(self.image_hashes)} hashes")
        comparison_count = 0
        duplicate_count = 0
        for i in range(len(self.image_hashes)):
            for j in range(i + 1, len(self.image_hashes)):
                comparison_count += 1
                distance = self.image_hashes[i][1] - self.image_hashes[j][1]
                if distance <= self.hash_size * self.hash_size * (1 - self.threshold):
                    duplicates[self.image_hashes[i][0]].append(self.image_hashes[j][0])
                    duplicates[self.image_hashes[j][0]].append(self.image_hashes[i][0])
                    duplicate_count += 1
            if (i + 1) % 100 == 0:
                self.logger.info(f"Processed {i + 1} hashes, found {duplicate_count} duplicates so far")
        self.logger.info(f"Finished duplicate search. Compared {comparison_count} pairs, found {duplicate_count} duplicates")

        duplicate_groups = []
        processed = set()
        for idx, similar in duplicates.items():
            if idx not in processed:
                group = [idx] + similar
                duplicate_groups.append(sorted(set(group)))
                processed.update(group)

        self.logger.info(f"Found {len(duplicate_groups)} duplicate groups")
        return duplicate_groups

    def remove_near_duplicate(self, keyframes: List[np.ndarray]) -> List[int]:
        self.logger.info(f"Starting near-duplicate removal for {len(keyframes)} keyframes")
        self.compute_hashes(keyframes=keyframes)
        duplicate_groups = self.find_duplicates()
        unique_indices = set(range(len(keyframes)))
        removed_count = 0
        for group in duplicate_groups:
            unique_indices -= set(group[1:]) 
            removed_count += len(group) - 1

        unique_indices = sorted(unique_indices)
        self.logger.info(f"Finished near-duplicate removal. Kept {len(unique_indices)} unique keyframes, removed {removed_count} duplicates")
        return unique_indices
