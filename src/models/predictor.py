import numpy as np
import pandas as pd
from typing import Dict, Any

class TrafficPredictor:
    """
    TODO: Implement the machine learning prediction pipeline.
    
    Learning Objectives:
    - Train regression/classification models (e.g. Scikit-learn, XGBoost) using pipeline features.
    - Save and load serialized model binaries (joblib/pickle).
    - Map custom telemetry inputs into inference feature vectors.
    - Compute prediction confidence bands (intervals) using tree variance or residual metrics.
    - Extract model feature importances for explainability (XAI).
    """
    def __init__(self):
        self.volume_model_name = "traffic_volume_rf.joblib"
        self.feature_columns = [
            "junction_id", "hour", "day_of_week", "month", "temperature", 
            "is_holiday", "hour_sin", "hour_cos", "day_sin", "day_cos", 
            "month_sin", "month_cos", "weather_encoded"
        ]
        self.is_trained = False
        
    def load_model(self):
        """
        TODO: Load the trained ML model weights from the models/ directory.
        If it does not exist, train a new model on the features and save it.
        """
        raise NotImplementedError(
            "TrafficPredictor.load_model() is not implemented yet. "
            "Please implement the model loading/training trigger in src/models/predictor.py."
        )

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        TODO: Perform real-time machine learning prediction using user inputs.
        
        Input dict:
        {
            "junction_id": int,
            "hour": int,
            "day_of_week": int,
            "month": int,
            "temperature": float,
            "is_holiday": int,
            "weather_condition": str
        }
        
        Requirements:
        1. Parse input_data into the exact 13-feature array required by the model (including cyclical sine/cosine calculations).
        2. Execute prediction on the loaded model.
        3. Determine congestion_level (Low/Medium/High) based on capacity thresholds.
        4. Calculate prediction confidence intervals and confidence scores.
        5. Return a dictionary containing:
           - "predicted_volume": int
           - "congestion_level": str
           - "congestion_color": str ("green", "warning", "danger")
           - "confidence_score": float (0-100)
           - "lower_bound": int
           - "upper_bound": int
           - "feature_importance": Dict[str, float]
        """
        raise NotImplementedError(
            "TrafficPredictor.predict() is not implemented yet. "
            "Please write the machine learning inference pipeline in src/models/predictor.py."
        )

    def get_feature_importances(self) -> Dict[str, float]:
        """
        TODO: Retrieve feature importances from the trained model.
        
        Returns:
            Dict: Key-value mapping of feature name to importance weight.
        """
        raise NotImplementedError(
            "TrafficPredictor.get_feature_importances() is not implemented yet. "
            "Please implement in src/models/predictor.py."
        )
