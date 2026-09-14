#!/usr/bin/env python3
"""
AgriSmart AI - Checkpoint Diagnostic Tool
Inspects the saved .pth file to reveal:
  - Backbone architecture used during training
  - Image size used during training
  - Number of classes
  - Exact class ordering (critical for correct predictions)
  - EMA vs raw weights availability
  - Validation accuracy at checkpoint
"""

import os
import sys
import json

# Add backend root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def inspect_checkpoint(path: str):
    try:
        import torch
    except ImportError:
        print("ERROR: PyTorch is not installed. Run: pip install torch")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  AgriSmart AI — Checkpoint Inspector")
    print(f"{'='*60}")
    print(f"  File : {path}")
    print(f"  Size : {os.path.getsize(path) / 1_000_000:.1f} MB")
    print(f"{'='*60}\n")

    ckpt = torch.load(path, map_location="cpu", weights_only=False)

    if not isinstance(ckpt, dict):
        print(f"WARNING: Checkpoint is not a dict — it is a {type(ckpt)}")
        print("This may be a raw state_dict saved with torch.save(model.state_dict(), ...)")
        keys = list(ckpt.keys()) if hasattr(ckpt, "keys") else []
        print(f"Top-level keys (first 10): {keys[:10]}")
        return

    print(f"[1] Top-level keys in checkpoint:")
    for k in ckpt.keys():
        val = ckpt[k]
        if isinstance(val, dict):
            print(f"    '{k}' -> dict with {len(val)} entries")
        elif isinstance(val, list):
            print(f"    '{k}' -> list with {len(val)} items")
        elif hasattr(val, 'shape'):
            print(f"    '{k}' -> tensor {tuple(val.shape)}")
        else:
            print(f"    '{k}' -> {repr(val)}")

    # ── Config block ──────────────────────────────────────────────────────────
    print(f"\n[2] Training Config (ckpt['config']):")
    cfg = ckpt.get("config", {})
    if cfg:
        for k, v in cfg.items():
            print(f"    {k}: {v}")
    else:
        print("    (no 'config' key found)")

    # ── Backbone detection from state dict keys ───────────────────────────────
    print(f"\n[3] Backbone Detection (from state dict layer names):")
    state = ckpt.get("ema_state") or ckpt.get("model_state") or ckpt.get("model_state_dict") or ckpt
    if isinstance(state, dict):
        sample_keys = list(state.keys())[:5]
        print(f"    First 5 weight keys:")
        for k in sample_keys:
            print(f"      {k}")

        if any("denseblock" in k or "features.denseblock" in k for k in state.keys()):
            print("    >>> DETECTED BACKBONE: DenseNet-201")
        elif any("features.0.0" in k for k in state.keys()):
            print("    >>> DETECTED BACKBONE: EfficientNet")
        elif any("layer1" in k or "conv1" in k for k in state.keys()):
            print("    >>> DETECTED BACKBONE: ResNet-18 or ResNet-50")
        else:
            print("    >>> DETECTED BACKBONE: Unknown (check keys above manually)")

    # ── Class names ───────────────────────────────────────────────────────────
    print(f"\n[4] Class Names (training-time ordering):")
    class_names = ckpt.get("class_names") or ckpt.get("classes")
    if class_names:
        print(f"    Total classes: {len(class_names)}")
        print(f"    First 10 classes:")
        for i, cls in enumerate(list(class_names)[:10]):
            print(f"      [{i}] {cls}")
        print(f"    Last 5 classes:")
        for i, cls in enumerate(list(class_names)[-5:]):
            print(f"      [{len(class_names) - 5 + i}] {cls}")
    else:
        print("    (no 'class_names' or 'classes' key found)")

    # ── class_to_idx (alternative source) ────────────────────────────────────
    print(f"\n[5] class_to_idx mapping:")
    c2i = ckpt.get("class_to_idx")
    if c2i:
        print(f"    Total classes: {len(c2i)}")
        # Sort by index to show ordered list
        sorted_classes = sorted(c2i.items(), key=lambda x: x[1])
        print(f"    First 5 (sorted by index):")
        for cls, idx in sorted_classes[:5]:
            print(f"      [{idx}] {cls}")
        print(f"    Last 5:")
        for cls, idx in sorted_classes[-5:]:
            print(f"      [{idx}] {cls}")
    else:
        print("    (no 'class_to_idx' key found)")

    # ── Accuracy & training info ──────────────────────────────────────────────
    print(f"\n[6] Training Stats:")
    print(f"    val_acc   : {ckpt.get('val_acc', 'N/A')}")
    print(f"    epoch     : {ckpt.get('epoch', 'N/A')}")
    print(f"    has EMA   : {'ema_state' in ckpt}")
    print(f"    has SWA   : {'swa_state' in ckpt}")

    # ── Image size summary ────────────────────────────────────────────────────
    img_size = cfg.get("img_size", "NOT FOUND in config")
    backbone = cfg.get("backbone", "NOT FOUND in config")
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Backbone  : {backbone}")
    print(f"  Image size: {img_size}")
    print(f"  Classes   : {len(class_names) if class_names else (len(c2i) if c2i else 'UNKNOWN')}")
    print(f"  EMA ready : {'ema_state' in ckpt}")
    print(f"{'='*60}\n")

    # ── Save full class list to file ──────────────────────────────────────────
    if class_names or c2i:
        out_path = os.path.join(os.path.dirname(path), "checkpoint_class_order.json")
        if class_names:
            ordered = list(class_names)
        else:
            ordered = [cls for cls, _ in sorted(c2i.items(), key=lambda x: x[1])]
        with open(out_path, "w") as f:
            json.dump({"backbone": backbone, "img_size": img_size, "class_order": ordered}, f, indent=2)
        print(f"  Full class ordering saved to: {out_path}")


if __name__ == "__main__":
    candidates = [
        "model/crop_disease_resnet18_best.pth",
        os.path.join(os.path.dirname(__file__), "model", "crop_disease_resnet18_best.pth"),
    ]
    path = None
    for c in candidates:
        if os.path.isfile(c) and os.path.getsize(c) > 1_000_000:
            path = os.path.abspath(c)
            break

    if not path:
        print("ERROR: Could not find 'crop_disease_resnet18_best.pth' (must be > 1MB).")
        sys.exit(1)

    inspect_checkpoint(path)
