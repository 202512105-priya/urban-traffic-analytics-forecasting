import pandas as pd

def impute_median_by_group(df: pd.DataFrame, col: str, group_cols: list) -> pd.Series:
    """
    TODO: Impute missing values with group-specific medians.
    """
    raise NotImplementedError("impute_median_by_group() is not implemented yet.")

def fill_missing_constants(df: pd.DataFrame, mappings: dict) -> pd.DataFrame:
    """
    TODO: Impute missing values with a dictionary of fallback constants.
    """
    raise NotImplementedError("fill_missing_constants() is not implemented yet.")
