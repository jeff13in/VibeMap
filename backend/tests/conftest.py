"""
Shared fixtures for VibeMap test suite.
"""

import sys
import sqlite3
from pathlib import Path

import pytest
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path setup – make backend modules (data_cleaner, recommender, clustering)
# importable from any test file.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Sample DataFrames
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_df():
    """100-row DataFrame with all columns used by recommender & clusterer."""
    rng = np.random.RandomState(42)
    n = 100
    return pd.DataFrame({
        "track_id": [f"track_{i:03d}" for i in range(n)],
        "track_name": [f"Song {i}" for i in range(n)],
        "artist": [f"Artist {i % 10}" for i in range(n)],
        "album": [f"Album {i % 5}" for i in range(n)],
        "popularity": rng.randint(0, 100, n),
        "valence": rng.rand(n),
        "energy": rng.rand(n),
        "danceability": rng.rand(n),
        "tempo": rng.uniform(70, 180, n),
        "acousticness": rng.rand(n),
        "instrumentalness": rng.rand(n),
        "liveness": rng.rand(n),
        "speechiness": rng.rand(n),
        "loudness": rng.uniform(-30, -3, n),
    })


@pytest.fixture()
def small_df():
    """20-row DataFrame for quick tests."""
    rng = np.random.RandomState(99)
    n = 20
    return pd.DataFrame({
        "track_id": [f"t{i}" for i in range(n)],
        "track_name": [f"Track {i}" for i in range(n)],
        "artist": [f"Art {i % 4}" for i in range(n)],
        "album": [f"Alb {i % 3}" for i in range(n)],
        "popularity": rng.randint(0, 100, n),
        "valence": rng.rand(n),
        "energy": rng.rand(n),
        "danceability": rng.rand(n),
        "tempo": rng.uniform(70, 180, n),
        "acousticness": rng.rand(n),
        "instrumentalness": rng.rand(n),
        "liveness": rng.rand(n),
        "speechiness": rng.rand(n),
        "loudness": rng.uniform(-30, -3, n),
    })


# ---------------------------------------------------------------------------
# SQLite test database
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_db(tmp_path, sample_df):
    """Create a temporary SQLite DB with a raw_songs table.

    Returns the path to the .db file.
    """
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    sample_df.to_sql("raw_songs", conn, index=False, if_exists="replace")
    conn.close()
    return db_path


@pytest.fixture()
def dirty_db(tmp_path):
    """SQLite DB with intentional quality issues (nulls, duplicates, outliers)."""
    rng = np.random.RandomState(7)
    n = 50
    df = pd.DataFrame({
        "track_id": [f"id_{i}" for i in range(n)],
        "track_name": [f"Song {i}" for i in range(n)],
        "artist": [f"Artist {i % 5}" for i in range(n)],
        "popularity": rng.randint(0, 100, n),
        "valence": rng.rand(n),
        "energy": rng.rand(n),
        "danceability": rng.rand(n),
        "tempo": rng.uniform(70, 180, n),
        "acousticness": rng.rand(n),
        "instrumentalness": rng.rand(n),
        "liveness": rng.rand(n),
        "speechiness": rng.rand(n),
        "loudness": rng.uniform(-30, -3, n),
    })

    # Inject nulls
    df.loc[0, "artist"] = None
    df.loc[1, "tempo"] = None
    df.loc[2, "valence"] = None
    df.loc[3, "energy"] = None

    # Inject duplicates (copy rows 10-12)
    dups = df.iloc[10:13].copy()
    df = pd.concat([df, dups], ignore_index=True)

    # Inject outliers
    df.loc[4, "tempo"] = 10.0     # below 50
    df.loc[5, "tempo"] = 250.0    # above 200
    df.loc[6, "valence"] = -0.5   # below 0
    df.loc[7, "energy"] = 1.5     # above 1

    db_path = tmp_path / "dirty.db"
    conn = sqlite3.connect(db_path)
    df.to_sql("raw_songs", conn, index=False, if_exists="replace")
    conn.close()
    return db_path


# ---------------------------------------------------------------------------
# Recommender fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def recommender(sample_df):
    """Fully initialized SongRecommender ready for querying."""
    from recommender import SongRecommender

    rec = SongRecommender(n_recommendations=5)
    rec.df = sample_df.copy()
    rec.feature_names = [
        "valence", "energy", "danceability", "tempo",
        "acousticness", "instrumentalness", "liveness",
        "speechiness", "loudness",
    ]
    rec.df = rec.df.dropna(subset=rec.feature_names).reset_index(drop=True)

    rec.df["tempo_normalized"] = (
        (rec.df["tempo"] - rec.df["tempo"].min())
        / (rec.df["tempo"].max() - rec.df["tempo"].min())
    )
    rec.df["loudness_normalized"] = (
        (rec.df["loudness"] - rec.df["loudness"].min())
        / (rec.df["loudness"].max() - rec.df["loudness"].min())
    )

    feature_cols = [
        "valence", "energy", "danceability", "tempo_normalized",
        "acousticness", "instrumentalness", "liveness",
        "speechiness", "loudness_normalized",
    ]
    rec.feature_matrix = rec.df[feature_cols].values
    rec.feature_matrix_scaled = rec.scaler.fit_transform(rec.feature_matrix)
    rec.build_knn_model(n_neighbors=min(10, len(rec.df) - 1))
    return rec


# ---------------------------------------------------------------------------
# Clusterer fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def clusterer():
    """Bare MoodClusterer (not yet fitted)."""
    from clustering import MoodClusterer
    return MoodClusterer(n_clusters=5, random_state=42)
