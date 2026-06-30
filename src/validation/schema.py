import pandas as pd
from typing import List, Dict

def numerical_columns(df: pd.DataFrame) -> List[str]:
    """TODO: Return list of numerical column names."""
    raise NotImplementedError("numerical_columns() is not implemented yet.")

def categorical_columns(df: pd.DataFrame) -> List[str]:
    """TODO: Return list of categorical column names."""
    raise NotImplementedError("categorical_columns() is not implemented yet.")

def datetime_columns(df: pd.DataFrame) -> List[str]:
    """TODO: Return list of datetime column names."""
    raise NotImplementedError("datetime_columns() is not implemented yet.")

def schema_summary(df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
    """
    TODO: Audit datatypes against target types.
    
    Returns:
        Dict: mapping column to actual vs expected type audit statuses.
    """
    raise NotImplementedError("schema_summary() is not implemented yet.")
