import pandas as pd
from typing import Dict, List, Any, Tuple

def detect_outliers_zscore(df: pd.DataFrame, col: str, threshold: float = 3.0) -> pd.DataFrame:
    """
    TODO: Filter rows containing outliers in the specified column based on Z-score.
    
    Args:
        df (pd.DataFrame): Dataset.
        col (str): Target column.
        threshold (float): Z-score threshold.
    Returns:
        pd.DataFrame: Outlier rows.
    """
    raise NotImplementedError("detect_outliers_zscore() is not implemented yet.")

def detect_outliers_iqr(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    TODO: Filter rows containing outliers in the specified column based on Interquartile Range (IQR).
    
    Args:
        df (pd.DataFrame): Dataset.
        col (str): Target column.
    Returns:
        pd.DataFrame: Outlier rows.
    """
    raise NotImplementedError("detect_outliers_iqr() is not implemented yet.")

def outlier_summary(df: pd.DataFrame, num_cols: List[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    TODO: Compute counts, percentages, and z-score boundaries of outliers.
    """
    raise NotImplementedError("outlier_summary() is not implemented yet.")
