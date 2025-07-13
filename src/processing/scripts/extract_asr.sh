#!/bin/bash
set -e  #

# Input 
VIE_CHUNK_ASR_PATH="/media/tinhanhnguyen/Data1/Projects/HCMAI/local/chunkformer-large-vie"
AUDIO_FOLDER="/media/tinhanhnguyen/Data1/Projects/HCMAI/data/subset_data/audio_file"
VIDEO_FOLDER="/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos"
 
DESTINATION_FOLDER="/media/tinhanhnguyen/Data1/Projects/HCMAI/data/subset_data/audio_text"
RUN_FILE="/media/tinhanhnguyen/Data1/Projects/HCMAI/src/processing/audio_extraction/chunkformer/decode_batch.py"

# Run the decoding
python "$RUN_FILE" \
    --model_checkpoint "$VIE_CHUNK_ASR_PATH" \
    --main_folder "$AUDIO_FOLDER" \
    --destination_folder "$DESTINATION_FOLDER" \
    --video_folder "$VIDEO_FOLDER"\
    --total_batch_duration 14400 \
    --chunk_size 64 \
    --left_context_size 128 \
    --right_context_size 128
