import os
import sys
import pandas as pd
import streamlit as st

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.data_generator import generate_sample_data

# Directories
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
FEATURES_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "features")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")

@st.cache_data(show_spinner="Loading raw traffic telemetry data...")
def get_raw_data() -> pd.DataFrame:
    """
    Loads raw traffic data. If not present, triggers the data generator.
    """
    raw_path = os.path.join(RAW_DATA_DIR, "traffic_raw.csv")
    if not os.path.exists(raw_path):
        # Generate the data automatically
        df = generate_sample_data(output_dir=RAW_DATA_DIR)
    else:
        # Load raw file (keeping temperature raw so validator can report corruption)
        df = pd.read_csv(raw_path)
    return df

@st.cache_data(show_spinner="Running data cleaning and imputation pipelines...")
def get_clean_data() -> pd.DataFrame:
    """
    Cleans raw data by executing the cleaner pipeline.
    """
    from src.cleaning.cleaner import TrafficCleaner
    
    clean_path = os.path.join(PROCESSED_DATA_DIR, "traffic_clean.csv")
    if os.path.exists(clean_path):
        df_clean = pd.read_csv(clean_path, parse_dates=["timestamp"])
    else:
        df_raw = get_raw_data()
        cleaner = TrafficCleaner()
        df_clean = cleaner.fit_transform(df_raw)
        
        # Save processed data
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        df_clean.to_csv(clean_path, index=False)
        
    return df_clean

@st.cache_data(show_spinner="Executing temporal and cyclical feature engineering...")
def get_featured_data() -> pd.DataFrame:
    """
    Performs feature engineering on cleaned data.
    """
    from src.feature_engineering.features import FeatureExtractor
    
    features_path = os.path.join(FEATURES_DATA_DIR, "traffic_features.csv")
    if os.path.exists(features_path):
        df_featured = pd.read_csv(features_path, parse_dates=["timestamp"])
    else:
        df_clean = get_clean_data()
        extractor = FeatureExtractor()
        df_featured = extractor.fit_transform(df_clean)
        
        # Save feature-engineered data
        os.makedirs(FEATURES_DATA_DIR, exist_ok=True)
        df_featured.to_csv(features_path, index=False)
        
    return df_featured

def save_model_artifact(model, filename: str):
    """
    Utility to save serialized ML models.
    """
    import joblib
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, filename)
    joblib.dump(model, model_path)
    return model_path

def load_model_artifact(filename: str):
    """
    Utility to load serialized ML models. Returns None if model is not trained yet.
    """
    import joblib
    model_path = os.path.join(MODEL_DIR, filename)
    if os.path.exists(model_path):
        try:
            return joblib.load(model_path)
        except Exception:
            return None
    return None
