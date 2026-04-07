#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Import


# In[30]:


import pandas as pd 
import json
from typing import List
import os
from os import listdir
import matplotlib.pyplot as plt
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.express as px
import plotly.io as pio
from datetime import datetime
import pytz 
from collections import Counter
from sklearn.cluster import KMeans


# In[ ]:


# Title: get_streaming

# Description:
# Scans a specified directory for files starting with 'Streaming_History_Audio_', 
# loads each file's JSON contents, 
# aggregates the streaming records from all files into a single list of dictionaries, 
# and returns the full combined history as structured data.


# In[23]:


def get_streamings(path: str = 'data') -> List[dict]:
    """
    Retrieves Spotify streaming history from the specified directory.

    Parameters:
        path (str): The directory path where Spotify streaming history data files are located.

    Returns:
        List[dict]: A list of dictionaries containing streaming history data.
    """

    # List all files in the specified directory with the correct naming scheme
    files = [f'{path}/{x}' for x in listdir(path) if x.startswith('Streaming_History_Audio_')]

    all_streamings = []

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            new_streamings = json.load(f)
            all_streamings += new_streamings

    return all_streamings


# In[ ]:


# Title: minsec_to_seconds

# Description:
# Parses a time string in "minutes:seconds" format, 
# converts it to total seconds as an integer, 
# and returns 0 if the input is invalid or an error occurs during parsing.


# In[24]:


def minsec_to_seconds(time_str):
    try:
        minutes, seconds = map(int, time_str.split(":"))
        return minutes * 60 + seconds
    except:
        return 0


# In[ ]:


# Title: format_time

# Description:
# Takes an integer number of seconds, 
# converts it into a "minutes:seconds" string format (MM:SS), 
# and ensures the seconds portion is zero-padded to two digits.


# In[25]:


def format_time(seconds):
    return f"{seconds // 60}:{seconds % 60:02d}"


# In[ ]:


# Title: generate_top_10_songs_by_year

# Description:
# Defines Spotify Wrapped cutoff dates from 2017 to 2024, 
# filters streaming data for each year based on those cutoffs, 
# groups tracks by name, artist, album, and URI to preserve metadata, 
# aggregates play counts and listening duration, 
# ranks the top 10 songs by play count per year, 
# formats listening time as MM:SS, 
# and returns a dictionary mapping each year to its corresponding top 10 songs DataFrame.


# In[26]:


def generate_top_10_songs_by_year(streaming_data):
    import pandas as pd

    wrapped_end_dates = {
        2017: "2017-10-31T23:59:59Z",
        2018: "2018-10-31T23:59:59Z",
        2019: "2019-10-31T23:59:59Z",
        2020: "2020-11-15T23:59:59Z",
        2021: "2021-11-15T23:59:59Z",
        2022: "2022-11-15T23:59:59Z",
        2023: "2023-11-15T23:59:59Z",
        2024: "2024-11-15T23:59:59Z"
    }

    streaming_data['ts'] = pd.to_datetime(streaming_data['ts'])
    top_10_songs_by_year = {}

    for year, end_str in wrapped_end_dates.items():
        print(f"Processing Wrapped {year}...")

        start = pd.Timestamp(f"{year}-01-01T00:00:00Z")
        end = pd.Timestamp(end_str)

        year_data = streaming_data[
            (streaming_data['ts'] >= start) & (streaming_data['ts'] <= end)
        ]

        if year_data.empty:
            top_10_songs_by_year[year] = pd.DataFrame()
            continue

        # Group by full identity of a track to keep metadata
        top_songs = (
            year_data
            .groupby([
                'master_metadata_track_name',
                'master_metadata_album_artist_name',
                'master_metadata_album_album_name',
                'spotify_track_uri'
            ])
            .agg({
                'ts': 'count',
                'ms_played': 'sum'
            })
            .reset_index()
            .rename(columns={'ts': 'play_count'})
            .sort_values(by='play_count', ascending=False)
            .head(10)
        )

        # Add formatted listening length
        top_songs['listening_length'] = top_songs['ms_played'].apply(
            lambda ms: f"{int(ms // 60000)}:{int((ms % 60000) // 1000):02d}"
        )

        top_10_songs_by_year[year] = top_songs

    return top_10_songs_by_year


# In[ ]:


# Title: save_cache

# Description:
# Writes the in-memory `cache` dictionary to a JSON file defined by `CACHE_FILE`, 
# using indentation for readability, to preserve updated artist-genre mappings for future use.


# In[ ]:


def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)


# In[ ]:


# Title: search_track_id

# Description:
# Constructs a search query using the provided artist and track name, 
# queries the Spotify API for matching tracks, 
# returns the Spotify track ID if a result is found, 
# and handles errors gracefully by printing the exception and returning `None`.


# In[28]:


def search_track_id(artist, track):
    try:
        query = f"artist:{artist} track:{track}"
        result = sp.search(q=query, type='track', limit=1)
        items = result['tracks']['items']
        if items:
            return items[0]['id']
        else:
            return None
    except Exception as e:
        print(f"Error searching for {track} by {artist}: {e}")
        return None


# In[ ]:


# Title: get_audio_features

# Description:
# Checks if the audio features for a given Spotify track ID exist in the local cache, 
# queries the Spotify API if not cached, 
# stores the retrieved features in the cache and saves it to file, 
# and returns the feature data or `None` if the track is not found or an error occurs.


# In[29]:


def get_audio_features(track_id):
    try:
        if track_id in cache:
            return cache[track_id]

        features = sp.audio_features([track_id])
        if features and features[0]:
            cache[track_id] = features[0]
            save_cache()
            return features[0]
        else:
            return None
    except Exception as e:
        print(f"Error fetching features for track ID {track_id}: {e}")
        return None


# In[ ]:


# Title: load_wrapped_data

# Description:
# Reads a CSV file containing Spotify Wrapped streaming data, 
# filters out entries beyond the year 2024, 
# and returns the cleaned DataFrame for further analysis.


# In[ ]:


def load_wrapped_data(path):
    df = pd.read_csv(path)
    df = df[df['year'] <= 2024]
    return df


# In[ ]:


# Title: create_vibe_clusters

# Description:
# Applies KMeans clustering to four Spotify audio features—energy, danceability, valence, and tempo— 
# assigns each track a cluster label stored in a new column `vibe_cluster`, 
# and returns the DataFrame with the added cluster assignments.


# In[ ]:


def create_vibe_clusters(df):
    features = ['energy', 'danceability', 'valence', 'tempo']
    kmeans = KMeans(n_clusters=4, random_state=42)
    df['vibe_cluster'] = kmeans.fit_predict(df[features])
    return df


# In[ ]:


# Title: get_feature_trend

# Description:
# Groups the input DataFrame by year and calculates the average of a selected audio feature, 
# then creates a Plotly line chart with markers showing how that feature changes over time, 
# and returns the resulting figure for display or embedding in a dashboard.


# In[32]:


def generate_feature_trend(df, selected_feature):
    trend = df.groupby('year')[selected_feature].mean().reset_index()
    fig = px.line(trend, x='year', y=selected_feature, markers=True, 
                  title=f"Average {selected_feature.capitalize()} Over Time")
    return fig


# In[ ]:


# Title: generate_top_10_table

# Description:
# Sorts the DataFrame in descending order based on a given audio feature, 
# selects the top 10 tracks, 
# extracts track name, artist name, and the selected feature value, 
# and returns the result as a list of dictionaries for easy use in interactive tables or dashboards.


# In[33]:


def generate_top_10_table(df, feature):
    top_10 = df.sort_values(by=feature, ascending=False).head(10)
    return top_10[[
        'master_metadata_track_name',
        'master_metadata_album_artist_name',
        feature
    ]].to_dict("records")


# In[ ]:


# Title: load_full_wrapped_data

# Description:
# Loads cleaned Spotify streaming history and audio feature metadata, 
# merges them by track name and artist, 
# maps artist genres using a preprocessed genre file (`top_genres_clean.json`), 
# extracts the primary genre from the list if applicable, 
# filters the data to include only entries through 2024, 
# and returns the fully enriched DataFrame for analysis or visualization.


# In[34]:


def load_full_wrapped_data():
    """
    Loads the full merged Spotify streaming data and Spotify features.
    Also maps genre info using the top_genres_clean.json file.
    """
    # Load data
    streaming_data = pd.read_csv('wrapped_data/streaming_data.csv')
    spotify_features = pd.read_csv('wrapped_data/SpotifyFeatures.csv')

    # Merge on track + artist
    merged = pd.merge(
        streaming_data,
        spotify_features,
        how='inner',
        left_on=['master_metadata_track_name', 'master_metadata_album_artist_name'],
        right_on=['track_name', 'artist_name']
    )

    # Load genre map
    with open('wrapped_data/top_genres_clean.json', 'r') as f:
        genre_map = json.load(f)

    # Map genres
    merged['genre'] = merged['master_metadata_album_artist_name'].map(genre_map)
    merged['genre'] = merged['genre'].apply(lambda g: g[0] if isinstance(g, list) else g)

    # Only keep data up to 2024
    merged = merged[merged['year'] <= 2024]

    return merged

