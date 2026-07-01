import pandas as pd
import numpy as np
def calculate_custom_congestion_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: Formulate and append custom Congestion Score (incorporating volume, weather, peaks).
    """
    data = df.copy()

    data["date_time"] = pd.to_datetime(data["date_time"])
    data["hour"] = data["date_time"].dt.hour

    # Rush hour: morning and evening commute windows
    data["is_rush_hour"] = data["hour"].isin([7, 8, 9, 16, 17, 18, 19])

    min_volume = data["traffic_volume"].min()
    max_volume = data["traffic_volume"].max()

    data["normalized_volume"] = (
        (data["traffic_volume"] - min_volume)
        / (max_volume - min_volume)
    )

    weather_weights = {
        "Clear": 0.00,
        "Clouds": 0.05,
        "Mist": 0.10,
        "Fog": 0.15,
        "Drizzle": 0.20,
        "Rain": 0.30,
        "Thunderstorm": 0.40,
        "Snow": 0.45,
    }

    data["weather_weight"] = data["weather_main"].map(weather_weights).fillna(0.10)

    rush_bonus = np.where(data["is_rush_hour"], 0.20, 0.00)

    data["congestion_score"] = (
        (data["normalized_volume"] * 0.80)
        + data["weather_weight"]
        + rush_bonus
    ) * 100

    data["congestion_score"] = data["congestion_score"].clip(0, 100).round(2)

    data["congestion_level"] = pd.cut(
        data["congestion_score"],
        bins=[0, 30, 60, 80, 100],
        labels=["Low", "Moderate", "High", "Critical"],
        include_lowest=True,
    )

    return data

    raise NotImplementedError("calculate_custom_congestion_score() is not implemented yet.")
