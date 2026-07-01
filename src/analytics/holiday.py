import pandas as pd

def holiday_impact_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: Group hourly volume profiles on holidays vs. regular days.
    """
    data = df.copy()

    # In this dataset, 'None' indicates a normal day.

    data["day_type"] = data["holiday"].apply(

        lambda x: "Holiday" if x != "None" else "Non-Holiday"

    )

    summary = (

        data.groupby("day_type")["traffic_volume"]

        .agg(

            average_traffic="mean",

            median_traffic="median",

            max_traffic="max",

            min_traffic="min",

            std_deviation="std",

            observations="count",

        )

        .reset_index()

    )

    summary["average_traffic"] = summary["average_traffic"].round(2)

    summary["median_traffic"] = summary["median_traffic"].round(2)

    summary["std_deviation"] = summary["std_deviation"].round(2)

    return summary
    raise NotImplementedError("holiday_impact_analysis() is not implemented yet.")
