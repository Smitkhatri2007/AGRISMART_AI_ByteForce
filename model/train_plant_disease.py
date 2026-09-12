import os
os.environ.setdefault("NCCL_P2P_DISABLE", "1")
os.environ.setdefault("NCCL_IB_DISABLE", "1")
os.environ.setdefault("NCCL_SHM_DISABLE", "1")
import io
import json
import math
import time
import random
import warnings
import argparse
from datetime import datetime
from contextlib import nullcontext

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.checkpoint import checkpoint_sequential
from torch.optim.swa_utils import AveragedModel, SWALR, update_bn

import torchvision
from torchvision import datasets, transforms, models

warnings.filterwarnings("ignore")

try:
    from sklearn.metrics import (
        precision_recall_fscore_support,
        confusion_matrix,
        classification_report,
        accuracy_score,
    )
except ImportError as e:
    raise ImportError(
        "scikit-learn is required for metrics (precision/recall/F1/confusion "
        "matrix). It ships by default in the Kaggle python environment."
    ) from e

try:
    # pyrefly: ignore [missing-import]
    import matplotlib
    matplotlib.use("Agg")
    # pyrefly: ignore [missing-import]
    import matplotlib.pyplot as plt
    _HAS_MPL = True
except ImportError:
    _HAS_MPL = False


# ==============================================================================
# 1. HYPERPARAMETER / CONFIGURATION BLOCK
# ==============================================================================

CONFIG = {
    # --- Backbone -------------------------------------------------------
    "backbone": "efficientnet_b4",       # "efficientnet_b4" | "densenet201" | "vit_b_16"
    "pretrained": True,
    "dropout": 0.3,
    "head_hidden_dim": 512,
    "grad_checkpointing": True,          # only applied for CNN backbones

    # --- Data -------------------------------------------------------------
    "img_size": None,                    # None -> auto-picked per backbone below
    "batch_size": 32,                    # PER-GPU batch size
    "num_workers": 4,                    # lowered from 8 to avoid Windows multiprocessing crashes
    "val_batch_size": 64,

    # --- Augmentation -------------------------------------------------------
    "random_resized_crop_scale": (0.7, 1.0),
    "random_perspective_distortion": 0.2,
    "random_perspective_p": 0.3,
    "color_jitter": (0.3, 0.3, 0.3, 0.0),   # brightness, contrast, saturation, hue
    "hflip_p": 0.5,
    "vflip_p": 0.5,
    "randaugment_n": 2,
    "randaugment_m": 9,
    "random_erasing_p": 0.4,
    "random_erasing_scale": (0.02, 0.25),
    "random_erasing_ratio": (0.3, 3.3),
    "imagenet_mean": [0.485, 0.456, 0.406],
    "imagenet_std": [0.229, 0.224, 0.225],

    # --- MixUp / CutMix -------------------------------------------------------
    "mixup_alpha": 0.2,
    "cutmix_alpha": 1.0,
    "mix_prob": 0.5,                    # probability a given batch is mixed at all

    # --- Optimization -------------------------------------------------------
    "epochs": 60,
    "grad_accum_steps": 2,               # effective batch = batch_size * accum * world_size
    "base_lr": 3e-4,
    "weight_decay": 1e-3,                # per spec: AdamW with weight_decay=1e-3
    "llrd_decay": 0.85,                  # layer-wise LR decay multiplier per group
    "grad_clip_norm": 5.0,
    "label_smoothing": 0.1,
    "use_class_weights": True,

    # --- Scheduler -------------------------------------------------------
    "scheduler_type": "warmup_cosine",   # "warmup_cosine" | "onecycle" | "cosine_restarts"
    "warmup_epochs": 5,
    "cosine_restart_t0": 10,
    "cosine_restart_tmult": 2,

    # --- EMA / SWA -------------------------------------------------------
    "use_ema": True,
    "ema_decay": 0.9995,
    "use_swa": True,
    "swa_start_frac": 0.75,              # fraction of total epochs at which SWA begins
    "swa_lr": 1e-5,

    # --- Early stopping / checkpointing -------------------------------------------------------
    "early_stop_patience": 10,
    "checkpoint_dir": "./checkpoints",
    "best_checkpoint_name": "crop_disease_resnet18_best.pth",  # name kept per spec
    "periodic_checkpoint_every": 5,
    "keep_top_k_for_ensemble": 3,

    # --- Validation / TTA -------------------------------------------------------
    "val_every_n_steps": None,           # None -> validate once per epoch only
    "use_tta": True,                     # hflip + vflip averaging at inference/final eval

    # --- Misc -------------------------------------------------------
    "seed": 42,
    "log_every_n_steps": 50,
    "report_path": "./training_report.txt",
    "curves_csv_path": "./training_curves.csv",
    "curves_png_path": "./training_curves.png",
}

_DEFAULT_IMG_SIZE = {
    "efficientnet_b4": 380,
    "densenet201": 224,
    "vit_b_16": 224,
}
if CONFIG["img_size"] is None:
    CONFIG["img_size"] = _DEFAULT_IMG_SIZE.get(CONFIG["backbone"], 224)


# ==============================================================================
# 2. DATASET PATH RESOLUTION (with fallback logic)
# ==============================================================================

def resolve_dataset_paths():
    """Try a series of known/likely dataset layouts and return the first that exists."""
    base_candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")),
        "./dataset",
        "./data",
        "/kaggle/input/datasets/vipoooool/new-plant-diseases-dataset",
        "/kaggle/input/new-plant-diseases-dataset",
        "/kaggle/input/new-plant-diseases-dataset-augmented",
    ]
    inner_candidates = [
        "New Plant Diseases Dataset(Augmented)/New Plant Diseases Dataset(Augmented)",
        "New Plant Diseases Dataset(Augmented)",
        "",  # some mirrors put train/valid directly under the base dir
    ]

    for base in base_candidates:
        for inner in inner_candidates:
            root = os.path.join(base, inner) if inner else base
            train_p = os.path.join(root, "train")
            valid_p = os.path.join(root, "valid")
            if os.path.isdir(train_p) and os.path.isdir(valid_p):
                return train_p, valid_p

    raise FileNotFoundError(
        "Could not locate the New Plant Diseases Dataset under any known path. "
        "Checked combinations of: " + json.dumps(base_candidates) +
        " x " + json.dumps(inner_candidates) +
        ". Please verify the dataset is attached to this Kaggle notebook/script."
    )


# ==============================================================================
# 3. REPRODUCIBILITY
# ==============================================================================

def set_seed(seed, rank=0):
    seed = seed + rank
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


# ==============================================================================
# 4. DISTRIBUTED SETUP HELPERS
# ==============================================================================

def setup_ddp(rank, world_size, port="29500"):
    os.environ.setdefault("MASTER_ADDR", "127.0.0.1")
    os.environ.setdefault("MASTER_PORT", port)
    dist.init_process_group(backend="nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)


def cleanup_ddp():
    if dist.is_initialized():
        dist.destroy_process_group()


def is_main_process(rank):
    return rank == 0


def reduce_tensor(tensor, world_size):
    """Sum-reduce a tensor across all processes and return the sum (caller divides as needed)."""
    if world_size > 1:
        rt = tensor.clone()
        dist.all_reduce(rt, op=dist.ReduceOp.SUM)
        return rt
    return tensor


def gather_object_lists(local_list, world_size):
    """Gather python lists (e.g. of predictions/labels) from all ranks onto every rank."""
    if world_size <= 1:
        return list(local_list)
    gathered = [None for _ in range(world_size)]
    dist.all_gather_object(gathered, local_list)
    merged = []
    for sub in gathered:
        merged.extend(sub)
    return merged


# ==============================================================================
# 5. DATA TRANSFORMS
# ==============================================================================

def build_transforms(cfg):
    img_size = cfg["img_size"]
    mean, std = cfg["imagenet_mean"], cfg["imagenet_std"]

    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(img_size, scale=cfg["random_resized_crop_scale"]),
        transforms.RandomHorizontalFlip(p=cfg["hflip_p"]),
        transforms.RandomVerticalFlip(p=cfg["vflip_p"]),
        transforms.RandomApply(
            [transforms.RandomPerspective(distortion_scale=cfg["random_perspective_distortion"], p=1.0)],
            p=cfg["random_perspective_p"],
        ),
        transforms.ColorJitter(
            brightness=cfg["color_jitter"][0],
            contrast=cfg["color_jitter"][1],
            saturation=cfg["color_jitter"][2],
            hue=cfg["color_jitter"][3],
        ),
        transforms.RandAugment(num_ops=cfg["randaugment_n"], magnitude=cfg["randaugment_m"]),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
        transforms.RandomErasing(
            p=cfg["random_erasing_p"],
            scale=cfg["random_erasing_scale"],
            ratio=cfg["random_erasing_ratio"],
        ),
    ])

    val_tf = transforms.Compose([
        transforms.Resize(int(img_size * 1.14)),
        transforms.CenterCrop(img_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

    return train_tf, val_tf


# ==============================================================================
# 6. MIXUP / CUTMIX
# ==============================================================================

def rand_bbox(width, height, lam):
    cut_rat = math.sqrt(1.0 - lam)
    cut_w, cut_h = int(width * cut_rat), int(height * cut_rat)
    cx, cy = np.random.randint(width), np.random.randint(height)
    x1 = np.clip(cx - cut_w // 2, 0, width)
    y1 = np.clip(cy - cut_h // 2, 0, height)
    x2 = np.clip(cx + cut_w // 2, 0, width)
    y2 = np.clip(cy + cut_h // 2, 0, height)
    return x1, y1, x2, y2


def apply_mixup_cutmix(x, y, cfg):
    """Returns (x, y_a, y_b, lam, was_mixed)."""
    if np.random.rand() > cfg["mix_prob"]:
        return x, y, y, 1.0, False

    batch_size = x.size(0)
    index = torch.randperm(batch_size, device=x.device)
    use_cutmix = np.random.rand() < 0.5 and cfg["cutmix_alpha"] > 0

    if use_cutmix:
        lam = float(np.random.beta(cfg["cutmix_alpha"], cfg["cutmix_alpha"]))
        _, _, H, W = x.shape
        x1, y1, x2, y2 = rand_bbox(W, H, lam)
        x[:, :, y1:y2, x1:x2] = x[index, :, y1:y2, x1:x2]
        lam = 1.0 - ((x2 - x1) * (y2 - y1) / (W * H))
    elif cfg["mixup_alpha"] > 0:
        lam = float(np.random.beta(cfg["mixup_alpha"], cfg["mixup_alpha"]))
        x = lam * x + (1.0 - lam) * x[index]
    else:
        return x, y, y, 1.0, False

    y_a, y_b = y, y[index]
    return x, y_a, y_b, lam, True


def mixed_criterion(criterion, outputs, y_a, y_b, lam):
    return lam * criterion(outputs, y_a) + (1.0 - lam) * criterion(outputs, y_b)


# ==============================================================================
# 7. MODEL DEFINITION
# ==============================================================================

class ClassifierHead(nn.Module):
    """Custom head: Linear -> BatchNorm -> ReLU -> Dropout -> Linear."""

    def __init__(self, in_features, num_classes, hidden_dim=512, dropout=0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x):
        return self.net(x)


class PlantDiseaseModel(nn.Module):
    """
    Wraps one of {efficientnet_b4, densenet201, vit_b_16} as a feature extractor,
    with the original classification heads stripped out and replaced by a
    custom ClassifierHead. Supports optional gradient checkpointing on the
    convolutional feature stack of the CNN backbones.
    """

    def __init__(self, backbone_name, num_classes, cfg):
        super().__init__()
        self.backbone_name = backbone_name
        self.grad_checkpointing = cfg["grad_checkpointing"]

        if backbone_name == "efficientnet_b4":
            weights = models.EfficientNet_B4_Weights.IMAGENET1K_V1 if cfg["pretrained"] else None
            backbone = models.efficientnet_b4(weights=weights)
            in_features = backbone.classifier[1].in_features
            backbone.classifier = nn.Identity()
            self.features = backbone.features
            self.pool = backbone.avgpool
            self.arch_type = "cnn"

        elif backbone_name == "densenet201":
            weights = models.DenseNet201_Weights.IMAGENET1K_V1 if cfg["pretrained"] else None
            backbone = models.densenet201(weights=weights)
            in_features = backbone.classifier.in_features
            backbone.classifier = nn.Identity()
            self.features = backbone.features
            self.pool = None  # densenet needs relu + adaptive pool manually
            self.arch_type = "densenet"

        elif backbone_name == "vit_b_16":
            weights = models.ViT_B_16_Weights.IMAGENET1K_V1 if cfg["pretrained"] else None
            backbone = models.vit_b_16(weights=weights)
            in_features = backbone.heads.head.in_features
            backbone.heads.head = nn.Identity()
            self.backbone = backbone
            self.arch_type = "vit"
        else:
            raise ValueError(f"Unsupported backbone: {backbone_name}")

        self.head = ClassifierHead(
            in_features, num_classes,
            hidden_dim=cfg["head_hidden_dim"], dropout=cfg["dropout"],
        )

    def forward_features(self, x):
        if self.arch_type == "cnn":
            if self.grad_checkpointing and self.training:
                feats = checkpoint_sequential(self.features, segments=4, input=x, use_reentrant=False)
            else:
                feats = self.features(x)
            feats = self.pool(feats)
            feats = torch.flatten(feats, 1)
        elif self.arch_type == "densenet":
            if self.grad_checkpointing and self.training:
                feats = checkpoint_sequential(self.features, segments=4, input=x, use_reentrant=False)
            else:
                feats = self.features(x)
            feats = F.relu(feats, inplace=True)
            feats = F.adaptive_avg_pool2d(feats, (1, 1))
            feats = torch.flatten(feats, 1)
        else:  # vit
            feats = self.backbone(x)
        return feats

    def forward(self, x):
        feats = self.forward_features(x)
        return self.head(feats)


def build_model(backbone_name, num_classes, cfg):
    return PlantDiseaseModel(backbone_name, num_classes, cfg)


# ==============================================================================
# 8. LAYER-WISE LEARNING RATE DECAY (LLRD)
# ==============================================================================

def build_llrd_param_groups(model, base_lr, decay, weight_decay):
    """
    Groups backbone parameters by depth (shallow -> deep) and applies an
    exponentially decayed learning rate to earlier layers, with the head
    always trained at the full base_lr.
    """
    no_decay_keywords = ("bias", "bn", "batchnorm", "norm")

    if hasattr(model, "features"):
        layer_groups = list(model.features.children())
    else:
        # ViT: fall back to encoder layers if present, else treat as one block
        try:
            layer_groups = list(model.backbone.encoder.layers.children())
        except AttributeError:
            layer_groups = [model.backbone] if hasattr(model, "backbone") else [model]

    n_groups = max(len(layer_groups), 1)
    param_groups = []

    for i, layer in enumerate(layer_groups):
        lr = base_lr * (decay ** (n_groups - 1 - i))
        decay_params, no_decay_params = [], []
        for name, p in layer.named_parameters():
            if not p.requires_grad:
                continue
            if any(k in name.lower() for k in no_decay_keywords):
                no_decay_params.append(p)
            else:
                decay_params.append(p)
        if decay_params:
            param_groups.append({"params": decay_params, "lr": lr, "weight_decay": weight_decay})
        if no_decay_params:
            param_groups.append({"params": no_decay_params, "lr": lr, "weight_decay": 0.0})

    # Head: full learning rate, standard weight decay
    head_decay, head_no_decay = [], []
    for name, p in model.head.named_parameters():
        if not p.requires_grad:
            continue
        if any(k in name.lower() for k in no_decay_keywords):
            head_no_decay.append(p)
        else:
            head_decay.append(p)
    if head_decay:
        param_groups.append({"params": head_decay, "lr": base_lr, "weight_decay": weight_decay})
    if head_no_decay:
        param_groups.append({"params": head_no_decay, "lr": base_lr, "weight_decay": 0.0})

    return param_groups


# ==============================================================================
# 9. EMA (EXPONENTIAL MOVING AVERAGE)
# ==============================================================================

class ModelEMA:
    def __init__(self, model, decay=0.9995):
        self.decay = decay
        self.shadow = {k: v.detach().clone().float() for k, v in model.state_dict().items()}

    @torch.no_grad()
    def update(self, model):
        msd = model.state_dict()
        for k, v in self.shadow.items():
            model_v = msd[k].detach().float()
            if v.dtype.is_floating_point:
                v.mul_(self.decay).add_(model_v, alpha=1.0 - self.decay)
            else:
                self.shadow[k] = model_v

    def apply_to(self, model):
        model.load_state_dict(self.shadow, strict=True)

    def state_dict(self):
        return self.shadow


# ==============================================================================
# 10. SCHEDULER FACTORY
# ==============================================================================

def build_scheduler(optimizer, cfg, steps_per_epoch):
    sched_type = cfg["scheduler_type"]
    total_epochs = cfg["epochs"]

    if sched_type == "onecycle":
        max_lrs = [g["lr"] for g in optimizer.param_groups]
        scheduler = torch.optim.lr_scheduler.OneCycleLR(
            optimizer, max_lr=max_lrs,
            steps_per_epoch=steps_per_epoch, epochs=total_epochs,
            pct_start=cfg["warmup_epochs"] / max(total_epochs, 1),
        )
        step_per_batch = True

    elif sched_type == "cosine_restarts":
        scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=cfg["cosine_restart_t0"], T_mult=cfg["cosine_restart_tmult"],
        )
        step_per_batch = False

    else:  # warmup_cosine (default)
        warmup_epochs = cfg["warmup_epochs"]

        def lr_lambda(epoch):
            if epoch < warmup_epochs:
                return float(epoch + 1) / float(max(1, warmup_epochs))
            progress = (epoch - warmup_epochs) / max(1, (total_epochs - warmup_epochs))
            return 0.5 * (1.0 + math.cos(math.pi * progress))

        scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=lr_lambda)
        step_per_batch = False

    return scheduler, step_per_batch


# ==============================================================================
# 11. TEST-TIME AUGMENTATION (TTA)
# ==============================================================================

@torch.no_grad()
def tta_forward(model, x, use_tta=True):
    """Averages softmax over identity, horizontal-flip, and vertical-flip views."""
    logits = model(x)
    probs = F.softmax(logits, dim=1)
    if not use_tta:
        return probs
    probs = probs + F.softmax(model(torch.flip(x, dims=[3])), dim=1)   # hflip
    probs = probs + F.softmax(model(torch.flip(x, dims=[2])), dim=1)   # vflip
    return probs / 3.0


# ==============================================================================
# 12. TRAIN / VALIDATION LOOPS
# ==============================================================================

def train_one_epoch(model, loader, sampler, optimizer, scheduler, step_per_batch,
                     criterion, scaler, ema, cfg, device, rank, world_size, epoch):
    model.train()
    if sampler is not None:
        sampler.set_epoch(epoch)

    running_loss = torch.zeros(1, device=device)
    running_correct = torch.zeros(1, device=device)
    running_total = torch.zeros(1, device=device)

    optimizer.zero_grad(set_to_none=True)
    t0 = time.time()

    for step, (images, labels) in enumerate(loader):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        images, y_a, y_b, lam, was_mixed = apply_mixup_cutmix(images, labels, cfg)

        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=torch.cuda.is_available()):
            outputs = model(images)
            if was_mixed:
                loss = mixed_criterion(criterion, outputs, y_a, y_b, lam)
            else:
                loss = criterion(outputs, y_a)
            loss = loss / cfg["grad_accum_steps"]

        scaler.scale(loss).backward()

        if (step + 1) % cfg["grad_accum_steps"] == 0:
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg["grad_clip_norm"])
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)
            if ema is not None:
                ema.update(model.module if isinstance(model, DDP) else model)
            if step_per_batch:
                scheduler.step()

        with torch.no_grad():
            preds = outputs.argmax(dim=1)
            running_correct += (preds == labels).sum()
            running_total += labels.size(0)
            running_loss += loss.detach() * cfg["grad_accum_steps"] * labels.size(0)

        if rank == 0 and (step + 1) % cfg["log_every_n_steps"] == 0:
            elapsed = time.time() - t0
            print(f"  [epoch {epoch+1}] step {step+1}/{len(loader)} "
                  f"loss={running_loss.item()/max(running_total.item(),1):.4f} "
                  f"acc={running_correct.item()/max(running_total.item(),1):.4f} "
                  f"elapsed={elapsed:.1f}s")

    # Sync metrics across GPUs
    stats = torch.cat([running_loss, running_correct, running_total])
    stats = reduce_tensor(stats, world_size)
    total_loss, total_correct, total_count = stats[0].item(), stats[1].item(), stats[2].item()

    return total_loss / max(total_count, 1), total_correct / max(total_count, 1)


@torch.no_grad()
def validate(model, loader, sampler, criterion, cfg, device, rank, world_size, use_tta=True):
    model.eval()
    running_loss = torch.zeros(1, device=device)
    running_total = torch.zeros(1, device=device)
    local_preds, local_labels = [], []

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=torch.cuda.is_available()):
            logits = model(images)
            loss = criterion(logits, labels)
            probs = tta_forward(model, images, use_tta=use_tta) if use_tta else F.softmax(logits, dim=1)

        preds = probs.argmax(dim=1)
        running_loss += loss.detach() * labels.size(0)
        running_total += labels.size(0)
        local_preds.extend(preds.cpu().tolist())
        local_labels.extend(labels.cpu().tolist())

    stats = torch.cat([running_loss, running_total])
    stats = reduce_tensor(stats, world_size)
    avg_loss = stats[0].item() / max(stats[1].item(), 1)

    all_preds = gather_object_lists(local_preds, world_size)
    all_labels = gather_object_lists(local_labels, world_size)

    acc = accuracy_score(all_labels, all_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        all_labels, all_preds, average="macro", zero_division=0
    )

    return {
        "loss": avg_loss,
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "all_preds": all_preds,
        "all_labels": all_labels,
    }


# ==============================================================================
# 13. CHECKPOINTING
# ==============================================================================

def save_checkpoint(state, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(state, path)


def manage_topk_checkpoints(ckpt_dir, epoch, val_acc, model_state, k=3):
    """Keeps the top-k checkpoints by validation accuracy for later ensembling."""
    manifest_path = os.path.join(ckpt_dir, "topk_manifest.json")
    manifest = []
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

    ckpt_name = f"ensemble_epoch{epoch+1}_acc{val_acc:.4f}.pth"
    ckpt_path = os.path.join(ckpt_dir, ckpt_name)
    torch.save(model_state, ckpt_path)
    manifest.append({"path": ckpt_path, "epoch": epoch + 1, "val_acc": val_acc})
    manifest.sort(key=lambda x: x["val_acc"], reverse=True)

    while len(manifest) > k:
        worst = manifest.pop()
        if os.path.exists(worst["path"]):
            os.remove(worst["path"])

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


# ==============================================================================
# 14. FINAL REPORT
# ==============================================================================

def write_final_report(cfg, class_names, best_epoch, best_val_metrics, history, report_path):
    lines = []
    lines.append("=" * 80)
    lines.append("PLANT DISEASE CLASSIFICATION — FINAL TRAINING REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append(f"Backbone: {cfg['backbone']}  |  Image size: {cfg['img_size']}")
    lines.append(f"Total epochs run: {len(history['val_acc'])} (configured: {cfg['epochs']})")
    lines.append(f"Best epoch: {best_epoch + 1}")
    lines.append("")
    lines.append(f"Best validation accuracy : {best_val_metrics['accuracy']:.4f}")
    lines.append(f"Best validation loss     : {best_val_metrics['loss']:.4f}")
    lines.append(f"Macro precision          : {best_val_metrics['precision']:.4f}")
    lines.append(f"Macro recall             : {best_val_metrics['recall']:.4f}")
    lines.append(f"Macro F1                 : {best_val_metrics['f1']:.4f}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("Per-class report (precision / recall / f1-score / support)")
    lines.append("-" * 80)
    report_str = classification_report(
        best_val_metrics["all_labels"], best_val_metrics["all_preds"],
        target_names=class_names, zero_division=0,
    )
    lines.append(report_str)
    lines.append("-" * 80)
    lines.append("Notes on omitted 'if applicable' techniques:")
    lines.append(" - Semi-supervised FixMatch: not applicable, dataset is fully labeled.")
    lines.append(" - Knowledge distillation: not applicable, single model trained "
                  "(EMA + SWA used instead for generalization).")
    lines.append("=" * 80)

    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    print("\n".join(lines))


def save_training_curves(history, csv_path, png_path):
    keys = list(history.keys())
    n = len(history[keys[0]])
    with open(csv_path, "w") as f:
        f.write(",".join(keys) + "\n")
        for i in range(n):
            f.write(",".join(str(history[k][i]) for k in keys) + "\n")

    if _HAS_MPL:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        axes[0].plot(history["train_loss"], label="train_loss")
        axes[0].plot(history["val_loss"], label="val_loss")
        axes[0].set_title("Loss")
        axes[0].set_xlabel("epoch")
        axes[0].legend()

        axes[1].plot(history["train_acc"], label="train_acc")
        axes[1].plot(history["val_acc"], label="val_acc")
        axes[1].set_title("Accuracy")
        axes[1].set_xlabel("epoch")
        axes[1].legend()

        fig.tight_layout()
        fig.savefig(png_path, dpi=150)
        plt.close(fig)


# ==============================================================================
# 15. MAIN TRAINING WORKER (one per GPU under DDP)
# ==============================================================================

def train_worker(rank, world_size, cfg):
    is_distributed = world_size > 1
    if is_distributed:
        setup_ddp(rank, world_size)

    set_seed(cfg["seed"], rank)
    device = torch.device(f"cuda:{rank}" if torch.cuda.is_available() else "cpu")
    torch.backends.cudnn.benchmark = True

    # ---------------- Data ----------------
    train_path, val_path = resolve_dataset_paths()
    train_tf, val_tf = build_transforms(cfg)

    train_dataset = datasets.ImageFolder(train_path, transform=train_tf)
    val_dataset = datasets.ImageFolder(val_path, transform=val_tf)
    class_names = train_dataset.classes
    num_classes = len(class_names)

    if rank == 0:
        print(f"Found {len(train_dataset)} training images, {len(val_dataset)} validation "
              f"images across {num_classes} classes.")

    train_sampler = DistributedSampler(train_dataset, num_replicas=world_size, rank=rank,
                                        shuffle=True, drop_last=True) if is_distributed else None
    val_sampler = DistributedSampler(val_dataset, num_replicas=world_size, rank=rank,
                                      shuffle=False, drop_last=False) if is_distributed else None

    train_loader = DataLoader(
        train_dataset, batch_size=cfg["batch_size"],
        shuffle=(train_sampler is None), sampler=train_sampler,
        num_workers=cfg["num_workers"], pin_memory=True, drop_last=True,
        persistent_workers=cfg["num_workers"] > 0,
    )
    val_loader = DataLoader(
        val_dataset, batch_size=cfg["val_batch_size"],
        shuffle=False, sampler=val_sampler,
        num_workers=cfg["num_workers"], pin_memory=True,
        persistent_workers=cfg["num_workers"] > 0,
    )

    # ---------------- Class weights ----------------
    class_weights_tensor = None
    if cfg["use_class_weights"]:
        targets = np.array(train_dataset.targets)
        counts = np.bincount(targets, minlength=num_classes).astype(np.float32)
        counts[counts == 0] = 1.0
        weights = counts.sum() / (num_classes * counts)
        class_weights_tensor = torch.tensor(weights, dtype=torch.float32, device=device)

    # ---------------- Model ----------------
    model = build_model(cfg["backbone"], num_classes, cfg).to(device)
    if is_distributed:
        model = DDP(model, device_ids=[rank], output_device=rank, find_unused_parameters=False)

    base_module = model.module if isinstance(model, DDP) else model
    param_groups = build_llrd_param_groups(
        base_module, cfg["base_lr"], cfg["llrd_decay"], cfg["weight_decay"]
    )
    optimizer = torch.optim.AdamW(param_groups, lr=cfg["base_lr"], weight_decay=cfg["weight_decay"])

    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor, label_smoothing=cfg["label_smoothing"])

    scheduler, step_per_batch = build_scheduler(optimizer, cfg, steps_per_epoch=len(train_loader))
    scaler = torch.cuda.amp.GradScaler(enabled=torch.cuda.is_available())

    ema = ModelEMA(base_module, decay=cfg["ema_decay"]) if cfg["use_ema"] else None

    swa_model = AveragedModel(base_module) if cfg["use_swa"] else None
    swa_scheduler = SWALR(optimizer, swa_lr=cfg["swa_lr"]) if cfg["use_swa"] else None
    swa_start_epoch = int(cfg["epochs"] * cfg["swa_start_frac"])

    # ---------------- Training loop ----------------
    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": [],
               "val_precision": [], "val_recall": [], "val_f1": [], "lr": []}

    best_val_acc = -1.0
    best_epoch = -1
    best_val_metrics = None
    patience_counter = 0

    os.makedirs(cfg["checkpoint_dir"], exist_ok=True)

    for epoch in range(cfg["epochs"]):
        epoch_t0 = time.time()

        train_loss, train_acc = train_one_epoch(
            model, train_loader, train_sampler, optimizer, scheduler, step_per_batch,
            criterion, scaler, ema, cfg, device, rank, world_size, epoch,
        )

        in_swa_phase = cfg["use_swa"] and epoch >= swa_start_epoch
        if in_swa_phase:
            swa_model.update_parameters(base_module)
            swa_scheduler.step()
        elif not step_per_batch:
            scheduler.step()

        # Validate with the EMA weights if enabled (typically generalizes better)
        eval_model = model
        restore_state = None
        if ema is not None:
            restore_state = {k: v.detach().clone() for k, v in base_module.state_dict().items()}
            ema.apply_to(base_module)

        val_metrics = validate(
            model, val_loader, val_sampler, criterion, cfg, device, rank, world_size,
            use_tta=cfg["use_tta"],
        )

        if ema is not None and restore_state is not None:
            base_module.load_state_dict(restore_state)

        current_lr = optimizer.param_groups[0]["lr"]

        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_metrics["loss"])
        history["val_acc"].append(val_metrics["accuracy"])
        history["val_precision"].append(val_metrics["precision"])
        history["val_recall"].append(val_metrics["recall"])
        history["val_f1"].append(val_metrics["f1"])
        history["lr"].append(current_lr)

        if rank == 0:
            epoch_time = time.time() - epoch_t0
            print(
                f"\nEpoch {epoch+1}/{cfg['epochs']} ({epoch_time:.1f}s) "
                f"[lr={current_lr:.2e}]"
                f"{' [SWA]' if in_swa_phase else ''}\n"
                f"  train: loss={train_loss:.4f} acc={train_acc:.4f}\n"
                f"  valid: loss={val_metrics['loss']:.4f} acc={val_metrics['accuracy']:.4f} "
                f"precision={val_metrics['precision']:.4f} recall={val_metrics['recall']:.4f} "
                f"f1={val_metrics['f1']:.4f}"
            )

            improved = val_metrics["accuracy"] > best_val_acc
            if improved:
                best_val_acc = val_metrics["accuracy"]
                best_epoch = epoch
                best_val_metrics = val_metrics
                patience_counter = 0
                save_checkpoint({
                    "epoch": epoch + 1,
                    "model_state": base_module.state_dict(),
                    "ema_state": ema.state_dict() if ema is not None else None,
                    "optimizer_state": optimizer.state_dict(),
                    "val_acc": val_metrics["accuracy"],
                    "class_names": class_names,
                    "config": cfg,
                }, os.path.join(cfg["checkpoint_dir"], cfg["best_checkpoint_name"]))
                manage_topk_checkpoints(
                    cfg["checkpoint_dir"], epoch, val_metrics["accuracy"],
                    base_module.state_dict(), k=cfg["keep_top_k_for_ensemble"],
                )
                print(f"  -> New best model saved (val_acc={best_val_acc:.4f})")
            else:
                patience_counter += 1

            save_checkpoint({
                "epoch": epoch + 1,
                "model_state": base_module.state_dict(),
                "optimizer_state": optimizer.state_dict(),
                "val_acc": val_metrics["accuracy"],
                "class_names": class_names,
                "config": cfg,
            }, os.path.join(cfg["checkpoint_dir"], "crop_disease_last.pth"))

            if (epoch + 1) % cfg["periodic_checkpoint_every"] == 0:
                save_checkpoint({
                    "epoch": epoch + 1,
                    "model_state": base_module.state_dict(),
                    "val_acc": val_metrics["accuracy"],
                    "class_names": class_names,
                }, os.path.join(cfg["checkpoint_dir"], f"crop_disease_epoch{epoch+1}.pth"))

        # Broadcast whether to early-stop so all ranks agree
        stop_flag = torch.tensor(
            [1.0 if (rank == 0 and patience_counter >= cfg["early_stop_patience"]) else 0.0],
            device=device,
        )
        if is_distributed:
            dist.broadcast(stop_flag, src=0)
        if stop_flag.item() > 0.5:
            if rank == 0:
                print(f"\nEarly stopping triggered at epoch {epoch+1} "
                      f"(no improvement for {cfg['early_stop_patience']} epochs).")
            break

    # ---------------- Finalize SWA batch norm stats ----------------
    if cfg["use_swa"] and swa_model is not None:
        if rank == 0:
            print("\nFinalizing SWA batch-norm statistics...")
        update_bn(train_loader, swa_model, device=device)
        if rank == 0:
            swa_val_metrics = validate(
                DDP(swa_model.module, device_ids=[rank]) if is_distributed else swa_model,
                val_loader, val_sampler, criterion, cfg, device, rank, world_size,
                use_tta=cfg["use_tta"],
            )
            print(f"SWA model validation accuracy: {swa_val_metrics['accuracy']:.4f}")
            if swa_val_metrics["accuracy"] > best_val_acc:
                print("SWA model outperforms best single-epoch checkpoint — saving as best.")
                save_checkpoint({
                    "epoch": "swa",
                    "model_state": swa_model.module.state_dict(),
                    "val_acc": swa_val_metrics["accuracy"],
                    "class_names": class_names,
                    "config": cfg,
                }, os.path.join(cfg["checkpoint_dir"], cfg["best_checkpoint_name"]))
                best_val_metrics = swa_val_metrics
                best_val_acc = swa_val_metrics["accuracy"]

    # ---------------- Final report (rank 0 only) ----------------
    if rank == 0 and best_val_metrics is not None:
        save_training_curves(history, cfg["curves_csv_path"], cfg["curves_png_path"])
        write_final_report(cfg, class_names, best_epoch, best_val_metrics, history, cfg["report_path"])
        print(f"\nTraining complete. Best validation accuracy: {best_val_acc:.4f}")
        print(f"Best checkpoint: {os.path.join(cfg['checkpoint_dir'], cfg['best_checkpoint_name'])}")
        print(f"Training curves: {cfg['curves_csv_path']} / {cfg['curves_png_path']}")
        print(f"Full report: {cfg['report_path']}")

    if is_distributed:
        cleanup_ddp()


# ==============================================================================
# 16. ENTRY POINT
# ==============================================================================

def parse_args():
    parser = argparse.ArgumentParser(description="Plant disease classification training")
    parser.add_argument("--backbone", type=str, default=CONFIG["backbone"],
                         choices=["efficientnet_b4", "densenet201", "vit_b_16"])
    parser.add_argument("--epochs", type=int, default=CONFIG["epochs"])
    parser.add_argument("--batch_size", type=int, default=CONFIG["batch_size"])
    parser.add_argument("--base_lr", type=float, default=CONFIG["base_lr"])
    parser.add_argument("--grad_accum_steps", type=int, default=CONFIG["grad_accum_steps"])
    parser.add_argument("--no_grad_checkpointing", action="store_true",
                         help="Disable gradient checkpointing. Safe to use with lighter "
                              "backbones/resolutions (e.g. densenet201 @ 224px) that have "
                              "memory headroom, for a meaningful speed gain.")
    parser.add_argument("--no_ddp", action="store_true",
                         help="Force single-process training even if 2 GPUs are visible.")
    # parse_known_args (not parse_args) so this survives being run inside a
    # notebook kernel (Colab/Jupyter inject their own "-f <kernel>.json" arg
    # that argparse would otherwise reject as unrecognized).
    args, _unknown = parser.parse_known_args()
    return args


def main():
    args = parse_args()
    CONFIG["backbone"] = args.backbone
    CONFIG["epochs"] = args.epochs
    CONFIG["batch_size"] = args.batch_size
    CONFIG["base_lr"] = args.base_lr
    CONFIG["grad_accum_steps"] = args.grad_accum_steps
    CONFIG["grad_checkpointing"] = not args.no_grad_checkpointing
    # Always re-derive img_size from the chosen backbone's default. There is no
    # separate --img_size flag, so this must run unconditionally on every launch
    # (comparing args.backbone against CONFIG["backbone"] here would be a no-op,
    # since the line above just made them equal).
    CONFIG["img_size"] = _DEFAULT_IMG_SIZE.get(args.backbone, CONFIG["img_size"])

    n_gpus = torch.cuda.device_count()
    print(f"Detected {n_gpus} CUDA device(s).")

    # Case 1: launched via `torchrun` / `torch.distributed.run`. torchrun starts
    # one real OS process per GPU itself (each with its own clean __main__), so
    # this path avoids the notebook mp.spawn pickling problem entirely and is
    # the recommended way to run this script for multi-GPU training.
    if "RANK" in os.environ and "WORLD_SIZE" in os.environ:
        rank = int(os.environ["RANK"])
        local_rank = int(os.environ.get("LOCAL_RANK", rank))
        world_size = int(os.environ["WORLD_SIZE"])
        print(f"Launched via torchrun: rank={rank} local_rank={local_rank} world_size={world_size}")
        train_worker(local_rank, world_size, CONFIG)
        return

    # Case 2: plain `python train_plant_disease.py` with 2+ GPUs -> mp.spawn
    # works here because this file is a real, importable module on disk.
    if n_gpus >= 2 and not args.no_ddp:
        print(f"Launching DistributedDataParallel training across {n_gpus} GPUs.")
        mp.spawn(train_worker, args=(n_gpus, CONFIG), nprocs=n_gpus, join=True)
    else:
        world_size = 1
        print("Running single-process training (single GPU or CPU).")
        train_worker(0, world_size, CONFIG)


if __name__ == "__main__":
    main()
