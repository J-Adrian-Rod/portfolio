# Spotify Wrapped Data Enrichment and Analysis

This project analyzes my Spotify listening history by enriching it with metadata and audio features using the Spotify Web API. The goal is to replicate and expand on the insights provided by the yearly Spotify Wrapped, including top songs, artists, and listening trends.

## Project Files

- `1-getting_data.ipynb`: Loads and combines raw Spotify streaming history JSON files.
- `2-api_call.ipynb`: Fetches metadata for tracks (e.g., ID, name, artist, album) from the Spotify API.
- `3-spotify_wrapped_data.ipynb`: Merges streaming and metadata, analyzes top tracks/artists by year and overall.
- `4-api_call_attributes.ipynb`: Retrieves audio features like energy, tempo, and danceability for each track.

## Goals

- Parse and clean Spotify streaming history data
- Map tracks to Spotify metadata using API calls
- Analyze user listening trends over time
- Enrich data with audio characteristics (e.g., energy, valence)
- Enable deeper exploration of listening behaviors and preferences

## Tools

- Python  
- Pandas, NumPy  
- Spotipy (Spotify API)  
- Requests  
- Matplotlib, Plotly (optional for visualization)

## Output

- Merged dataset of streaming history with track metadata
- Audio features for each track (danceability, energy, etc.)
- Aggregated top songs, artists, and genres by year
- Dataset ready for dashboards, visual storytelling, or ML-based recommendation systems
