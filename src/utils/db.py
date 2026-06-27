import os
import sys
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Directories
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
FEATURES_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "features")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")

def get_raw_data() -> pd.DataFrame:
    """
    TODO: Load raw traffic telemetry data.
    
    Requirements:
    1. Read the raw telemetry dataset from RAW_DATA_DIR/traffic_raw.csv.
    2. If the file does not exist, raise FileNotFoundError or call generate_sample_data() to create it.
    3. Return the dataset as a pandas DataFrame.
    
    Returns:
        pd.DataFrame: Raw dataset.
    """
    raise NotImplementedError(
        "get_raw_data() is not implemented yet. "
        "Please write the loading logic in src/utils/db.py."
    )

def get_clean_data() -> pd.DataFrame:
    """
    TODO: Impute missing values, drop duplicates, and type-coerce the raw dataset.
    
    Requirements:
    1. Check if the processed CSV exists in PROCESSED_DATA_DIR/traffic_clean.csv.
    2. If it does, load and return it.
    3. If it does not, load raw data using get_raw_data(), instantiate TrafficCleaner,
       fit and transform the data, save the result to PROCESSED_DATA_DIR, and return it.
       
    Returns:
        pd.DataFrame: Cleaned dataset.
    """
    raise NotImplementedError(
        "get_clean_data() is not implemented yet. "
        "Please write the pipeline trigger in src/utils/db.py."
    )

def get_featured_data() -> pd.DataFrame:
    """
    TODO: Run the feature engineering pipeline.
    
    Requirements:
    1. Check if FEATURES_DATA_DIR/traffic_features.csv exists. If so, return it.
    2. If not, load clean data using get_clean_data(), instantiate FeatureExtractor,
       fit and transform the dataset, save the output to FEATURES_DATA_DIR, and return it.
       
    Returns:
        pd.DataFrame: Feature engineered dataset.
    """
    raise NotImplementedError(
        "get_featured_data() is not implemented yet. "
        "Please write the pipeline trigger in src/utils/db.py."
    )

def save_model_artifact(model, filename: str) -> str:
    """
    TODO: Save a serialized ML model.
    
    Requirements:
    1. Create MODEL_DIR if it doesn't exist.
    2. Serialize and save the model object using joblib or pickle to MODEL_DIR/filename.
    
    Args:
        model: Trained model object.
        filename (str): Name of the file (e.g. model.joblib).
        
    Returns:
        str: Absolute path to the saved artifact.
    """
    raise NotImplementedError(
        "save_model_artifact() is not implemented yet. "
        "Please implement in src/utils/db.py."
    )

def load_model_artifact(filename: str):
    """
    TODO: Load a serialized ML model.
    
    Requirements:
    1. Check if MODEL_DIR/filename exists.
    2. If it exists, load the model weights using joblib or pickle and return it.
    3. If not, return None.
    
    Args:
        filename (str): Name of the file.
        
    Returns:
        Trained model or None.
    """
    raise NotImplementedError(
        "load_model_artifact() is not implemented yet. "
        "Please implement in src/utils/db.py."
    )
