import pandas as pd

class TrafficForecaster:
    """
    TODO: Implement the time-series forecasting model.
    
    Learning Objectives:
    - Fit time-series models (e.g. Meta Prophet, SARIMAX, or custom additive models) to historical datasets.
    - Forecast future intervals (horizon) with confidence intervals.
    - Perform time-series decomposition to isolate growth trends, daily cycles, and weekly cycles.
    """
    def __init__(self):
        self.model_type = "Uninitialized"
        
    def fit(self, df: pd.DataFrame, junction_id: int):
        """
        TODO: Filter and train a forecasting model on the history of a specific junction.
        
        Args:
            df (pd.DataFrame): Ingested cleaned traffic telemetry.
            junction_id (int): Junction index.
            
        Returns:
            self
        """
        raise NotImplementedError(
            "TrafficForecaster.fit() is not implemented yet. "
            "Please write the training logic in src/forecasting/forecaster.py."
        )
        
    def forecast(self, horizon_hours: int = 168) -> pd.DataFrame:
        """
        TODO: Forecast future traffic volume.
        
        Requirements:
        1. Generate a future timeline of horizon_hours from the end of the history.
        2. Predict volume, upper bounds, and lower bounds (e.g. 95% intervals).
        3. Extract trend and seasonal subcomponents (daily, weekly, yearly).
        4. Return a DataFrame with columns:
           - timestamp (datetime)
           - forecasted_volume (int)
           - lower_bound (int)
           - upper_bound (int)
           - trend (float)
           - seasonal_daily (float)
           - seasonal_weekly (float)
        """
        raise NotImplementedError(
            "TrafficForecaster.forecast() is not implemented yet. "
            "Please write the forecasting prediction pipeline in src/forecasting/forecaster.py."
        )
