#!/usr/bin/env python3
"""
AgriSmart AI - Mandatory Submission Prediction Interface (Root Entrypoint)
Ref: SIH 2026 Problem Statement 1, Page 3 (Section 4.1) & Page 5 (Section 7.1).

Usage:
  1. CLI:
     python predict.py --image path/to/leaf.jpg
     (Outputs strictly the predicted class label string)

  2. Python API:
     from predict import predict
     label = predict("path/to/leaf.jpg")
"""

import os
import sys

# Ensure backend and backend/model are in python search path
_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.join(_ROOT_DIR, "backend")
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from backend.predict import predict, main

if __name__ == "__main__":
    main()
