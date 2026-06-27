import pandas as pd
import numpy as np

class TrafficCleaner:
    """
    Production data cleaning pipeline.
    Handles data type casting, duplicate records removal, 
    value coercion (handling corrupted strings in numerical fields),
    and advanced group-based missing value imputation.
    """
    def __init__(self):
        # We can store imputation maps if we want to run this out-of-sample,
        # but for the dashboard it will compute them on the fly.
        self.median_volume_map = {}
        self.median_speed_map = {}
        self.mean_temp_map = {}
        self.weather_mode = "Clear"
        
    def fit(self, df: pd.DataFrame):
        """
        Learns imputation statistics from the training set.
        """
        # Create a temporary copy to parse timestamps and compute stats safely
        temp_df = df.copy()
        
        # Parse timestamp safely
        if "timestamp" in temp_df.columns:
            temp_df["timestamp"] = pd.to_datetime(temp_df["timestamp"], errors="coerce")
            temp_df["hour"] = temp_df["timestamp"].dt.hour
            temp_df["month"] = temp_df["timestamp"].dt.month
        else:
            temp_df["hour"] = 0
            temp_df["month"] = 1
            
        # Coerce numeric values for training calculations
        for col in ["traffic_volume", "average_speed"]:
            if col in temp_df.columns:
                temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
                
        if "temperature" in temp_df.columns:
            temp_df["temperature"] = pd.to_numeric(temp_df["temperature"], errors="coerce")
            
        # 1. Compute median volume grouped by junction and hour
        if "traffic_volume" in temp_df.columns and "junction_id" in temp_df.columns:
            self.median_volume_map = temp_df.groupby(["junction_id", "hour"])["traffic_volume"].median().to_dict()
            
        # 2. Compute median speed grouped by junction and hour
        if "average_speed" in temp_df.columns and "junction_id" in temp_df.columns:
            self.median_speed_map = temp_df.groupby(["junction_id", "hour"])["average_speed"].median().to_dict()
            
        # 3. Compute mean temperature grouped by month and hour
        if "temperature" in temp_df.columns:
            self.mean_temp_map = temp_df.groupby(["month", "hour"])["temperature"].mean().to_dict()
            
        # 4. Mode of weather
        if "weather_condition" in temp_df.columns:
            modes = temp_df["weather_condition"].mode()
            if not modes.empty:
                self.weather_mode = modes.iloc[0]
                
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies cleaning operations to a dataframe.
        """
        cleaned_df = df.copy()
        
        # 1. Remove duplicate records
        cleaned_df = cleaned_df.drop_duplicates().reset_index(drop=True)
        
        # 2. Enforce proper Datetime typing
        if "timestamp" in cleaned_df.columns:
            cleaned_df["timestamp"] = pd.to_datetime(cleaned_df["timestamp"], errors="coerce")
            # Create temp tracking columns for imputation lookup
            cleaned_df["_hour"] = cleaned_df["timestamp"].dt.hour
            cleaned_df["_month"] = cleaned_df["timestamp"].dt.month
        else:
            cleaned_df["_hour"] = 0
            cleaned_df["_month"] = 1
            
        # 3. Convert junction_id to integer
        if "junction_id" in cleaned_df.columns:
            cleaned_df["junction_id"] = pd.to_numeric(cleaned_df["junction_id"], errors="coerce").fillna(-1).astype(int)
            
        # 4. Handle Temperature type coercion and imputation
        if "temperature" in cleaned_df.columns:
            cleaned_df["temperature"] = pd.to_numeric(cleaned_df["temperature"], errors="coerce")
            
            # Impute temperature based on month & hour mapping
            def impute_temp(row):
                if pd.isna(row["temperature"]):
                    key = (row["_month"], row["_hour"])
                    return self.mean_temp_map.get(key, 15.0) # 15C default
                return row["temperature"]
            
            cleaned_df["temperature"] = cleaned_df.apply(impute_temp, axis=1)
            
        # 5. Impute Traffic Volume (group-based median)
        if "traffic_volume" in cleaned_df.columns:
            cleaned_df["traffic_volume"] = pd.to_numeric(cleaned_df["traffic_volume"], errors="coerce")
            
            def impute_vol(row):
                if pd.isna(row["traffic_volume"]):
                    key = (row["junction_id"], row["_hour"])
                    # Fallback to general median of junction, or global median 200
                    return self.median_volume_map.get(key, 200)
                return row["traffic_volume"]
                
            cleaned_df["traffic_volume"] = cleaned_df.apply(impute_vol, axis=1).astype(int)
            
        # 6. Impute Average Speed (group-based median)
        if "average_speed" in cleaned_df.columns:
            cleaned_df["average_speed"] = pd.to_numeric(cleaned_df["average_speed"], errors="coerce")
            
            def impute_speed(row):
                if pd.isna(row["average_speed"]):
                    key = (row["junction_id"], row["_hour"])
                    return self.median_speed_map.get(key, 45.0) # 45 km/h default
                return row["average_speed"]
                
            cleaned_df["average_speed"] = cleaned_df.apply(impute_speed, axis=1)
            
        # 7. Impute Weather Condition
        if "weather_condition" in cleaned_df.columns:
            cleaned_df["weather_condition"] = cleaned_df["weather_condition"].fillna(self.weather_mode)
            cleaned_df["weather_condition"] = cleaned_df["weather_condition"].astype(str)
            
        # 8. Clean up holiday and congestion
        if "is_holiday" in cleaned_df.columns:
            cleaned_df["is_holiday"] = pd.to_numeric(cleaned_df["is_holiday"], errors="coerce").fillna(0).astype(int)
            
        if "congestion_index" in cleaned_df.columns:
            cleaned_df["congestion_index"] = pd.to_numeric(cleaned_df["congestion_index"], errors="coerce")
            # Recalculate if null
            cleaned_df["congestion_index"] = cleaned_df["congestion_index"].fillna(0.0)
            
        # Remove helper columns
        cleaned_df = cleaned_df.drop(columns=["_hour", "_month"], errors="ignore")
        
        return cleaned_df
        
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit to data and transform in one step.
        """
        return self.fit(df).transform(df)
