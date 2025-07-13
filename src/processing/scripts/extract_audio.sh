#!/bin/bash

PYTHON_EXE=python
INPUT_DIR="/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos"
OUTPUT_DIR="/media/tinhanhnguyen/Data1/Projects/HCMAI/data/audio_file"
SCRIPT_PATH="/media/tinhanhnguyen/Data1/Projects/HCMAI/src/audio_extraction/audio_extraction.py"
SAMPLE_RATE=16000

echo "Running audio extraction..."
"$PYTHON_EXE" "$SCRIPT_PATH" \
    --input_dir "$INPUT_DIR" \
    --output_dir "$OUTPUT_DIR" \
    --sample_rate "$SAMPLE_RATE"

echo "Audio extraction complete."
