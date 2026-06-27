import numpy as np
import pandas as pd
import os
import sys
from typing import Dict, Any, Tuple

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.db import load_model_artifact, save_model_artifact, get_featured_data

class TrafficPredictor:
    """
    ML prediction engine.
    Handles loading trained models, auto-training models if artifacts are missing,
    predicting traffic volume and congestion level, and calculating confidence intervals
    using tree prediction variances.
    """
    def __init__(self):
        self.volume_model_name = "traffic_volume_rf.joblib"
        self.feature_columns = [
            "junction_id", "hour", "day_of_week", "month", "temperature", 
            "is_holiday", "hour_sin", "hour_cos", "day_sin", "day_cos", 
            "month_sin", "month_cos", "weather_encoded"
        ]
        self.weather_mapping = {
            "Clear": 0,
            "Foggy": 1,
            "Rainy": 2,
            "Snowy": 3
        }
        self.model = None
        self.is_trained = False
        
    def _train_fallback_model(self):
        """
        Loads featured data and trains a RandomForestRegressor on the fly.
        Saves the trained model artifact to the models/ folder.
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            
            # Load feature-engineered data
            df = get_featured_data()
            
            # Prepare features and target
            X = df[self.feature_columns].copy()
            y = df["traffic_volume"]
            
            # Fit model
            print("No pre-trained ML model found. Training a Random Forest Regressor on the fly...")
            rf = RandomForestRegressor(n_estimators=50, max_depth=12, random_state=42, n_jobs=-1)
            rf.fit(X, y)
            
            # Save artifact
            save_model_artifact(rf, self.volume_model_name)
            self.model = rf
            self.is_trained = True
            print("Model trained and saved successfully.")
        except Exception as e:
            print(f"Failed to auto-train fallback model: {e}")
            self.model = None
            self.is_trained = False

    def load_model(self):
        """
        Loads the trained model. Trains it on-the-fly if not found.
        """
        self.model = load_model_artifact(self.volume_model_name)
        if self.model is not None:
            self.is_trained = True
        else:
            self._train_fallback_model()
        return self

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes prediction on input variables.
        Input format:
        {
            "junction_id": int,
            "hour": int,
            "day_of_week": int,
            "month": int,
            "temperature": float,
            "is_holiday": int,
            "weather_condition": str
        }
        """
        if not self.is_trained or self.model is None:
            self.load_model()
            
        if self.model is None:
            # Absolute fallback if sklearn is broken
            return self._rule_based_fallback(input_data)
            
        # 1. Transform inputs
        hour = input_data["hour"]
        day_of_week = input_data["day_of_week"]
        month = input_data["month"]
        weather = input_data["weather_condition"]
        
        weather_enc = self.weather_mapping.get(weather, 0)
        
        hour_sin = np.sin(2 * np.pi * hour / 24.0)
        hour_cos = np.cos(2 * np.pi * hour / 24.0)
        day_sin = np.sin(2 * np.pi * day_of_week / 7.0)
        day_cos = np.cos(2 * np.pi * day_of_week / 7.0)
        month_sin = np.sin(2 * np.pi * month / 12.0)
        month_cos = np.cos(2 * np.pi * month / 12.0)
        
        features_dict = {
            "junction_id": input_data["junction_id"],
            "hour": hour,
            "day_of_week": day_of_week,
            "month": month,
            "temperature": input_data["temperature"],
            "is_holiday": input_data["is_holiday"],
            "hour_sin": hour_sin,
            "hour_cos": hour_cos,
            "day_sin": day_sin,
            "day_cos": day_cos,
            "month_sin": month_sin,
            "month_cos": month_cos,
            "weather_encoded": weather_enc
        }
        
        # Create single-row DataFrame matching training schema order
        X_pred = pd.DataFrame([features_dict])[self.feature_columns]
        
        # 2. Compute prediction
        pred_volume = float(self.model.predict(X_pred)[0])
        pred_volume = max(0, int(round(pred_volume)))
        
        # 3. Compute prediction intervals using tree variance
        # Calculate predictions from all individual estimators (trees) in the random forest
        try:
            tree_preds = [tree.predict(X_pred)[0] for tree in self.model.estimators_]
            std_dev = np.std(tree_preds)
            
            # 95% Confidence Interval (z=1.96)
            lower_bound = max(0, int(round(pred_volume - 1.96 * std_dev)))
            upper_bound = int(round(pred_volume + 1.96 * std_dev))
            
            # Confidence score (inverse of standard deviation normalized by volume, scaled to 70-98%)
            cv = (std_dev / pred_volume) if pred_volume > 0 else 0.5
            confidence_score = max(50.0, min(99.0, 95.0 - (cv * 15.0)))
        except Exception:
            # Fallback if estimators_ not available
            lower_bound = max(0, int(pred_volume * 0.85))
            upper_bound = int(pred_volume * 1.15)
            confidence_score = 88.0
            
        # 4. Map volume & features to congestion level
        # Capacity maps matching dataset generation base values
        capacities = {1: 800, 2: 400, 3: 1200, 4: 600}
        capacity = capacities.get(input_data["junction_id"], 600)
        
        ratio = pred_volume / capacity
        if weather in ["Rainy", "Snowy"]:
            ratio *= 1.25 # weather multiplier
            
        if ratio < 0.45:
            congestion_level = "Low"
            congestion_color = "green"
        elif ratio < 0.75:
            congestion_level = "Medium"
            congestion_color = "warning"
        else:
            congestion_level = "High"
            congestion_color = "danger"
            
        return {
            "predicted_volume": pred_volume,
            "congestion_level": congestion_level,
            "congestion_color": congestion_color,
            "confidence_score": round(confidence_score, 1),
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "feature_importance": self.get_feature_importances()
        }

    def get_feature_importances(self) -> Dict[str, float]:
        """
        Returns feature importance weights from the trained model.
        """
        if not self.is_trained or self.model is None:
            self.load_model()
            
        if self.model is None or not hasattr(self.model, "feature_importances_"):
            # Dummy feature importances if model is uninitialized
            importances = [0.35, 0.25, 0.10, 0.05, 0.08, 0.02, 0.04, 0.04, 0.02, 0.02, 0.01, 0.01, 0.01]
        else:
            importances = list(self.model.feature_importances_)
            
        importance_dict = dict(zip(self.feature_columns, importances))
        # Sort by importance value descending
        return dict(sorted(importance_dict.items(), key=lambda item: item[1], reverse=True))

    def _rule_based_fallback(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Backup inference logic if ML environment fails entirely.
        """
        hour = input_data["hour"]
        junction = input_data["junction_id"]
        weather = input_data["weather_condition"]
        
        # Rule based approximation
        base = {1: 300, 2: 120, 3: 500, 4: 200}.get(junction, 200)
        mult = 0.2
        if 7 <= hour <= 9 or 16 <= hour <= 18:
            mult = 1.6
        elif 10 <= hour <= 15:
            mult = 0.8
            
        if weather == "Rainy":
            mult *= 0.9
        elif weather == "Snowy":
            mult *= 0.75
            
        pred_volume = int(base * mult)
        
        return {
            "predicted_volume": pred_volume,
            "congestion_level": "Medium" if mult >= 0.8 else "Low",
            "congestion_color": "warning" if mult >= 0.8 else "green",
            "confidence_score": 75.0,
            "lower_bound": int(pred_volume * 0.8),
            "upper_bound": int(pred_volume * 1.2),
            "feature_importance": {
                "hour": 0.50,
                "junction_id": 0.30,
                "weather_encoded": 0.10,
                "temperature": 0.05,
                "is_holiday": 0.05
            }
        }
