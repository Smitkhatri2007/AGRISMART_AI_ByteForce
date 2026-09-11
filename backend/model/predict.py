#!/usr/bin/env python3
"""
AgriSmart AI - Mandatory Submission Prediction Interface
Model 1: Leaf Disease Classification (Computer Vision)
Gemini Pro: Disease Description & On-Demand Cureness Advisory
Ref: SIH 2026 Problem Statement 1, Page 3 (Section 4.1).
"""

import sys
import os
import argparse
import json

# Ensure current working directory / repo root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model.fake_engine import default_engine
from app.services.gemini_service import gemini_advisor


def predict(image_path: str) -> str:
    """
    Mandatory Submission Contract Function:
    Accepts a file path to an image and returns strictly the predicted class_label string.
    """
    return default_engine.predict(image_path)


def main():
    parser = argparse.ArgumentParser(
        description="AgriSmart AI - Crop Disease Prediction CLI (CV Detection + Gemini Pro Advisory)"
    )
    parser.add_argument(
        "--image",
        type=str,
        help="Path to the leaf/crop image file to classify."
    )
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Use Gemini Pro to describe the disease and prompt if the farmer wants a cure."
    )
    parser.add_argument(
        "--cure",
        action="store_true",
        help="Generate full Gemini Pro cure and recovery plan."
    )
    parser.add_argument(
        "--cure-for",
        type=str,
        help="Directly generate a Gemini Pro cure plan for a known disease (e.g. 'Tomato Early Blight')."
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="Growing",
        help="Crop growth stage (e.g. Vegetative, Flowering, Fruiting)."
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Output complete JSON metadata."
    )

    args = parser.parse_args()

    try:
        # Scenario A: Direct cure request
        if args.cure_for:
            plan = gemini_advisor.generate_cure_plan(args.cure_for, crop="Crop", growth_stage=args.stage)
            print(json.dumps(plan, indent=2))
            sys.exit(0)

        # Scenario B: Image prediction
        if not args.image:
            parser.error("Either --image <path> or --cure-for <disease_name> is required.")

        # Mandatory Section 4.1 check: If called simply with --image, print ONLY the class string!
        if not (args.describe or args.cure or args.detailed):
            predicted_class = predict(args.image)
            print(predicted_class)
            sys.exit(0)

        # Detailed analysis flow
        detection = default_engine.predict_detailed(args.image)
        predicted_class = detection["predicted_class"]
        crop = detection["crop"]
        is_healthy = detection["is_healthy"]

        description_info = gemini_advisor.describe_disease(
            disease_name=predicted_class,
            crop=crop,
            severity=detection["severity"],
            is_healthy=is_healthy
        )

        response = {
            "detection": detection,
            "disease_description": description_info
        }

        # If user explicitly wants cure
        if args.cure:
            cure_plan = gemini_advisor.generate_cure_plan(
                disease_name=predicted_class,
                crop=crop,
                growth_stage=args.stage
            )
            response["cure_plan"] = cure_plan

        print(json.dumps(response, indent=2))
        sys.exit(0)

    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
