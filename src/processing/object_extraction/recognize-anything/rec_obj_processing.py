from ram.models import ram_plus, RAM_plus
import torch
from PIL import Image
import numpy as np
from torchvision.transforms import Normalize, Compose, Resize, ToTensor, Lambda
from pathlib import Path
from tqdm import tqdm
import glob
import argparse
import json
from colorama import Fore, Style, init


DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def convert_to_rgb(image):
    return image.convert("RGB")

def img_proc(image_paths: list[str], image_size: int = 384) -> torch.Tensor:
    transform = Compose([
        Lambda(convert_to_rgb),
        Resize((image_size, image_size)),
        ToTensor(),
        Normalize(mean=[0.485, 0.456, 0.406],
                  std=[0.229, 0.224, 0.225])
    ])
    tensors = []
    for path in image_paths:
        img = Image.open(path)
        tensors.append(transform(img))
    return torch.stack(tensors).to(DEVICE)


def processing(
    input_folder: str,
    output_folder: str,
    batch_size: int,
    model: RAM_plus,
    threshold: float = 0.9
):
    source_base = Path(input_folder)
    destination_base = Path(output_folder)

    image_files = sorted(
        glob.glob(str(source_base / "**/*.webp"), recursive=True),
        key=lambda x: Path(x).stem
    )

    print(Fore.CYAN + f"[INFO] Found {len(image_files)} image(s) to process.")
    model.eval()
    model = model.to(DEVICE)
    for index in tqdm(range(0, len(image_files), batch_size), desc="Processing batches"):
        image_paths_input = image_files[index: index + batch_size]

        tensors = img_proc(image_paths_input)

        with torch.no_grad():
            tags = model.generate_tag_openset(tensors, threshold=threshold)

        for image_path, tag in zip(image_paths_input, tags):
            relative_path = Path(image_path).relative_to(source_base)
            output_path = (destination_base / relative_path).with_suffix('.json')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(tag, f, indent=4, ensure_ascii=False)

            print(Fore.GREEN + f"[SAVED] {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Batch image tagging using RAM+")
    
    parser.add_argument(
        "--model_checkpoint", type=str, required=True,
        help="Path to the model checkpoint .pt file"
    )
    parser.add_argument(
        "--main_folder", type=str, required=True,
        help="Root folder containing image files (recursively)"
    )
    parser.add_argument(
        "--destination_folder", type=str, required=True,
        help="Root folder where .json output files will be written"
    )
    parser.add_argument(
        "--batch_size", type=int, default=1,
        help="Batch size for tagging"
    )
    parser.add_argument(
        '--threshold', type=float, default=0.9,
        help="Confidence threshold for tags"
    )

    args = parser.parse_args()

    print(Fore.YELLOW + "[LOADING MODEL]")
    model = ram_plus(
        pretrained=args.model_checkpoint,
        image_size=384,
        vit='swin_l',
        threshold=args.threshold
    )
    print(Fore.YELLOW + "[MODEL LOADED]")

    processing(
        input_folder=args.main_folder,
        output_folder=args.destination_folder,
        batch_size=args.batch_size,
        model=model,
    )

    print(Fore.CYAN + Style.BRIGHT + "\n[✔] Tagging complete!")

if __name__ == "__main__":
    main()
