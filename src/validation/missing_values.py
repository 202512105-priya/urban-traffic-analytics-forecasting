import pandas as pd
from typing import Dict, List, Any

def count_missing(df: pd.DataFrame) -> Dict[str, int]:
    """
    TODO: Count missing (null) values and sentinels per column.
    
    Args:
        df (pd.DataFrame): Dataset.
    Returns:
        Dict[str, int]: Column names to missing cell counts.
    """
    raise NotImplementedError("count_missing() is not implemented yet.")

def missing_percentage(df: pd.DataFrame) -> Dict[str, float]:
    """
    TODO: Calculate missing percentage (0.0 to 100.0) per column.
    
    Args:
        df (pd.DataFrame): Dataset.
    Returns:
        Dict[str, float]: Column names to missing percentages.
    """
    raise NotImplementedError("missing_percentage() is not implemented yet.")

def columns_with_missing(df: pd.DataFrame) -> List[str]:
    """
    TODO: Get columns containing any missing values.
    
    Args:
        df (pd.DataFrame): Dataset.
    Returns:
        List[str]: Column names.
    """
    raise NotImplementedError("columns_with_missing() is not implemented yet.")

def missing_summary(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    TODO: Compile missing counts and percentages into a nested dictionary.
    
    Returns:
        Dict[str, Dict[str, Any]]: e.g. {"col_name": {"count": 10, "pct": 2.5}}
    """
    raise NotImplementedError("missing_summary() is not implemented yet.")
