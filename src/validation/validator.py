import pandas as pd
import numpy as np
from typing import Dict, Any, List

class TrafficValidator:
    """
    Data validation engine.
    Analyzes schema completeness, duplicates, missingness, type mismatches, and outliers.
    Produces structured validation reports and a total Data Quality Score.
    """
    def __init__(self, target_schema: Dict[str, str] = None):
        # Target schema definitions
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
        Validates column existence and records datatype discrepancies.
        """
        missing_cols = []
        type_discrepancies = {}
        
        for col, target_type in self.target_schema.items():
            if col not in df.columns:
                missing_cols.append(col)
                continue
                
            actual_type = str(df[col].dtype)
            
            # Simple check mapping
            is_valid = True
            if target_type == "datetime":
                # Check if it is datetime or can be parsed
                if not pd.api.types.is_datetime64_any_dtype(df[col]):
                    # Check if string representation is convertible
                    try:
                        pd.to_datetime(df[col].head(5), errors="raise")
                    except Exception:
                        is_valid = False
            elif target_type == "integer":
                # Check if integer type, or numeric and convertible to int without loss
                if not pd.api.types.is_integer_dtype(df[col]):
                    # Try to parse numeric
                    temp = pd.to_numeric(df[col], errors="coerce")
                    if temp.isna().sum() > df[col].isna().sum(): # Coercion introduced new NaNs
                        is_valid = False
            elif target_type == "float":
                if not pd.api.types.is_float_dtype(df[col]) and not pd.api.types.is_integer_dtype(df[col]):
                    temp = pd.to_numeric(df[col], errors="coerce")
                    if temp.isna().sum() > df[col].isna().sum():
                        is_valid = False
            elif target_type == "string":
                # Strings can be object
                if not pd.api.types.is_string_dtype(df[col]) and df[col].dtype != 'O':
                    is_valid = False
                    
            if not is_valid:
                type_discrepancies[col] = {
                    "expected": target_type,
                    "actual": actual_type
                }
                
        return {
            "is_schema_ok": len(missing_cols) == 0 and len(type_discrepancies) == 0,
            "missing_columns": missing_cols,
            "type_discrepancies": type_discrepancies
        }
        
    def check_missing_values(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Counts missing values and percentages.
        """
        report = {}
        total_rows = len(df)
        
        for col in df.columns:
            null_count = int(df[col].isna().sum())
            null_pct = (null_count / total_rows) * 100 if total_rows > 0 else 0
            
            # Also check for empty strings or sentinel strings representing null
            sentinel_count = 0
            if df[col].dtype == "object":
                sentinels = ["", "none", "null", "nan", "undefined", "unknown"]
                sentinel_count = int(df[col].astype(str).str.lower().str.strip().isin(sentinels).sum())
                
            total_missing = null_count + sentinel_count
            total_missing_pct = (total_missing / total_rows) * 100 if total_rows > 0 else 0
            
            report[col] = {
                "null_count": null_count,
                "sentinel_count": sentinel_count,
                "total_missing": total_missing,
                "percentage": round(total_missing_pct, 2)
            }
        return report

    def check_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Finds duplicate records.
        """
        duplicate_count = int(df.duplicated().sum())
        total_rows = len(df)
        percentage = (duplicate_count / total_rows) * 100 if total_rows > 0 else 0
        return {
            "duplicate_count": duplicate_count,
            "percentage": round(percentage, 2)
        }

    def check_outliers(self, df: pd.DataFrame, num_cols: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Finds outliers using the Z-score method (threshold = 3.0).
        """
        report = {}
        if num_cols is None:
            num_cols = ["traffic_volume", "average_speed", "congestion_index"]
            
        for col in num_cols:
            if col not in df.columns:
                continue
                
            # Convert to numeric, ignoring errors for z-score calculation
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(series) == 0:
                report[col] = {"outlier_count": 0, "percentage": 0.0, "bounds": (0, 0)}
                continue
                
            mean = series.mean()
            std = series.std()
            
            if std == 0:
                report[col] = {"outlier_count": 0, "percentage": 0.0, "bounds": (mean, mean)}
                continue
                
            lower_bound = mean - 3 * std
            upper_bound = mean + 3 * std
            
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            outlier_count = int(len(outliers))
            percentage = (outlier_count / len(df)) * 100 if len(df) > 0 else 0
            
            report[col] = {
                "outlier_count": outlier_count,
                "percentage": round(percentage, 2),
                "bounds": (round(lower_bound, 2), round(upper_bound, 2))
            }
        return report

    def get_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Runs all checks and computes a final Data Quality Score (0 to 100).
        """
        if len(df) == 0:
            return {"quality_score": 0.0, "summary": "Empty dataset"}
            
        schema_report = self.validate_schema(df)
        missing_report = self.check_missing_values(df)
        duplicate_report = self.check_duplicates(df)
        outlier_report = self.check_outliers(df)
        
        # Compute quality score
        # Base score is 100. Deduct based on issues.
        # Deduct weightings:
        # - Missing values: Max deduction 25 points. Deduct based on average missing percentage.
        # - Duplicates: Max deduction 20 points. Deduct direct percentage.
        # - Schema issues: Max deduction 25 points. Deduct 25 points if schema is broken.
        # - Outliers: Max deduction 15 points. Deduct based on percentage of outliers.
        # - Datatype corruptions: Max deduction 15 points. Deduct 3 points for each mismatched column.
        
        # 1. Missingness deduction
        total_cols = len(df.columns)
        avg_missing_pct = sum([info["percentage"] for info in missing_report.values()]) / total_cols if total_cols > 0 else 0
        missing_deduction = min(25.0, avg_missing_pct * 3.0) # Escalates quickly
        
        # 2. Duplicate deduction
        dup_pct = duplicate_report["percentage"]
        dup_deduction = min(20.0, dup_pct * 4.0)
        
        # 3. Schema deduction
        schema_deduction = 0.0
        if not schema_report["is_schema_ok"]:
            # Deduct 10 points per missing column (max 20)
            schema_deduction += min(20.0, len(schema_report["missing_columns"]) * 10)
            # Deduct 5 points per type mismatch (max 15)
            schema_deduction += min(15.0, len(schema_report["type_discrepancies"]) * 5)
        schema_deduction = min(25.0, schema_deduction)
        
        # 4. Outlier deduction
        avg_outlier_pct = sum([info["percentage"] for info in outlier_report.values()]) / len(outlier_report) if outlier_report else 0
        outlier_deduction = min(15.0, avg_outlier_pct * 2.0)
        
        # 5. Non-numeric coercibility check in numeric columns (corruption check)
        corrupted_cols_count = 0
        for col, target_type in self.target_schema.items():
            if col in df.columns and target_type in ["integer", "float"]:
                # Check for object columns containing uncoercible strings
                if df[col].dtype == "object":
                    parsed = pd.to_numeric(df[col], errors="coerce")
                    # If parsing introduced new NaNs, it means there are corrupted values (strings)
                    new_nans = parsed.isna().sum() - df[col].isna().sum()
                    if new_nans > 0:
                        corrupted_cols_count += 1
                        
        corruption_deduction = min(15.0, corrupted_cols_count * 5.0)
        
        final_score = 100.0 - (missing_deduction + dup_deduction + schema_deduction + outlier_deduction + corruption_deduction)
        final_score = max(0.0, round(final_score, 1))
        
        return {
            "quality_score": final_score,
            "schema": schema_report,
            "missing_values": missing_report,
            "duplicates": duplicate_report,
            "outliers": outlier_report,
            "corrupted_columns_count": corrupted_cols_count,
            "row_count": len(df),
            "col_count": total_cols
        }
