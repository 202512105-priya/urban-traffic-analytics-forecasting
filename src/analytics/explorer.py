import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class TrafficExplorer:
    """
    Analytics engine to compute statistical aggregations, 
    filter traffic profiles, and structure data for interactive Plotly charts.
    """
    def __init__(self):
        pass
        
    def _apply_filter(self, df: pd.DataFrame, junction_id: Optional[int] = None) -> pd.DataFrame:
        """
        Applies filter to dataset.
        """
        if junction_id is not None and junction_id in df["junction_id"].values:
            return df[df["junction_id"] == junction_id]
        return df

    def get_summary_kpis(self, df: pd.DataFrame, junction_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Computes summary KPIs for the dashboard.
        """
        f_df = self._apply_filter(df, junction_id)
        if len(f_df) == 0:
            return {
                "total_records": 0, "avg_volume": 0, "avg_speed": 0.0, 
                "max_volume": 0, "congestion_rate": 0.0, "active_junctions": 0
            }
            
        total_records = len(f_df)
        avg_volume = int(f_df["traffic_volume"].mean())
        avg_speed = round(f_df["average_speed"].mean(), 1)
        max_volume = int(f_df["traffic_volume"].max())
        active_junctions = int(f_df["junction_id"].nunique())
        
        # High congestion defined as congestion index > 6.0
        high_congestion_count = (f_df["congestion_index"] > 6.0).sum()
        congestion_rate = round((high_congestion_count / total_records) * 100, 2) if total_records > 0 else 0.0
        
        return {
            "total_records": total_records,
            "avg_volume": avg_volume,
            "avg_speed": avg_speed,
            "max_volume": max_volume,
            "congestion_rate": congestion_rate,
            "active_junctions": active_junctions
        }

    def get_hourly_peaks(self, df: pd.DataFrame, junction_id: Optional[int] = None) -> pd.DataFrame:
        """
        Aggregates traffic volume and speed by hour of the day.
        """
        f_df = self._apply_filter(df, junction_id).copy()
        if "hour" not in f_df.columns:
            f_df["hour"] = f_df["timestamp"].dt.hour
            
        agg = f_df.groupby("hour").agg(
            avg_volume=("traffic_volume", "mean"),
            avg_speed=("average_speed", "mean"),
            avg_congestion=("congestion_index", "mean")
        ).reset_index()
        
        agg["avg_volume"] = agg["avg_volume"].round(0).astype(int)
        agg["avg_speed"] = agg["avg_speed"].round(1)
        agg["avg_congestion"] = agg["avg_congestion"].round(2)
        return agg

    def get_weather_impact(self, df: pd.DataFrame, junction_id: Optional[int] = None) -> pd.DataFrame:
        """
        Aggregates traffic features by weather conditions.
        """
        f_df = self._apply_filter(df, junction_id)
        agg = f_df.groupby("weather_condition").agg(
            avg_volume=("traffic_volume", "mean"),
            avg_speed=("average_speed", "mean"),
            avg_congestion=("congestion_index", "mean"),
            record_count=("traffic_volume", "count")
        ).reset_index()
        
        agg["avg_volume"] = agg["avg_volume"].round(0).astype(int)
        agg["avg_speed"] = agg["avg_speed"].round(1)
        agg["avg_congestion"] = agg["avg_congestion"].round(2)
        return agg

    def get_holiday_comparison(self, df: pd.DataFrame, junction_id: Optional[int] = None) -> pd.DataFrame:
        """
        Compares hourly traffic patterns on holidays vs regular days.
        """
        f_df = self._apply_filter(df, junction_id).copy()
        if "hour" not in f_df.columns:
            f_df["hour"] = f_df["timestamp"].dt.hour
            
        agg = f_df.groupby(["hour", "is_holiday"]).agg(
            avg_volume=("traffic_volume", "mean"),
            avg_speed=("average_speed", "mean")
        ).reset_index()
        
        agg["avg_volume"] = agg["avg_volume"].round(0).astype(int)
        agg["day_type"] = agg["is_holiday"].map({1: "Holiday", 0: "Regular Day"})
        return agg

    def get_monthly_trends(self, df: pd.DataFrame, junction_id: Optional[int] = None) -> pd.DataFrame:
        """
        Aggregates monthly traffic trends.
        """
        f_df = self._apply_filter(df, junction_id).copy()
        if "month" not in f_df.columns:
            f_df["month"] = f_df["timestamp"].dt.month
            
        agg = f_df.groupby("month").agg(
            avg_volume=("traffic_volume", "mean"),
            avg_speed=("average_speed", "mean"),
            avg_congestion=("congestion_index", "mean")
        ).reset_index()
        
        # Map month integers to names
        month_names = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }
        agg["month_name"] = agg["month"].map(month_names)
        # Sort by month number
        agg = agg.sort_values("month").reset_index(drop=True)
        return agg

    def get_junction_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes summary statistics for each junction to compare performance.
        """
        agg = df.groupby("junction_id").agg(
            total_records=("traffic_volume", "count"),
            avg_volume=("traffic_volume", "mean"),
            max_volume=("traffic_volume", "max"),
            avg_speed=("average_speed", "mean"),
            avg_congestion=("congestion_index", "mean"),
            peak_congestion=("congestion_index", "max")
        ).reset_index()
        
        agg["avg_volume"] = agg["avg_volume"].round(0).astype(int)
        agg["avg_speed"] = agg["avg_speed"].round(1)
        agg["avg_congestion"] = agg["avg_congestion"].round(2)
        agg["peak_congestion"] = agg["peak_congestion"].round(2)
        return agg
