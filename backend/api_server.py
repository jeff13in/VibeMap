"""
VibeMap API Server
Flask REST API that bridges the React frontend to the SongRecommender backend.

Usage:
    python api_server.py
"""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

# ---------------------------------------------------------------------------
# Project root = folder containing api_server.py (your VibeMap root)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# Your recommender is in ROOT: recommender.py
from recommender import SongRecommender  # noqa: E402

app = Flask(__name__)
CORS(app, origins=os.environ.get("CORS_ORIGINS", "*").split(","))

# ---------------------------------------------------------------------------
# Data loading from SQLite database
# ---------------------------------------------------------------------------
DB_PATH = PROJECT_ROOT / "spotify_data.db"


def init_recommender() -> SongRecommender:
    """Load data from SQLite database and initialize the SongRecommender."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at: {DB_PATH}\n"
            f"Expected spotify_data.db in the project root: {PROJECT_ROOT}"
        )

    conn = sqlite3.connect(str(DB_PATH))
    try:
        df = pd.read_sql_query("SELECT * FROM cleaned_songs", conn)
    finally:
        conn.close()

    # Map 'id' -> 'track_id' to match SongRecommender expectations
    if "id" in df.columns and "track_id" not in df.columns:
        df = df.rename(columns={"id": "track_id"})

    rec = SongRecommender(n_recommendations=50)
    rec.df = df.copy()

    rec.feature_names = [
        "valence", "energy", "danceability", "tempo",
        "acousticness", "instrumentalness", "liveness",
        "speechiness", "loudness",
    ]
    rec.df = rec.df.dropna(subset=rec.feature_names).reset_index(drop=True)

    # Normalize safely
    tempo_range = rec.df["tempo"].max() - rec.df["tempo"].min()
    loud_range = rec.df["loudness"].max() - rec.df["loudness"].min()

    rec.df["tempo_normalized"] = (
        (rec.df["tempo"] - rec.df["tempo"].min()) / (tempo_range if tempo_range != 0 else 1.0)
    )
    rec.df["loudness_normalized"] = (
        (rec.df["loudness"] - rec.df["loudness"].min()) / (loud_range if loud_range != 0 else 1.0)
    )

    feature_cols = [
        "valence", "energy", "danceability", "tempo_normalized",
        "acousticness", "instrumentalness", "liveness",
        "speechiness", "loudness_normalized",
    ]

    rec.feature_matrix = rec.df[feature_cols].values
    rec.feature_matrix_scaled = rec.scaler.fit_transform(rec.feature_matrix)

    if len(rec.df) >= 2:
        rec.build_knn_model(n_neighbors=min(50, len(rec.df) - 1))

    return rec


rec = init_recommender()
print(f"✅ API Server initialized: {len(rec.df)} songs loaded from {DB_PATH.name}")


# ---------------------------------------------------------------------------
# Helper: convert DataFrame rows to JSON-friendly dicts
# ---------------------------------------------------------------------------
SONG_FIELDS = [
    "track_id", "track_name", "artist", "album", "popularity",
    "valence", "energy", "danceability", "tempo",
    "acousticness", "instrumentalness", "liveness",
    "speechiness", "loudness", "spotify_url",
]

OPTIONAL_FIELDS = ["similarity_score", "mood_score", "cluster", "year", "release_date"]


def df_to_songs(df: pd.DataFrame) -> list[dict]:
    songs: list[dict] = []
    for _, row in df.iterrows():
        song: dict = {}

        for field in SONG_FIELDS:
            if field in row.index:
                val = row[field]
                song[field] = None if pd.isna(val) else val

        for field in OPTIONAL_FIELDS:
            if field in row.index:
                val = row[field]
                if not pd.isna(val):
                    song[field] = val

        songs.append(song)

    return songs


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
@app.route("/health")
def health():
    return jsonify({"status": "healthy", "songs_loaded": len(rec.df)})


@app.route("/api/moods")
def get_moods():
    return jsonify({"moods": list(rec.MOOD_FILTERS.keys())})


@app.route("/api/tempos")
def get_tempos():
    return jsonify({"tempos": list(rec.TEMPO_FILTERS.keys())})


@app.route("/api/recommendations/mood")
def recommend_by_mood():
    mood = request.args.get("mood")
    count = request.args.get("count", 10, type=int)

    if not mood:
        return jsonify({"success": False, "error": "Missing 'mood' parameter"}), 400
    if mood not in rec.MOOD_FILTERS:
        return jsonify({
            "success": False,
            "error": f"Unknown mood: '{mood}'. Available: {list(rec.MOOD_FILTERS.keys())}",
        }), 400

    results = rec.recommend_by_mood(mood, n_songs=count)
    return jsonify({
        "success": True,
        "count": len(results),
        "filters": {"mood": mood, "count": count},
        "recommendations": df_to_songs(results),
    })


@app.route("/api/recommendations/tempo")
def recommend_by_tempo():
    tempo = request.args.get("tempo")
    count = request.args.get("count", 10, type=int)

    if not tempo:
        return jsonify({"success": False, "error": "Missing 'tempo' parameter"}), 400
    if tempo not in rec.TEMPO_FILTERS:
        return jsonify({
            "success": False,
            "error": f"Unknown tempo: '{tempo}'. Available: {list(rec.TEMPO_FILTERS.keys())}",
        }), 400

    results = rec.recommend_by_tempo(tempo, n_songs=count)
    return jsonify({
        "success": True,
        "count": len(results),
        "filters": {"tempo": tempo, "count": count},
        "recommendations": df_to_songs(results),
    })


@app.route("/api/recommendations/combined")
def recommend_combined():
    mood = request.args.get("mood")
    tempo = request.args.get("tempo")
    count = request.args.get("count", 10, type=int)

    if not mood or not tempo:
        return jsonify({"success": False, "error": "Missing 'mood' and/or 'tempo' parameter"}), 400
    if mood not in rec.MOOD_FILTERS:
        return jsonify({"success": False, "error": f"Unknown mood: '{mood}'"}), 400
    if tempo not in rec.TEMPO_FILTERS:
        return jsonify({"success": False, "error": f"Unknown tempo: '{tempo}'"}), 400

    results = rec.recommend_by_mood_and_tempo(mood, tempo, n_songs=count)
    return jsonify({
        "success": True,
        "count": len(results),
        "filters": {"mood": mood, "tempo": tempo, "count": count},
        "recommendations": df_to_songs(results),
    })


@app.route("/api/recommendations/similar")
def recommend_similar():
    song_id = request.args.get("song_id")
    method = request.args.get("method", "knn")
    count = request.args.get("count", 10, type=int)

    if not song_id:
        return jsonify({"success": False, "error": "Missing 'song_id' parameter"}), 400
    if method not in ("knn", "cosine", "euclidean"):
        return jsonify({"success": False, "error": f"Unknown method: '{method}'"}), 400

    old_n = rec.n_recommendations
    rec.n_recommendations = count
    try:
        results = rec.recommend_by_song(song_id, method=method)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    finally:
        rec.n_recommendations = old_n

    return jsonify({
        "success": True,
        "count": len(results),
        "filters": {"method": method, "count": count},
        "recommendations": df_to_songs(results),
    })


@app.route("/api/songs/search")
def search_songs():
    query = request.args.get("query", "")
    limit = request.args.get("limit", 20, type=int)

    if not query:
        return jsonify({"success": False, "error": "Missing 'query' parameter"}), 400

    mask = (
        rec.df["track_name"].str.contains(query, case=False, na=False)
        | rec.df["artist"].str.contains(query, case=False, na=False)
    )
    results = rec.df[mask].head(limit)

    return jsonify({
        "success": True,
        "query": query,
        "count": len(results),
        "results": df_to_songs(results),
    })


@app.route("/api/songs/<track_id>")
def get_song(track_id: str):
    match = rec.df[rec.df["track_id"] == track_id]
    if match.empty:
        return jsonify({"success": False, "error": f"Song '{track_id}' not found"}), 404

    return jsonify({"success": True, "song": df_to_songs(match.head(1))[0]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
