import pandas as pd

def get_traffic_peaks(df: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: Identify peak hourly volumes across junctions.
    """
    data = df.copy()

    data["date_time"] = pd.to_datetime(data["date_time"])
    data["hour"] = data["date_time"].dt.hour

    hourly_summary = (
        data.groupby("hour")["traffic_volume"]
        .agg(
            average_traffic="mean",
            max_traffic="max",
            min_traffic="min",
            observations="count",
        )
        .reset_index()
    )

    hourly_summary["average_traffic"] = hourly_summary["average_traffic"].round(2)

    return hourly_summary.sort_values(
        by="average_traffic", ascending=False
    ).reset_index(drop=True)

    raise NotImplementedError("get_traffic_peaks() is not implemented yet.")
