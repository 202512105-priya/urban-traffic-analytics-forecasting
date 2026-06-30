import os
import sys
import pandas as pd
import streamlit as st

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, FEATURES_DATA_DIR, MODEL_DIR

@st.cache_data(show_spinner="Loading raw traffic telemetry data...")
def get_raw_data() -> pd.DataFrame:
    """
    Loads raw traffic data. If not present, raises NotImplementedError
    to trigger the dashboard's developer warning banner.
    """
    from src.core.loader import load_csv
    raw_path = os.path.join(RAW_DATA_DIR, "traffic_raw.csv")
    if not os.path.exists(raw_path):
        # We raise NotImplementedError to indicate the ingestion/loader pipeline needs setup
        raise NotImplementedError(
            "Raw dataset not found. Please implement generate_sample_data() in "
            "src/utils/data_generator.py to generate it, or implement load_csv() in src/core/loader.py."
        )
    return load_csv(raw_path)

@st.cache_data(show_spinner="Running data cleaning and imputation pipelines...")
def get_clean_data() -> pd.DataFrame:
    """
    Cleans raw data by executing the modular cleaning pipeline.
    """
    from src.cleaning.pipeline import run_cleaning_pipeline
    
    clean_path = os.path.join(PROCESSED_DATA_DIR, "traffic_clean.csv")
    if os.path.exists(clean_path):
        return pd.read_csv(clean_path, parse_dates=["timestamp"])
    
    df_raw = get_raw_data()
    df_clean = run_cleaning_pipeline(df_raw)
    
    # Save processed data
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    df_clean.to_csv(clean_path, index=False)
    return df_clean

@st.cache_data(show_spinner="Executing temporal and cyclical feature engineering...")
def get_featured_data() -> pd.DataFrame:
    """
    Performs feature engineering on cleaned data using the modular features pipeline.
    """
    from src.feature_engineering.pipeline import compile_model_features
    
    features_path = os.path.join(FEATURES_DATA_DIR, "traffic_features.csv")
    if os.path.exists(features_path):
        return pd.read_csv(features_path, parse_dates=["timestamp"])
        
    df_clean = get_clean_data()
    df_featured = compile_model_features(df_clean)
    
    # Save feature-engineered data
    os.makedirs(FEATURES_DATA_DIR, exist_ok=True)
    df_featured.to_csv(features_path, index=False)
    return df_featured

def save_model_artifact(model, filename: str) -> str:
    """
    Saves serialized ML models using utility logic.
    """
    import joblib
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, filename)
    joblib.dump(model, model_path)
    return model_path

def load_model_artifact(filename: str):
    """
    Loads serialized ML models. Returns None if not trained yet.
    """
    import joblib
    model_path = os.path.join(MODEL_DIR, filename)
    if os.path.exists(model_path):
        try:
            return joblib.load(model_path)
        except Exception:
            return None
    return None
