from pathlib import Path
import torch

# ==========================
# PROJECT PATHS
# ==========================

ROOT = Path(__file__).resolve().parent

DATASET_DIR = ROOT / "dataset" / "food-101"

CHECKPOINT_DIR = ROOT / "checkpoints"

EXPORT_DIR = ROOT / "exports"

CHECKPOINT_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

# ==========================
# MODEL
# ==========================

MODEL_NAME = "efficientnet_b0"
NUM_CLASSES = 101

# ==========================
# TRAINING
# ==========================

IMAGE_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 20
LEARNING_RATE = 1e-4

# ==========================
# DEVICE
# ==========================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Running on: {DEVICE}")