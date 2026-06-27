import pandas as pd
import numpy as np

class FeatureExtractor:
    """
    Feature engineering pipeline.
    Creates cyclical temporal features (sine/cosine of hour, day, month),
    lag features, rolling statistics, and numerical encodings for models.
    """
    def __init__(self):
        self.weather_mapping = {
            "Clear": 0,
            "Foggy": 1,
            "Rainy": 2,
            "Snowy": 3
        }
        
    def fit(self, df: pd.DataFrame):
        """
        Learns parameters for feature extraction (if any, like scaling/categorical boundaries).
        """
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms cleaned dataframe to engineer features.
        """
        featured_df = df.copy()
        
        # Ensure timestamp is parsed
        if not pd.api.types.is_datetime64_any_dtype(featured_df["timestamp"]):
            featured_df["timestamp"] = pd.to_datetime(featured_df["timestamp"])
            
        # 1. Base Temporal Features
        featured_df["hour"] = featured_df["timestamp"].dt.hour
        featured_df["day_of_week"] = featured_df["timestamp"].dt.weekday
        featured_df["month"] = featured_df["timestamp"].dt.month
        featured_df["is_weekend"] = (featured_df["day_of_week"] >= 5).astype(int)
        
        # 2. Cyclical Time Encodings (captures 23:00 -> 00:00 wrapping)
        featured_df["hour_sin"] = np.sin(2 * np.pi * featured_df["hour"] / 24.0)
        featured_df["hour_cos"] = np.cos(2 * np.pi * featured_df["hour"] / 24.0)
        
        featured_df["day_sin"] = np.sin(2 * np.pi * featured_df["day_of_week"] / 7.0)
        featured_df["day_cos"] = np.cos(2 * np.pi * featured_df["day_of_week"] / 7.0)
        
        featured_df["month_sin"] = np.sin(2 * np.pi * featured_df["month"] / 12.0)
        featured_df["month_cos"] = np.cos(2 * np.pi * featured_df["month"] / 12.0)
        
        # 3. Categorical Encodings (Weather)
        featured_df["weather_encoded"] = featured_df["weather_condition"].map(self.weather_mapping).fillna(0).astype(int)
        
        # 4. Lag and Rolling features
        # Note: Since we have multiple junctions, lag features must be calculated per junction.
        # Sort by junction and timestamp first to ensure shifts are aligned
        featured_df = featured_df.sort_values(by=["junction_id", "timestamp"]).reset_index(drop=True)
        
        # Shift functions grouped by junction
        # Lag volume (1h and 24h prior)
        featured_df["volume_lag_1"] = featured_df.groupby("junction_id")["traffic_volume"].shift(1)
        featured_df["volume_lag_24"] = featured_df.groupby("junction_id")["traffic_volume"].shift(24)
        
        # Lag speed
        featured_df["speed_lag_1"] = featured_df.groupby("junction_id")["average_speed"].shift(1)
        
        # Rolling averages (3h and 24h moving window)
        featured_df["volume_roll_mean_3"] = featured_df.groupby("junction_id")["traffic_volume"].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )
        featured_df["volume_roll_mean_24"] = featured_df.groupby("junction_id")["traffic_volume"].transform(
            lambda x: x.rolling(window=24, min_periods=1).mean()
        )
        
        # Fill lags that resulted in NaNs at the beginning of each junction time series
        featured_df["volume_lag_1"] = featured_df["volume_lag_1"].fillna(featured_df["traffic_volume"])
        featured_df["volume_lag_24"] = featured_df["volume_lag_24"].fillna(featured_df["traffic_volume"])
        featured_df["speed_lag_1"] = featured_df["speed_lag_1"].fillna(featured_df["average_speed"])
        
        # Convert floats resulting from NaNs back to int
        featured_df["volume_lag_1"] = featured_df["volume_lag_1"].astype(int)
        featured_df["volume_lag_24"] = featured_df["volume_lag_24"].astype(int)
        
        # Final sort by timestamp
        featured_df = featured_df.sort_values(by="timestamp").reset_index(drop=True)
        
        return featured_df
        
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit and transform helper.
        """
        return self.fit(df).transform(df)
