# Flight Phase Classification and Visualization

This project analyzes NASA aircraft flight data to identify different flight phases using time-series feature engineering and clustering. The workflow includes data exploration, cleaning, feature creation, and visualization of patterns related to altitude and flight dynamics.

## Project Files

- `1-exploring_dataset.ipynb`: Summary statistics and initial exploration
- `2-data_cleaning.ipynb`: Data formatting, filtering, and cleaning
- `3-aircraft_time-series_feature_engineering_clustering.ipynb`: Feature engineering and KMeans clustering to identify flight phases
- `4-data_visualization_relationship_analysis.ipynb`: Visualizations of altitude, speed, and phase patterns

## Goals

- Understand the structure and quality of raw flight data
- Clean and prepare time-series data
- Engineer features like smoothed altitude and acceleration
- Use clustering to label phases like taxi, climb, cruise, and descent
- Visualize the results and relationships between flight features

## Tools

- Python
- Pandas, NumPy
- Scikit-learn
- Matplotlib, Plotly

## Output

- Cleaned and labeled flight datasets
- Clustered time-series with identified phases
- Visual summaries of altitude and speed across flight stages
