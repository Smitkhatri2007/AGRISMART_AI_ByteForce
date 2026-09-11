#!/usr/bin/env python3
"""
AgriSmart AI - Root CLI Entrypoint
Enables direct invocation from repository root:
    python predict.py --image path/to/leaf.jpg
Ref: SIH 2026 Problem Statement 1, Page 3 (Section 4.1).
"""
from model.predict import main, predict

__all__ = ["predict", "main"]

if __name__ == "__main__":
    main()
