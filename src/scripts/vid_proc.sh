#!/bin/bash

PYTHON_EXE=python
SCRIPT_PATH="/media/tinhanhnguyen/Data1/Projects/HCMAI/src/video_processing/main.py"
MODEL_PATH="/media/tinhanhnguyen/Data1/Projects/HCMAI/local/model_weights/transnetv2-pytorch-weights.pth"

INPUT_DIRS=(
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos/Videos_L03_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos/Videos_L04_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos/Videos_L05_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos/Videos_L06_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos/Videos_L07_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos/Videos_L08_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos/Videos_L09_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos/Videos_L10_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos/Videos_L11_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/videos/Videos_L12_a"

)

KEYFRAME_DIRS=(
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/keyframe/Videos_L03_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/keyframe/Videos_L04_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/keyframe/Videos_L05_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/keyframe/Videos_L06_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/keyframe/Videos_L07_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/keyframe/Videos_L08_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/keyframe/Videos_L09_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/keyframe/Videos_L10_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/keyframe/Videos_L11_a"
    "/media/tinhanhnguyen/Data1/Projects/HCMAI/data/keyframe/Videos_L12_a"
k
)

for i in "${!INPUT_DIRS[@]}"; do
    echo "Processing videos in ${INPUT_DIRS[$i]}"
    $PYTHON_EXE $SCRIPT_PATH --model_path $MODEL_PATH --input_dirs "${INPUT_DIRS[$i]}" --keyframe_dirs "${KEYFRAME_DIRS[$i]}"
done

echo "All video processing tasks completed."