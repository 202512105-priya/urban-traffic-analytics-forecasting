import pandas as pd
import os

def generate_sample_data(output_dir: str = "data/raw", num_days: int = 365) -> pd.DataFrame:
    """
    TODO: Implement a synthetic data generator to simulate 1 year of hourly traffic telemetry.
    
    Requirements:
    1. Generate hourly timestamps for 365 days across 4 junctions.
    2. Add features: traffic_volume, average_speed, weather_condition, temperature, is_holiday, congestion_index.
    3. Introduce realistic characteristics (e.g. rush hours on weekdays, lower volume on weekends, weather delays).
    4. Introduce quality issues: 1.5% missing values, 0.5% duplicate rows, and string corruptions in numeric columns (e.g. "ERR").
    5. Save the generated DataFrame to output_dir/traffic_raw.csv and return it.
    
    Args:
        output_dir (str): Path to save the raw CSV file.
        num_days (int): Number of days of hourly records to generate.
        
    Returns:
        pd.DataFrame: The generated raw traffic dataset.
    """
    raise NotImplementedError(
        "generate_sample_data() is not implemented yet. "
        "Please write the synthetic data generation logic in src/utils/data_generator.py."
    )
