import pandas as pd

class FeatureExtractor:
    """
    TODO: Implement feature engineering.
    
    Learning Objectives:
    - Extract basic temporal fields (hour, day of week, month, weekend indicators).
    - Implement Cyclical Time Encodings (sine/cosine representations of hour, day, month).
    - Map and encode categorical text values (weather conditions).
    - Compute junction-grouped lag features (e.g. traffic volume 1h ago).
    - Compute rolling statistical metrics (e.g. 3h/24h rolling averages).
    """
    def __init__(self):
        pass
        
    def fit(self, df: pd.DataFrame):
        """
        TODO: Learn feature parameters (e.g. categorical mappings).
        
        Args:
            df (pd.DataFrame): Cleaned training data.
        Returns:
            self
        """
        raise NotImplementedError(
            "FeatureExtractor.fit() is not implemented yet. "
            "Please write the fitting logic in src/feature_engineering/features.py."
        )

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        TODO: Apply feature engineering to the dataset.
        
        Requirements:
        1. Extract hour, day_of_week, month, is_weekend.
        2. Encode cyclical hours, days, and months using np.sin and np.cos.
        3. Shift/lag columns grouped by junction_id (volume_lag_1, volume_lag_24, speed_lag_1).
        4. Compute rolling means grouped by junction_id (volume_roll_mean_3, volume_roll_mean_24).
        5. Return the featured DataFrame.
        
        Args:
            df (pd.DataFrame): Cleaned input data.
        Returns:
            pd.DataFrame: Feature engineered DataFrame.
        """
        raise NotImplementedError(
            "FeatureExtractor.transform() is not implemented yet. "
            "Please write the transformation logic in src/feature_engineering/features.py."
        )
        
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fits and transforms in a single step.
        """
        return self.fit(df).transform(df)
