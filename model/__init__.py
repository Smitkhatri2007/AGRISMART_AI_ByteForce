"""
AgriSmart AI - Model Module (Root Entrypoint)
Ref: SIH 2026 Problem Statement 1, Section 4.1 & 7.1.
"""

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND = os.path.join(_ROOT, "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from backend.predict import predict

__all__ = ["predict"]
