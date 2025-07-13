#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# -------- CONFIGURATION --------
MODEL_CHECKPOINT="/media/tinhanhnguyen/Data1/Projects/HCMAI/local/ram_plus_swin_large_14m.pth"
INPUT_FOLDER="/media/tinhanhnguyen/Data1/Projects/HCMAI/data/subset_data/keyframe"
OUTPUT_FOLDER="/media/tinhanhnguyen/Data1/Projects/HCMAI/data/subset_data/objects"
BATCH_SIZE=35
THRESHOLD=0.80
RUN_FILE="/media/tinhanhnguyen/Data1/Projects/HCMAI/src/processing/object_extraction/recognize-anything/rec_obj_processing.py"


# -------- RUN SCRIPT --------
python "$RUN_FILE" \
  --model_checkpoint "$MODEL_CHECKPOINT" \
  --main_folder "$INPUT_FOLDER" \
  --destination_folder "$OUTPUT_FOLDER" \
  --batch_size "$BATCH_SIZE" \
  --threshold "$THRESHOLD"
