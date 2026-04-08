# Sonic Universe

A personal data project that turns nine years of Spotify listening history (2017–2026) into an interactive star map — where every track is a star, coloured by its audio personality.

---

## What it does

**Notebook 1 — Exploration (`01_exploration.ipynb`)**
- Loads and cleans raw Spotify Extended Streaming History JSON files
- Removes PII (`ip_addr`, `platform`) and filters out podcasts / audiobooks
- Engineers temporal features and visualises multi-year listening trends
- Surfaces top artists and tracks, skip behaviour, and listening session patterns
- Enriches the top songs with Spotify audio features (via `SpotifyFeatures.csv`)

**Notebook 2 — Clustering & Universe (`02_clustering.ipynb`)**
- Scales 7 audio features: `acousticness`, `danceability`, `energy`, `instrumentalness`, `liveness`, `speechiness`, `valence`
- Uses the elbow method + silhouette score to select the optimal number of clusters (K = 4)
- Runs K-Means to assign each track a cluster (audio personality)
- Reduces the 7-dimensional feature space to 2D and 3D with UMAP
- Renders interactive Plotly visualisations where:
  - **Position** → UMAP audio coordinates
  - **Colour** → cluster
  - **Size** → play count
  - **Hover** → track, artist, genre, key audio features

---

## Cluster Personalities

| Cluster | Tracks | Character |
|---------|--------|-----------|
| 0 | 410 | High energy, positive — the everyday indie-rock backbone |
| 1 | 214 | Acoustic, low energy, melancholic |
| 2 | 70 | Instrumental-heavy, less danceable |
| 3 | 30 | High danceability + speechiness — hip-hop / Latin pop |

---

## Outputs

| File | Description |
|------|-------------|
| `data/processed/sonic_universe_2d.html` | Interactive 2D star map |
| `data/processed/sonic_universe_3d.html` | Interactive 3D star map |
| `data/processed/top_songs_clustered.csv` | 724 songs with UMAP coords + cluster labels |
| `data/processed/fig_*.png` | Static charts from the EDA notebook |

Open the HTML files in any browser — no server required.

---

## Setup

```bash
# From the project root
bash setup.sh
```

This creates a `.venv` virtual environment, installs dependencies, and registers a Jupyter kernel named `sonic_universe`.

```bash
# Launch JupyterLab
source .venv/bin/activate && jupyter lab
```

Run notebooks in order: `01_exploration.ipynb` → `02_clustering.ipynb`.

---

## Requirements

- Python 3.9+
- pandas, numpy, matplotlib, seaborn, scipy
- scikit-learn, umap-learn
- plotly
- jupyterlab

See `requirements.txt` for pinned versions.

---

## Data

| File | Source |
|------|--------|
| `Streaming_History_Audio_*.json` | Spotify Extended Streaming History (personal data export) |
| `data/SpotifyFeatures.csv` | [Kaggle — Spotify Audio Features](https://www.kaggle.com/datasets/zaheenhamidani/ultimate-spotify-tracks-db) |

> Spotify data is personal and not included in this repository. Request your own at [spotify.com/account/privacy](https://www.spotify.com/account/privacy). Feature coverage depends on track overlap with the Kaggle dataset.
