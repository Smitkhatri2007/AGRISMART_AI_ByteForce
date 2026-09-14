import torch
import torch.nn as nn
import timm


NUM_CLASSES = 38


def create_model(num_classes=NUM_CLASSES, pretrained=True):
    """
    Create an EfficientNet-B2 classifier.

    The ImageNet-pretrained backbone provides useful visual
    features, while the final classifier is replaced for our
    38 PlantVillage disease classes.
    """

    model = timm.create_model(
        "efficientnet_b2",
        pretrained=pretrained,
        num_classes=num_classes,
    )

    return model


def get_device():
    """Use the NVIDIA GPU when CUDA is available."""

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")