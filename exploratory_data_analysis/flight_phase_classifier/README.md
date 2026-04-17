# Flight Phase Classifier

This project classifies aircraft flight phases from unlabeled time-series sensor data using NASA flight recorder data. The core challenge: there were no phase labels in the dataset, so rather than relying solely on clustering output, I researched the altitude thresholds and dynamics of each flight phase and encoded that domain knowledge directly into a rule-based classifier. This transformed what started as a clustering exploration into a functioning phase prediction system.

## Data Source

Data comes from the [NASA DASHlink repository](https://c3.ndc.nasa.gov/dashlink/resources/), specifically the **Tail_681_1** dataset, composed of `.mat` (MATLAB) binary files containing multi-channel flight recorder time-series.

## Approach

The project began as a KMeans clustering exercise, but the dataset had no ground-truth phase labels — making it impossible to validate cluster assignments by name. To solve this, I researched the altitude ranges and flight dynamics characteristic of each phase (taxi, takeoff, climb, cruise, descent, landing), then coded those rules explicitly. This classifier provided reliable phase labels that the visualizations and analysis are built on.

## Notebooks

The repository contains four notebooks documenting the full pipeline:

- `1-exploring_dataset.ipynb` — Summary statistics and initial exploration
- `2-data_cleaning.ipynb` — Data formatting, filtering, and cleaning
- `3-aircraft_time-series_feature_engineering_clustering.ipynb` — Feature engineering and KMeans clustering to identify flight phases
- `4-data_visualization_relationship_analysis.ipynb` — Visualizations of altitude, speed, and phase patterns

**The primary deliverable is `4-data_visualization_relationship_analysis.ipynb`.** Notebooks 1–3 document the data acquisition and preprocessing pipeline but are not required to run the visualizations.

## Goals

- Predict the flight phase of an aircraft at any point in a flight recording
- Demonstrate that domain-informed rule-based classification can supplement or replace cluster labeling on unlabeled sensor data
- Visualize altitude, speed, and phase transitions across a complete flight

## Tools

- Python
- Pandas, NumPy
- Scikit-learn
- Matplotlib, Plotly

## Output

- Phase-labeled flight time-series (taxi, takeoff, climb, cruise, descent, landing)
- Visual summaries of altitude and airspeed across flight stages
- Relationship analysis between sensor channels and classified phases
