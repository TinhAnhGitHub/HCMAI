# Base image with CUDA 12.1
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-venv python3.10-dev python3-pip \
    git wget curl build-essential libgl1-mesa-glx libglib2.0-0 \
    neovim \
    && rm -rf /var/lib/apt/lists/*

# Set Python alternatives
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Upgrade pip
RUN python -m pip install --upgrade pip

WORKDIR /workspace

RUN pip install openmim && \
    mim install mmengine==0.10.5 && \
    mim install mmcv==2.2.0

RUN pip install \
    torch==2.2.1+cu121 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121 \
    numpy==1.22.2 \
    transformers==4.37.2 \
    timm \
    deepspeed \
    pycocotools \
    lvis \
    jsonlines \
    fairscale \
    nltk \
    peft \
    wandb \
    terminaltables \
    shapely

CMD ["/bin/bash"]
