import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Add project root to path if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

class TrafficForecaster:
    """
    Time-series forecasting module.
    Attempts to use Meta's Prophet for advanced forecasting.
    Falls back to a high-fidelity multi-seasonal additive trend model
    (incorporating hourly, daily, and weekly cycles plus linear trend projection)
    if Prophet is unavailable or fails.
    """
    def __init__(self):
        self.model_type = "Statistical Fallback (Multi-Seasonal Additive)"
        self.prophet_model = None
        self.history = None
        self.junction_id = None
        self.residual_std = 0.0
        
    def fit(self, df: pd.DataFrame, junction_id: int):
        """
        Fits the forecaster on historical data for a specific junction.
        """
        self.junction_id = junction_id
        
        # Filter for the junction
        j_df = df[df["junction_id"] == junction_id].copy()
        j_df = j_df.sort_values("timestamp").reset_index(drop=True)
        
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(j_df["timestamp"]):
            j_df["timestamp"] = pd.to_datetime(j_df["timestamp"])
            
        self.history = j_df
        
        # Try to fit using Prophet
        try:
            from prophet import Prophet
            
            # Prepare data frame for Prophet
            prophet_df = j_df[["timestamp", "traffic_volume"]].rename(
                columns={"timestamp": "ds", "traffic_volume": "y"}
            )
            # Remove timezone if any
            if prophet_df["ds"].dt.tz is not None:
                prophet_df["ds"] = prophet_df["ds"].dt.tz_localize(None)
                
            model = Prophet(
                growth="linear",
                yearly_seasonality=False,
                weekly_seasonality=True,
                daily_seasonality=True,
                interval_width=0.95
            )
            model.fit(prophet_df)
            
            self.prophet_model = model
            self.model_type = "Meta Prophet (Time Series Regressor)"
            print(f"Successfully fit Prophet model for Junction {junction_id}.")
            return self
        except (ImportError, Exception) as e:
            # Fall back to custom statistical model
            self.model_type = "Statistical Fallback (Multi-Seasonal Additive)"
            print(f"Prophet not available or failed ({e}). Fitting statistical fallback model...")
            self._fit_fallback(j_df)
            return self

    def _fit_fallback(self, df: pd.DataFrame):
        """
        Fits a custom additive multi-seasonal model:
        y_hat = Trend(t) + Hourly_Seasonality(t_hour) + Weekly_Seasonality(t_day) + noise
        """
        df = df.copy()
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.weekday
        
        # Convert timestamp to ordinal index for linear regression
        start_time = df["timestamp"].min()
        df["time_idx"] = (df["timestamp"] - start_time).dt.total_seconds() / 3600.0
        
        # 1. Fit linear trend: y = m * x + c
        X_trend = df["time_idx"].values
        y_val = df["traffic_volume"].values
        
        # Fit trend using numpy least squares
        A = np.vstack([X_trend, np.ones(len(X_trend))]).T
        m, c = np.linalg.lstsq(A, y_val, rcond=None)[0]
        
        self.trend_slope = m
        self.trend_intercept = c
        self.start_time = start_time
        
        # Calculate trend-detrended values
        df["detrended"] = y_val - (m * X_trend + c)
        
        # 2. Extract Hourly Seasonality (24 values)
        self.hourly_profile = df.groupby("hour")["detrended"].mean().to_dict()
        
        # Detrend and de-hourly values
        df["dehourly"] = df["detrended"] - df["hour"].map(self.hourly_profile)
        
        # 3. Extract Weekly Seasonality (7 values)
        self.weekly_profile = df.groupby("day_of_week")["dehourly"].mean().to_dict()
        
        # Compute residuals to estimate uncertainty bounds
        df["y_hat"] = (m * X_trend + c) + df["hour"].map(self.hourly_profile) + df["day_of_week"].map(self.weekly_profile)
        residuals = df["traffic_volume"] - df["y_hat"]
        self.residual_std = residuals.std()
        
    def forecast(self, horizon_hours: int = 168) -> pd.DataFrame:
        """
        Generates forecast for the specified horizon (in hours).
        Returns a DataFrame containing forecasted_volume, upper_bound, lower_bound, trend, and seasonality.
        """
        if self.history is None:
            raise ValueError("Forecaster has not been fitted yet. Please call .fit() first.")
            
        last_time = self.history["timestamp"].max()
        future_times = [last_time + timedelta(hours=i+1) for i in range(horizon_hours)]
        
        # 1. Predict using Prophet
        if self.prophet_model is not None:
            try:
                future_df = pd.DataFrame({"ds": future_times})
                forecast_res = self.prophet_model.predict(future_df)
                
                # Extract columns
                res_df = pd.DataFrame({
                    "timestamp": forecast_res["ds"],
                    "forecasted_volume": forecast_res["yhat"].clip(lower=0).round(0).astype(int),
                    "lower_bound": forecast_res["yhat_lower"].clip(lower=0).round(0).astype(int),
                    "upper_bound": forecast_res["yhat_upper"].clip(lower=0).round(0).astype(int),
                    "trend": forecast_res["trend"].round(2),
                    "seasonal_daily": forecast_res["daily"] if "daily" in forecast_res else 0.0,
                    "seasonal_weekly": forecast_res["weekly"] if "weekly" in forecast_res else 0.0
                })
                return res_df
            except Exception as e:
                print(f"Prophet forecast failed ({e}), using statistical fallback forecast...")
                # fall through to statistical fallback
                
        # 2. Predict using Fallback Model
        forecast_rows = []
        for dt in future_times:
            hour = dt.hour
            day_of_week = dt.weekday()
            time_idx = (dt - self.start_time).total_seconds() / 3600.0
            
            # Reconstruct forecast
            trend_val = self.trend_slope * time_idx + self.trend_intercept
            hour_val = self.hourly_profile.get(hour, 0.0)
            week_val = self.weekly_profile.get(day_of_week, 0.0)
            
            pred = max(0, trend_val + hour_val + week_val)
            
            # Uncertainty bounds (95% confidence interval using 1.96 * residual std dev)
            margin = 1.96 * self.residual_std
            lower = max(0, int(round(pred - margin)))
            upper = int(round(pred + margin))
            
            forecast_rows.append({
                "timestamp": dt,
                "forecasted_volume": int(round(pred)),
                "lower_bound": lower,
                "upper_bound": upper,
                "trend": round(trend_val, 2),
                "seasonal_daily": round(hour_val, 2),
                "seasonal_weekly": round(week_val, 2)
            })
            
        return pd.DataFrame(forecast_rows)
