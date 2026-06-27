import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_sample_data(output_dir="data/raw", num_days=365):
    """
    Generates a high-fidelity synthetic traffic dataset simulating 1 year of hourly traffic across 4 junctions.
    Models:
    - Daily/weekly/yearly seasonality
    - Weather impacts (rain, snow, temperature)
    - Holidays
    - Random incidents (accidents, construction) affecting congestion and speed
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "traffic_raw.csv")
    
    if os.path.exists(file_path):
        print(f"Dataset already exists at {file_path}. Skipping generation.")
        return pd.read_csv(file_path, parse_dates=["timestamp"])
    
    print(f"Generating synthetic traffic dataset for {num_days} days...")
    
    # Setup seed for reproducibility
    np.random.seed(42)
    
    # Generate timestamp range
    start_date = datetime(2025, 1, 1, 0, 0, 0)
    timestamps = [start_date + timedelta(hours=i) for i in range(num_days * 24)]
    
    junctions = [1, 2, 3, 4]
    
    # Base traffic capacity for junctions
    junction_capacities = {1: 800, 2: 400, 3: 1200, 4: 600}
    junction_base_volumes = {1: 300, 2: 120, 3: 500, 4: 200}
    
    data_list = []
    
    # Generate list of holidays
    holidays = {
        (1, 1),   # New Year
        (5, 26),  # Memorial Day
        (7, 4),   # July 4th
        (9, 1),   # Labor Day
        (11, 27), # Thanksgiving
        (12, 25), # Christmas
    }
    
    for dt in timestamps:
        hour = dt.hour
        day_of_week = dt.weekday()
        month = dt.month
        is_weekend = day_of_week >= 5
        is_holiday = (month, dt.day) in holidays
        
        # Simple seasonal temperature model (sinusoidal)
        # Tmax in July (month 7), Tmin in January (month 1)
        temp_base = 15 - 12 * np.cos(2 * np.pi * (month - 1) / 12)
        # Add daily temperature variation (warmest at 15:00, coolest at 05:00)
        temp_daily = 6 * np.sin(2 * np.pi * (hour - 9) / 24)
        temperature = round(temp_base + temp_daily + np.random.normal(0, 2), 1)
        
        # Determine weather condition
        # Higher chance of rain in spring, snow in winter
        rain_prob = 0.15 if month in [3, 4, 5, 10, 11] else 0.08
        snow_prob = 0.20 if month in [12, 1, 2] and temperature < 2.0 else 0.0
        
        weather_roll = np.random.rand()
        if snow_prob > 0 and weather_roll < snow_prob:
            weather = "Snowy"
        elif weather_roll < rain_prob:
            weather = "Rainy"
        elif weather_roll < rain_prob + 0.05:
            weather = "Foggy"
        else:
            weather = "Clear"
            
        for j_id in junctions:
            capacity = junction_capacities[j_id]
            base_vol = junction_base_volumes[j_id]
            
            # Temporal multipliers
            # Weekdays: Peak at 8 AM and 5 PM
            if not is_weekend and not is_holiday:
                hourly_multiplier = 0.2 + 0.6 * np.exp(-((hour - 8)**2)/4) + 0.7 * np.exp(-((hour - 17)**2)/6)
            # Weekends / Holidays: Broad peak in early afternoon
            else:
                hourly_multiplier = 0.15 + 0.5 * np.exp(-((hour - 13)**2)/16)
                
            # Weekly multiplier (Friday has slightly more, Sunday less)
            weekly_multipliers = [1.0, 1.0, 1.05, 1.05, 1.15, 0.85, 0.75]
            weekly_multiplier = weekly_multipliers[day_of_week]
            if is_holiday:
                weekly_multiplier = 0.70 # Holiday travel drop or shift
                
            # Weather impacts: Rain/Snow reduces volume slightly (people stay home or drive slower)
            weather_volume_multiplier = 1.0
            if weather == "Rainy":
                weather_volume_multiplier = 0.90
            elif weather == "Snowy":
                weather_volume_multiplier = 0.75
            elif weather == "Foggy":
                weather_volume_multiplier = 0.85
                
            # Add random noise
            noise = np.random.normal(1.0, 0.08)
            
            # Final Volume calculation
            volume = int(base_vol * hourly_multiplier * weekly_multiplier * weather_volume_multiplier * noise)
            volume = max(0, volume) # Cannot be negative
            
            # Introduce missingness and duplicates in raw data to simulate real data quality issues
            # We want about 1.5% missing values and 0.5% duplicate records
            
            # Outliers (e.g. accidents or extreme events)
            # 0.2% chance of huge congestion spike
            incident_roll = np.random.rand()
            is_incident = incident_roll < 0.002
            
            if is_incident:
                volume = int(volume * np.random.uniform(1.5, 2.5))
                
            # Calculate congestion index based on volume and capacity (0.0 to 10.0 scale)
            raw_ratio = volume / capacity
            if is_incident:
                raw_ratio *= 1.5
            if weather == "Rainy":
                raw_ratio *= 1.2
            elif weather == "Snowy":
                raw_ratio *= 1.5
            elif weather == "Foggy":
                raw_ratio *= 1.3
                
            congestion = min(10.0, round(raw_ratio * 7.5, 2))
            congestion = max(0.0, congestion)
            
            # Average speed (negatively correlated with congestion)
            # Base speed is 60 km/h, drops as congestion increases
            speed_drop = congestion * 4.5
            weather_speed_drop = 0
            if weather == "Rainy":
                weather_speed_drop = 8
            elif weather == "Snowy":
                weather_speed_drop = 20
            elif weather == "Foggy":
                weather_speed_drop = 12
                
            avg_speed = round(max(10.0, 60.0 - speed_drop - weather_speed_drop + np.random.normal(0, 3)), 1)
            
            # Populate row
            row = {
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "junction_id": j_id,
                "traffic_volume": volume,
                "average_speed": avg_speed,
                "weather_condition": weather,
                "temperature": temperature,
                "is_holiday": 1 if is_holiday else 0,
                "congestion_index": congestion
            }
            
            data_list.append(row)
            
    df = pd.DataFrame(data_list)
    
    # Introduce some synthetic duplicates
    dup_indices = np.random.choice(df.index, size=int(len(df) * 0.005), replace=False)
    dups = df.loc[dup_indices].copy()
    df = pd.concat([df, dups], ignore_index=True)
    
    # Introduce some synthetic missing values (NaNs) in key columns
    for col in ["traffic_volume", "average_speed", "weather_condition"]:
        nan_indices = np.random.choice(df.index, size=int(len(df) * 0.015), replace=False)
        df.loc[nan_indices, col] = np.nan
        
    # Introduce datatype corruption (some strings in numeric columns)
    # We will introduce a small fraction of string values in 'temperature' e.g. "missing" or "temp_err"
    corrupt_indices = np.random.choice(df.index, size=5, replace=False)
    df.loc[corrupt_indices, "temperature"] = "ERR"
    
    # Sort by timestamp and junction
    # We parse the timestamp back to string since we created corruptions, then we'll save
    df.to_csv(file_path, index=False)
    print(f"Generated raw traffic dataset at {file_path} with {len(df)} rows.")
    return df

if __name__ == "__main__":
    generate_sample_data()
