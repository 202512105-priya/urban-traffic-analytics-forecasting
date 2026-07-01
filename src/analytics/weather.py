import pandas as pd

def weather_impact_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: Calculate traffic volume/speed indices grouped by weather condition.
    """
    data = df.copy()

    summary = (
        data.groupby("weather_main")["traffic_volume"]
        .agg(
            average_traffic="mean",
            median_traffic="median",
            max_traffic="max",
            min_traffic="min",
            std_deviation="std",
            observations="count",
        )
        .reset_index()
        .sort_values("average_traffic", ascending=False)
    )

    summary["average_traffic"] = summary["average_traffic"].round(2)
    summary["median_traffic"] = summary["median_traffic"].round(2)
    summary["std_deviation"] = summary["std_deviation"].round(2)

    return summary

    raise NotImplementedError("weather_impact_analysis() is not implemented yet.")

def temperature_correlation_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: Correlation details of temperature against traffic volume.
    """
    data = df.copy()

    data["temperature_celsius"] = data["temp"] - 273.15

    correlation = data[["temperature_celsius", "traffic_volume"]].corr().iloc[0, 1]

    return pd.DataFrame(
        {
            "Metric": ["Temperature vs Traffic Correlation"],
            "Correlation": [round(correlation, 4)],
        }
    )

    raise NotImplementedError("temperature_correlation_analysis() is not implemented yet.")
