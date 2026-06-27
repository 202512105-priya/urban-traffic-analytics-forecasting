import pandas as pd
from typing import Dict, Any, List

class TrafficValidator:
    """
    TODO: Implement the data validation engine.
    
    Learning Objectives:
    - Validate schemas against expected datatypes.
    - Compute missing value and sentinel percentages.
    - Detect duplicates.
    - Identify statistical outliers (e.g. using Z-score > 3.0 or IQR).
    - Compute a composite Data Quality Health Score.
    """
    def __init__(self, target_schema: Dict[str, str] = None):
        self.target_schema = target_schema or {
            "timestamp": "datetime",
            "junction_id": "integer",
            "traffic_volume": "integer",
            "average_speed": "float",
            "weather_condition": "string",
            "temperature": "float",
            "is_holiday": "integer",
            "congestion_index": "float"
        }
        
    def validate_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        TODO: Validate columns and datatypes.
        
        Returns a dict with:
        - "is_schema_ok": bool
        - "missing_columns": list of missing columns
        - "type_discrepancies": dict of mismatched columns and types
        """
        raise NotImplementedError(
            "TrafficValidator.validate_schema() is not implemented yet. "
            "Please write the schema check in src/validation/validator.py."
        )
        
    def check_missing_values(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        TODO: Count null values and sentinel strings (e.g. 'none', 'unknown') per column.
        
        Returns a dict mapping column names to:
        - "null_count": int
        - "sentinel_count": int
        - "total_missing": int
        - "percentage": float (0-100)
        """
        raise NotImplementedError(
            "TrafficValidator.check_missing_values() is not implemented yet. "
            "Please write the missing values check in src/validation/validator.py."
        )

    def check_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        TODO: Count duplicate rows.
        
        Returns a dict with:
        - "duplicate_count": int
        - "percentage": float
        """
        raise NotImplementedError(
            "TrafficValidator.check_duplicates() is not implemented yet. "
            "Please write the duplicates check in src/validation/validator.py."
        )

    def check_outliers(self, df: pd.DataFrame, num_cols: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        TODO: Detect statistical outliers in numerical columns using Z-score or IQR.
        
        Returns a dict mapping column names to:
        - "outlier_count": int
        - "percentage": float
        - "bounds": Tuple[float, float] (lower_bound, upper_bound)
        """
        raise NotImplementedError(
            "TrafficValidator.check_outliers() is not implemented yet. "
            "Please write the outlier check in src/validation/validator.py."
        )

    def get_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        TODO: Run all checks and compute a final Data Quality Score (0 to 100).
        
        Deduct points from 100 for:
        - Mismatched or missing schema columns.
        - High missing percentages.
        - High duplication rates.
        - Presence of statistical outliers.
        - Uncoerced data corruptions.
        
        Returns a comprehensive report dictionary.
        """
        raise NotImplementedError(
            "TrafficValidator.get_quality_report() is not implemented yet. "
            "Please implement the full validation report in src/validation/validator.py."
        )
