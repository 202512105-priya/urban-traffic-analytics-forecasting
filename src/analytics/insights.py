import pandas as pd
from typing import List

def generate_insights_report(df: pd.DataFrame) -> List[str]:
    """
    TODO: Convert numerical analytical facts into actionable English insights.
    """
    data = df.copy()

    insights = []

    avg_traffic = data["traffic_volume"].mean()

    max_row = data.loc[data["traffic_volume"].idxmax()]
    min_row = data.loc[data["traffic_volume"].idxmin()]

    busiest_weather = (
        data.groupby("weather_main")["traffic_volume"]
        .mean()
        .idxmax()
    )

    quietest_weather = (
        data.groupby("weather_main")["traffic_volume"]
        .mean()
        .idxmin()
    )

    insights.append(
        f"Average traffic volume recorded was {avg_traffic:.2f} vehicles."
    )

    insights.append(
        f"Highest traffic volume ({int(max_row['traffic_volume'])}) occurred on {max_row['date_time']}."
    )

    insights.append(
        f"Lowest traffic volume ({int(min_row['traffic_volume'])}) occurred on {min_row['date_time']}."
    )

    insights.append(
        f"'{busiest_weather}' weather recorded the highest average traffic volume."
    )

    insights.append(
        f"'{quietest_weather}' weather recorded the lowest average traffic volume."
    )

    return insights

    raise NotImplementedError("generate_insights_report() is not implemented yet.")
