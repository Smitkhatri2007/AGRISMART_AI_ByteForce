import json
import sys
from pathlib import Path

import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

from model import create_model, get_device
# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "model" / "best_model.pth"
CLASSES_PATH = BASE_DIR / "model" / "classes.json"
DISEASE_INFO_PATH = BASE_DIR / "data" / "disease_info.json"

CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"

DEVICE = get_device()


# ============================================================
# Load disease model
# ============================================================

print("Loading AgriSmart AI...")

with open(CLASSES_PATH, "r", encoding="utf-8") as f:
    classes = json.load(f)

with open(DISEASE_INFO_PATH, "r", encoding="utf-8") as f:
    disease_database = json.load(f)["classes"]


# classes.json contains label -> index
idx_to_class = {
    int(index): label
    for label, index in classes.items()
}


disease_model = create_model(
    num_classes=len(idx_to_class),
    pretrained=False
)

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

disease_model.load_state_dict(
    checkpoint["model_state"]
)

disease_model = disease_model.to(DEVICE)
disease_model.eval()


# ============================================================
# Load CLIP plant gate
# ============================================================

print("Loading plant image validator...")

clip_model = CLIPModel.from_pretrained(
    CLIP_MODEL_NAME
).to(DEVICE)

clip_processor = CLIPProcessor.from_pretrained(
    CLIP_MODEL_NAME
)

clip_model.eval()


# ============================================================
# CLIP validation
# ============================================================

PLANT_PROMPTS = [
    "a photo of a plant leaf",
    "a photo of a crop plant",
]

NON_PLANT_PROMPTS = [
    "a photo of a car",
    "a photo of a person",
    "a photo of an animal",
    "a photo of a building",
    "a photo of an object",
]


def is_plant_image(image):
    """
    Validate whether an image appears to contain
    a plant or crop leaf.

    Returns:
        is_plant: bool
        plant_score: float
        non_plant_score: float
    """

    labels = PLANT_PROMPTS + NON_PLANT_PROMPTS

    inputs = clip_processor(
        text=labels,
        images=image,
        return_tensors="pt",
        padding=True
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = clip_model(**inputs)

        probabilities = (
            outputs.logits_per_image
            .softmax(dim=1)[0]
        )

    plant_score = (
        probabilities[0].item()
        + probabilities[1].item()
    )

    non_plant_score = (
        probabilities[2:].sum().item()
    )

    is_plant = plant_score > non_plant_score

    return (
        is_plant,
        plant_score,
        non_plant_score
    )


# ============================================================
# Disease prediction
# ============================================================

def predict_disease(image):
    """
    Run EfficientNet-B2 disease classifier.

    Returns:
        predicted_class
        confidence_percent
    """

    from torchvision import transforms

    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    image_tensor = preprocess(image)

    image_tensor = image_tensor.unsqueeze(0)

    image_tensor = image_tensor.to(DEVICE)

    with torch.no_grad():

        outputs = disease_model(image_tensor)

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        confidence, predicted = torch.max(
            probabilities,
            dim=1
        )

    predicted_class = idx_to_class[
        predicted.item()
    ]

    confidence_percent = (
        confidence.item() * 100
    )

    return predicted_class, confidence_percent


# ============================================================
# Main prediction function
# ============================================================

def predict(image_path, verbose=True):

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = Image.open(image_path).convert("RGB")

    # --------------------------------------------------------
    # Plant validation
    # --------------------------------------------------------

    is_plant, plant_score, non_plant_score = (
        is_plant_image(image)
    )

    if verbose:

        print("\n" + "=" * 60)
        print("AGRISMART AI - IMAGE VALIDATION")
        print("=" * 60)

        print(
            f"Plant score     : "
            f"{plant_score * 100:.2f}%"
        )

        print(
            f"Non-plant score : "
            f"{non_plant_score * 100:.2f}%"
        )

        print("=" * 60)

    # --------------------------------------------------------
    # Reject non-plant image
    # --------------------------------------------------------

    if not is_plant:

        if verbose:

            print(
                "Result          : "
                "NOT A PLANT / LEAF"
            )

            print()
            print(
                "Please upload a clear photo "
                "of a crop or leaf."
            )

            print("=" * 60)

        return {
            "valid_plant": False,
            "prediction": None,
            "confidence": 0.0,
            "plant_score": plant_score,
            "non_plant_score": non_plant_score,
            "disease_info": None
        }

    # --------------------------------------------------------
    # Disease prediction
    # --------------------------------------------------------

    predicted_class, confidence = predict_disease(
        image
    )

    info = disease_database.get(
        predicted_class
    )

    if verbose:

        print(
            "Result          : PLANT / LEAF"
        )

        print("\n" + "=" * 60)
        print("DISEASE PREDICTION")
        print("=" * 60)

        print(
            f"Prediction      : "
            f"{predicted_class}"
        )

        print(
            f"Confidence      : "
            f"{confidence:.2f}%"
        )

        if info:

            print("\n" + "=" * 60)
            print("DISEASE INFORMATION")
            print("=" * 60)

            print(
                f"Crop            : "
                f"{info['crop']}"
            )

            print(
                f"Disease         : "
                f"{info['disease']}"
            )

            print(
                f"Cause           : "
                f"{info['cause']}"
            )

            print(
                f"Severity        : "
                f"{info['severity']}"
            )

            print("\nSymptoms:")
            print(
                f"  {info['symptoms']}"
            )

            print("\nManagement / Treatment:")
            print(
                f"  {info['management']}"
            )

            print("\nPrevention:")
            print(
                f"  {info['prevention']}"
            )

            print("=" * 60)

    return {
        "valid_plant": True,
        "prediction": predicted_class,
        "confidence": confidence,
        "plant_score": plant_score,
        "non_plant_score": non_plant_score,
        "disease_info": info
    }


# ============================================================
# User feedback
# ============================================================


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            'Usage: python src\\predict.py '
            '"path\\to\\image.jpg"'
        )

        sys.exit(1)

    result = predict(
        sys.argv[1],
        verbose=True
    )

    print("\nPrediction result:")
    print(result)