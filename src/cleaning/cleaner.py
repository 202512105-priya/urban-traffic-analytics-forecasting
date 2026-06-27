import pandas as pd

class TrafficCleaner:
    """
    TODO: Implement the data cleaning pipeline.
    
    Learning Objectives:
    - Handle duplicate records.
    - Standardize and cast datatypes (timestamps to datetime, categorical sensors to int/category).
    - Handle value coercions (handling non-numeric strings in numeric columns like temperature).
    - Implement group-based missing value imputation (e.g. median volume for a specific junction and hour).
    """
    def __init__(self):
        pass
        
    def fit(self, df: pd.DataFrame):
        """
        TODO: Learn cleaning parameters (e.g. modes, medians) from the dataset.
        
        Args:
            df (pd.DataFrame): Raw training data.
        Returns:
            self
        """
        raise NotImplementedError(
            "TrafficCleaner.fit() is not implemented yet. "
            "Please write the fitting logic in src/cleaning/cleaner.py."
        )

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        TODO: Apply cleaning transformations to the dataset.
        
        Requirements:
        1. Remove duplicate rows.
        2. Convert 'timestamp' to datetime and extract helper features if needed for imputation.
        3. Convert 'temperature' to numeric, replacing strings like 'ERR' with NaN, then impute.
        4. Impute missing traffic_volume, average_speed, and weather_condition using learned statistics.
        5. Return the clean DataFrame.
        
        Args:
            df (pd.DataFrame): Input DataFrame.
        Returns:
            pd.DataFrame: Cleaned DataFrame.
        """
        raise NotImplementedError(
            "TrafficCleaner.transform() is not implemented yet. "
            "Please write the transformation logic in src/cleaning/cleaner.py."
        )
        
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fits and transforms in a single step.
        """
        return self.fit(df).transform(df)
