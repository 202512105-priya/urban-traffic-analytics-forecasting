import pandas as pd

def peak_hour_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: Calculate average volume and speed grouped by hour of the day.
    """
    data=df.copy()
    data["date_time"]=pd.to_datetime(data["date_time"])
    data["hour"]= data["date_time"].dt.hour
    hourly_summary = (
        data.groupby("hour")["traffic_volume"]
        .agg(
                average_traffic="mean",
                max_traffic="max",
                min_traffic="min",
                observations="count",)
                                                              .reset_index()
                                                            )
    hourly_summary["average_traffic"]=(hourly_summary["average_traffic"].round(2))
    return hourly_summary

    raise NotImplementedError("peak_hour_analysis() is not implemented yet in src/analytics/temporal.py.")

def weekday_vs_weekend_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: Compare traffic densities on weekdays vs weekends.
    """
    data=df.copy()
    data["date_time"]=pd.to_datetime(data["date_time"])
    data["day_name"]=data["date_time"].dt.day_name()
    data["day_type"]=data["day_name"].apply(
        lambda day: "Weekend"
        if day in ["Saturday","Sunday"]
        else "Weekday"
    )
    summary=(
        data.groupby("day_type")["traffic_volume"]

        .agg(

            average_traffic="mean",

            max_traffic="max",

            min_traffic="min",

            std_deviation="std",

            observations="count",

        )

        .reset_index()

    )

    summary["average_traffic"] = summary["average_traffic"].round(2)

    summary["std_deviation"] = summary["std_deviation"].round(2)

    return summary
    


    raise NotImplementedError("weekday_vs_weekend_analysis() is not implemented yet.")

def monthly_trend_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: Group traffic counts by month.
    """
    data = df.copy()

    data["date_time"] = pd.to_datetime(data["date_time"])

    data["month_number"] = data["date_time"].dt.month

    data["month"] = data["date_time"].dt.month_name()

    monthly_summary = (

        data.groupby(["month_number", "month"])["traffic_volume"]

        .agg(

            average_traffic="mean",

            max_traffic="max",

            min_traffic="min",

            std_deviation="std",

            observations="count",

        )

        .reset_index()

        .sort_values("month_number")

    )

    monthly_summary["average_traffic"] = (

        monthly_summary["average_traffic"].round(2)

    )

    monthly_summary["std_deviation"] = (

        monthly_summary["std_deviation"].round(2)

    )

    return monthly_summary.drop(columns="month_number")
    raise NotImplementedError("monthly_trend_analysis() is not implemented yet.")
