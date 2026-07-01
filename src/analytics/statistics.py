import pandas as pd

def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: Calculate Pearson correlation matrix for numerical parameters.
    """
    data = df.copy()

    numerical_columns = [
        "temp",
        "rain_1h",
        "snow_1h",
        "clouds_all",
        "traffic_volume",
    ]

    return data[numerical_columns].corr(method="pearson")

    raise NotImplementedError("correlation_matrix() is not implemented yet.")

def traffic_variance_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    TODO: Compute standard deviations and variances for speeds and volumes.
    """
    data = df.copy()

    summary = pd.DataFrame(
        {
            "Metric": [
                "Variance",
                "Standard Deviation",
                "Mean",
                "Median",
                "Minimum",
                "Maximum",
            ],
            "Value": [
                round(data["traffic_volume"].var(), 2),
                round(data["traffic_volume"].std(), 2),
                round(data["traffic_volume"].mean(), 2),
                round(data["traffic_volume"].median(), 2),
                round(data["traffic_volume"].min(), 2),
                round(data["traffic_volume"].max(), 2),
            ],
        }
    )

    return summary

    raise NotImplementedError("traffic_variance_analysis() is not implemented yet.")
