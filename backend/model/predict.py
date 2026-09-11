#!/usr/bin/env python3
"""
AgriSmart AI - Mandatory Submission Prediction Interface with Dual Model Support
Model 1: Leaf Disease Classification
Model 2: Cureness & Treatment Recommendation
Ref: SIH 2026 Problem Statement 1, Page 3 (Section 4.1).
"""

import sys
import os
import argparse
import json

# Ensure current working directory / repo root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model.fake_engine import default_engine
from model.cure_model import cure_model


def predict(image_path: str) -> str:
    """
    Mandatory Submission Contract Function:
    Accepts a file path to an image and returns strictly the predicted class_label string.
    Delegates to Model 1 (Disease Detector).
    """
    return default_engine.predict(image_path)


def predict_cure(disease_class: str, crop: str = None, stage: str = "Growing") -> dict:
    """
    Direct Model 2 interface: Returns treatment, recovery probability, and timeline.
    """
    return cure_model.predict_cure(disease_class, crop=crop, growth_stage=stage)


def main():
    parser = argparse.ArgumentParser(
        description="AgriSmart AI - Dual AI Model CLI (Model 1: Disease Detection + Model 2: Cureness Plan)"
    )
    parser.add_argument(
        "--image",
        type=str,
        help="Path to the leaf/crop image file to classify with Model 1."
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="Growing",
        help="Crop growth stage (e.g. Germination, Growing, Flowering, Fruiting)."
    )
    parser.add_argument(
        "--cure",
        action="store_true",
        help="Run Model 2 (Cureness Prescriber) chained after Model 1 disease diagnosis."
    )
    parser.add_argument(
        "--cure-for",
        type=str,
        help="Directly run Model 2 for an already known disease class (e.g. 'Tomato Early Blight')."
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Output complete JSON metadata from both models."
    )

    args = parser.parse_args()

    try:
        # Scenario A: Direct Model 2 call
        if args.cure_for:
            cure_res = predict_cure(args.cure_for, stage=args.stage)
            print(json.dumps(cure_res, indent=2))
            sys.exit(0)

        # Scenario B: Image inference required
        if not args.image:
            parser.error("Either --image <path> or --cure-for <disease_name> is required.")

        if args.cure or args.detailed:
            result = default_engine.predict_detailed(args.image, growth_stage=args.stage)
            print(json.dumps(result, indent=2))
        else:
            # Mandatory Section 4.1 contract: strictly prints the predicted class string
            predicted_class = predict(args.image)
            print(predicted_class)

        sys.exit(0)
    except Exception as e:
        sys.stderr.write(f"Error during prediction: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
