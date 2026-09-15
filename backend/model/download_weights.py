#!/usr/bin/env python3
"""
AgriSmart AI - Automated Model Weights Downloader
Downloads the pre-trained DenseNet-201 checkpoint (~295MB) from Google Drive
if the local file is missing or only a Git LFS text pointer (<1MB).
Ref: SIH 2026 Problem Statement 1, Section 4.1 & 7.1.
"""

import os
import sys
import time
import urllib.request
import urllib.parse

# Google Drive File ID for crop_disease_resnet18_best.pth
GDRIVE_FILE_ID = "1BjFAs0QN0dmci23IrROr6hQIVDpFn20u"
EXPECTED_MIN_BYTES = 100_000_000  # At least 100 MB


def get_weights_path() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "crop_disease_resnet18_best.pth")


def is_weights_valid(path: str) -> bool:
    return os.path.isfile(path) and os.path.getsize(path) >= EXPECTED_MIN_BYTES


def download_from_gdrive(file_id: str, destination: str) -> bool:
    """
    Downloads large files from Google Drive handling the virus scan confirmation token.
    Uses standard library urllib (zero external dependencies).
    """
    print(f"\n{'='*60}")
    print(f"  AgriSmart AI - Downloading Trained Model Checkpoint")
    print(f"{'='*60}")
    print(f"  Target: {destination}")
    print(f"  Source: Google Drive (ID: {file_id})")
    print(f"  Estimated Size: ~295 MB")
    print(f"{'='*60}\n")

    os.makedirs(os.path.dirname(destination), exist_ok=True)
    temp_destination = destination + ".tmp"

    base_url = "https://drive.usercontent.google.com/download"
    params = {"id": file_id, "export": "download", "confirm": "t"}
    download_url = f"{base_url}?{urllib.parse.urlencode(params)}"

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    ]

    try:
        req = urllib.request.Request(download_url)
        with opener.open(req) as response:
            total_length = response.headers.get('content-length')
            if total_length:
                total_length = int(total_length)

            downloaded = 0
            block_size = 1024 * 1024  # 1 MB blocks
            start_time = time.time()

            with open(temp_destination, "wb") as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    f.write(buffer)

                    # Progress report
                    if total_length:
                        percent = downloaded * 100 / total_length
                        elapsed = time.time() - start_time
                        speed = (downloaded / 1024 / 1024) / (elapsed + 1e-5)
                        sys.stdout.write(f"\r  [↓] Progress: {downloaded / 1024 / 1024:.1f} MB / {total_length / 1024 / 1024:.1f} MB ({percent:.1f}%) | Speed: {speed:.1f} MB/s")
                    else:
                        sys.stdout.write(f"\r  [↓] Downloaded: {downloaded / 1024 / 1024:.1f} MB")
                    sys.stdout.flush()

        print("\n")

        # Check if downloaded file is HTML (e.g. permission or quota error)
        if os.path.getsize(temp_destination) < 100_000:
            with open(temp_destination, "r", encoding="utf-8", errors="ignore") as f:
                snippet = f.read(500)
            if "<html" in snippet.lower() or "google" in snippet.lower():
                print("  [ERROR] Downloaded content appears to be an HTML page instead of binary weights.")
                print("  Please verify Google Drive link sharing permissions (must be 'Anyone with the link').")
                if os.path.exists(temp_destination):
                    os.remove(temp_destination)
                return False

        # Rename temp to destination
        if os.path.exists(destination):
            os.remove(destination)
        os.rename(temp_destination, destination)

        print(f"  [✓] Model weights successfully downloaded and verified ({os.path.getsize(destination) / 1024 / 1024:.1f} MB)!")
        return True

    except Exception as e:
        print(f"\n  [ERROR] Failed to download model weights: {e}")
        if os.path.exists(temp_destination):
            try:
                os.remove(temp_destination)
            except OSError:
                pass
        return False


def ensure_weights(destination: str = None) -> str:
    """Ensures model weights exist. Returns path to valid weights or raises RuntimeError."""
    dest = destination or get_weights_path()
    if is_weights_valid(dest):
        return dest

    print(f"[INFO] Full model weights not found at '{dest}' (size is < 100MB).")
    print("[INFO] Attempting automatic download from Google Drive...")
    success = download_from_gdrive(GDRIVE_FILE_ID, dest)
    if success and is_weights_valid(dest):
        return dest

    raise RuntimeError(
        f"Model weights file could not be downloaded automatically.\n"
        f"Please download 'crop_disease_resnet18_best.pth' manually from:\n"
        f"  https://drive.google.com/file/d/{GDRIVE_FILE_ID}/view?usp=sharing\n"
        f"and save it into: {dest}"
    )


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else get_weights_path()
    if is_weights_valid(target):
        print(f"[✓] Model weights already valid at: {target} ({os.path.getsize(target)/1024/1024:.1f} MB)")
        sys.exit(0)
    ensure_weights(target)
