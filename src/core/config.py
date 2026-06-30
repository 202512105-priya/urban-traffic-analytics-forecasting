import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
FEATURES_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "features")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
