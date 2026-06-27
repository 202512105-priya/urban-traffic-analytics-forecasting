import pandas as pd
from typing import Dict, Any, Optional

class TrafficExplorer:
    """
    TODO: Implement the analytics query and aggregation engine.
    
    Learning Objectives:
    - Group and aggregate time-series data.
    - Write analytical metrics (averages, sums, rates).
    - Handle date, junction, and categorical filtering.
    """
    def __init__(self):
        pass

    def get_summary_kpis(self, df: pd.DataFrame, junction_id: Optional[int] = None) -> Dict[str, Any]:
        """
        TODO: Compute summary KPIs.
        
        Requirements:
        1. Calculate: total records, average volume, average speed, max volume, congestion rate (volume/capacity threshold), and active junctions.
        
        Args:
            df (pd.DataFrame): Input dataset.
            junction_id (int, optional): Filter for a specific junction.
            
        Returns:
            Dict: Key value pairs of KPIs.
        """
        raise NotImplementedError(
            "TrafficExplorer.get_summary_kpis() is not implemented yet. "
            "Please implement the KPI calculations in src/analytics/explorer.py."
        )

    def get_hourly_peaks(self, df: pd.DataFrame, junction_id: Optional[int] = None) -> pd.DataFrame:
        """
        TODO: Aggregate traffic volume, speed, and congestion by hour of the day (0-23).
        
        Args:
            df (pd.DataFrame): Input dataset.
            junction_id (int, optional): Filter.
            
        Returns:
            pd.DataFrame: Aggregated hourly stats.
        """
        raise NotImplementedError(
            "TrafficExplorer.get_hourly_peaks() is not implemented yet. "
            "Please implement the hourly peak aggregation in src/analytics/explorer.py."
        )

    def get_weather_impact(self, df: pd.DataFrame, junction_id: Optional[int] = None) -> pd.DataFrame:
        """
        TODO: Aggregate traffic volume, speed, and congestion by weather conditions.
        
        Args:
            df (pd.DataFrame): Input dataset.
            
        Returns:
            pd.DataFrame: Aggregated weather impact stats.
        """
        raise NotImplementedError(
            "TrafficExplorer.get_weather_impact() is not implemented yet. "
            "Please implement the weather impact aggregation in src/analytics/explorer.py."
        )

    def get_holiday_comparison(self, df: pd.DataFrame, junction_id: Optional[int] = None) -> pd.DataFrame:
        """
        TODO: Compare average traffic volume profiles on holidays vs. regular days by hour.
        
        Args:
            df (pd.DataFrame): Input dataset.
            
        Returns:
            pd.DataFrame: Grouped hourly holiday stats.
        """
        raise NotImplementedError(
            "TrafficExplorer.get_holiday_comparison() is not implemented yet. "
            "Please implement the holiday comparison aggregation in src/analytics/explorer.py."
        )

    def get_monthly_trends(self, df: pd.DataFrame, junction_id: Optional[int] = None) -> pd.DataFrame:
        """
        TODO: Aggregate average volume, speed, and congestion by month.
        
        Args:
            df (pd.DataFrame): Input dataset.
            
        Returns:
            pd.DataFrame: Grouped monthly stats.
        """
        raise NotImplementedError(
            "TrafficExplorer.get_monthly_trends() is not implemented yet. "
            "Please implement the monthly trend aggregation in src/analytics/explorer.py."
        )

    def get_junction_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        TODO: Group by junction and calculate total records, average volume, max volume, average speed, and congestion statistics.
        
        Args:
            df (pd.DataFrame): Input dataset.
            
        Returns:
            pd.DataFrame: Junction benchmark stats.
        """
        raise NotImplementedError(
            "TrafficExplorer.get_junction_summary() is not implemented yet. "
            "Please implement the junction summary aggregation in src/analytics/explorer.py."
        )
