# Day 1 Dataset Report

## Dataset Name

Metro Interstate Traffic Volume

## Total Rows

48204

## Total Columns

9

## Numerical Features

holiday,temp,rain,snow,traffic volume

## Categorical Features

weather main, weather desc

## Datetime Features

date time

## Proposed Target Variable

traffic_volume

## Missing Values

Only the `holiday` column contains missing values.

- Missing Values: 48,143
- Percentage: ~99.87%

### Observation

Most days in the dataset are non-holidays. The missing values likely indicate regular working days rather than missing sensor readings.

This assumption will be verified during the data cleaning phase.

## Duplicate Records

- Duplicate Rows: 17

### Observation

A small number of duplicate records exist.

Further investigation is required to determine whether these duplicates are accidental data duplication or repeated traffic sensor readings.

## Business Problem

Urban traffic congestion impacts commuting efficiency, fuel consumption, emergency response times, and city infrastructure planning.

The objective of this project is to analyze historical traffic patterns, identify factors contributing to congestion, and develop predictive models capable of forecasting traffic volume and congestion levels.

## Initial Observations

- Dataset contains 48,204 traffic observations.
- Only one column contains missing values (`holiday`).
- A small number of duplicate records (17) exist.
- The dataset includes temporal, weather, and traffic-related features, making it suitable for predictive analytics.
- `traffic_volume` appears to be the most appropriate target variable.
- `date_time` should be converted to a datetime datatype before further analysis.
- The dataset is suitable for both descriptive analytics and machine learning tasks.

## Questions for Day 2

- Should missing values in the `holiday` column be treated as "None" or left as missing?
- Should duplicate records be removed?
- Are there outliers in the numerical features?
- Does the dataset contain invalid or impossible values?
- Should numerical features be scaled for future modeling?