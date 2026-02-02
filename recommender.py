"""
Song Recommender Module
Content-based and similarity-based song recommendations

Similarity methods:
    1. K-Nearest Neighbors (KNN) - cosine distance
    2. Cosine Similarity - sklearn pairwise
    3. Euclidean Distance - scipy spatial
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cdist
from pathlib import Path
import joblib

# Configuration
DATA_DIR = Path(__file__).parent.parent / 'data'
MODEL_DIR = Path(__file__).parent.parent / 'models'
MODEL_DIR.mkdir(exist_ok=True)


class SongRecommender:
    """Content-based song recommender using audio features.

    Supports three similarity methods:
        - KNN with cosine distance
        - Cosine similarity (sklearn pairwise)
        - Euclidean distance (scipy spatial)

    Four recommendation modes:
        - recommend_by_song()          : find similar songs
        - recommend_by_mood()           : filter by mood (8 moods)
        - recommend_by_tempo()          : filter by tempo (3 categories)
        - recommend_by_mood_and_tempo() : combined filtering
    """

    # 8 mood filters with min (>=) and max (<=) thresholds
    MOOD_FILTERS = {
        'happy':     {'valence': 0.6, 'energy': 0.5},
        'sad':       {'valence_max': 0.4, 'energy_max': 0.4},
        'energetic': {'energy': 0.7, 'danceability': 0.5},
        'calm':      {'energy_max': 0.4, 'acousticness': 0.5},
        'dark':      {'valence_max': 0.3, 'energy': 0.6},
        'romantic':  {'valence': 0.5, 'acousticness': 0.4, 'energy_max': 0.6},
        'angry':     {'energy': 0.7, 'valence_max': 0.4},
        'party':     {'danceability': 0.7, 'energy': 0.6, 'valence': 0.5},
    }

    # 3 tempo categories
    TEMPO_FILTERS = {
        'slow':   {'tempo_max': 100},
        'medium': {'tempo_min': 100, 'tempo_max': 120},
        'fast':   {'tempo_min': 120},
    }

    def __init__(self, n_recommendations=5):
        self.n_recommendations = n_recommendations
        self.scaler = StandardScaler()
        self.df = None
        self.feature_names = None
        self.feature_matrix = None
        self.feature_matrix_scaled = None
        self.knn_model = None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_mood_filter(self, mood):
        """Return a boolean mask over self.df for the given mood."""
        if mood not in self.MOOD_FILTERS:
            raise ValueError(
                f"Unknown mood: '{mood}'. "
                f"Available moods: {list(self.MOOD_FILTERS.keys())}"
            )

        thresholds = self.MOOD_FILTERS[mood]
        mask = pd.Series(True, index=self.df.index)

        for key, value in thresholds.items():
            if key.endswith('_max'):
                col = key.replace('_max', '')
                mask &= self.df[col] <= value
            else:
                mask &= self.df[key] >= value

        return mask

    def _apply_tempo_filter(self, tempo_type):
        """Return a boolean mask over self.df for the given tempo type."""
        if tempo_type not in self.TEMPO_FILTERS:
            raise ValueError(
                f"Unknown tempo type: '{tempo_type}'. "
                f"Available types: {list(self.TEMPO_FILTERS.keys())}"
            )

        thresholds = self.TEMPO_FILTERS[tempo_type]
        mask = pd.Series(True, index=self.df.index)

        if 'tempo_min' in thresholds:
            mask &= self.df['tempo'] >= thresholds['tempo_min']
        if 'tempo_max' in thresholds:
            mask &= self.df['tempo'] <= thresholds['tempo_max']

        return mask

    # ------------------------------------------------------------------
    # Model building
    # ------------------------------------------------------------------

    def build_knn_model(self, n_neighbors=10):
        """Fit a KNN model on the scaled feature matrix using cosine distance."""
        self.knn_model = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric='cosine',
            algorithm='brute',   # brute required for cosine metric
        )
        self.knn_model.fit(self.feature_matrix_scaled)

    # ------------------------------------------------------------------
    # Recommendation modes
    # ------------------------------------------------------------------

    def recommend_by_mood(self, mood, n_songs=5):
        """Filter songs by mood thresholds and return top results."""
        mask = self._apply_mood_filter(mood)
        return self.df[mask].head(n_songs)

    def recommend_by_tempo(self, tempo_type, n_songs=5):
        """Filter songs by tempo thresholds and return top results."""
        mask = self._apply_tempo_filter(tempo_type)
        return self.df[mask].head(n_songs)

    def recommend_by_mood_and_tempo(self, mood, tempo, n_songs=5):
        """Combine mood and tempo filters and return top results."""
        mood_mask = self._apply_mood_filter(mood)
        tempo_mask = self._apply_tempo_filter(tempo)
        return self.df[mood_mask & tempo_mask].head(n_songs)

    def recommend_by_song(self, song_id, method='knn'):
        """Find similar songs using the specified method.

        Args:
            song_id: track_id of the seed song
            method:
                'knn'       - K-Nearest Neighbors with cosine distance
                'cosine'    - sklearn pairwise cosine similarity
                'euclidean' - scipy spatial euclidean distance

        Returns:
            DataFrame (<= n_recommendations rows) with a similarity_score
            column normalized to [0, 1].
        """
        idx = self.df.index[self.df['track_id'] == song_id].tolist()
        if not idx:
            raise ValueError(f"Song ID '{song_id}' not found in dataset")
        idx = idx[0]

        song_vector = self.feature_matrix_scaled[idx].reshape(1, -1)

        if method == 'knn':
            # KNN with cosine distance
            distances, indices = self.knn_model.kneighbors(song_vector)
            neighbor_indices = indices[0][1:]      # exclude the song itself
            neighbor_distances = distances[0][1:]
            result = self.df.iloc[neighbor_indices].copy()
            # cosine distance is in [0, 2]; convert to similarity in [0, 1]
            result['similarity_score'] = 1 - (neighbor_distances / 2)

        elif method == 'cosine':
            # sklearn pairwise cosine similarity
            sim_matrix = cosine_similarity(song_vector, self.feature_matrix_scaled)[0]
            sim_matrix[idx] = -1  # exclude self
            top_indices = np.argsort(sim_matrix)[::-1][:self.n_recommendations]
            result = self.df.iloc[top_indices].copy()
            # cosine similarity is already in [-1, 1]; normalize to [0, 1]
            result['similarity_score'] = (sim_matrix[top_indices] + 1) / 2

        elif method == 'euclidean':
            # scipy spatial euclidean distance
            dist_matrix = cdist(song_vector, self.feature_matrix_scaled, metric='euclidean')[0]
            dist_matrix[idx] = np.inf  # exclude self
            top_indices = np.argsort(dist_matrix)[:self.n_recommendations]
            top_distances = dist_matrix[top_indices]
            result = self.df.iloc[top_indices].copy()
            max_dist = top_distances.max() if top_distances.max() > 0 else 1
            result['similarity_score'] = 1 - (top_distances / max_dist)

        else:
            raise ValueError(
                f"Unknown method: '{method}'. Use 'knn', 'cosine', or 'euclidean'."
            )

        return result.head(self.n_recommendations)

    # ------------------------------------------------------------------
    # Model persistence
    # ------------------------------------------------------------------

    def save_model(self, filename='song_recommender.pkl'):
        """Save the recommender model to disk."""
        model_path = MODEL_DIR / filename
        model_data = {
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'knn_model': self.knn_model,
            'n_recommendations': self.n_recommendations,
        }
        joblib.dump(model_data, model_path)
        print(f"Model saved to {model_path}")

    @classmethod
    def load_model(cls, filename='song_recommender.pkl'):
        """Load a recommender model from disk."""
        model_path = MODEL_DIR / filename
        model_data = joblib.load(model_path)
        rec = cls(n_recommendations=model_data['n_recommendations'])
        rec.scaler = model_data['scaler']
        rec.feature_names = model_data['feature_names']
        rec.knn_model = model_data['knn_model']
        print(f"Model loaded from {model_path}")
        return rec


def main():
    """Main execution: load data, build recommender, run demos, save model."""
    print("\nSONG RECOMMENDER")

    # Load processed data
    data_path = Path(__file__).parent.parent / 'cleaned_spotify_data.csv'
    df = pd.read_csv(data_path)

    # Rename id -> track_id if needed
    if 'id' in df.columns and 'track_id' not in df.columns:
        df = df.rename(columns={'id': 'track_id'})

    print(f"Loaded dataset: {df.shape}")

    # Initialize recommender
    rec = SongRecommender(n_recommendations=5)
    rec.df = df

    # Feature setup
    rec.feature_names = [
        'valence', 'energy', 'danceability', 'tempo',
        'acousticness', 'instrumentalness', 'liveness',
        'speechiness', 'loudness',
    ]

    # Drop rows with NaN in feature columns
    rec.df = rec.df.dropna(subset=rec.feature_names).reset_index(drop=True)
    print(f"After dropping NaN rows: {rec.df.shape}")

    # Normalize tempo and loudness to 0-1 range
    rec.df['tempo_normalized'] = (
        (rec.df['tempo'] - rec.df['tempo'].min()) /
        (rec.df['tempo'].max() - rec.df['tempo'].min())
    )
    rec.df['loudness_normalized'] = (
        (rec.df['loudness'] - rec.df['loudness'].min()) /
        (rec.df['loudness'].max() - rec.df['loudness'].min())
    )

    feature_cols = [
        'valence', 'energy', 'danceability', 'tempo_normalized',
        'acousticness', 'instrumentalness', 'liveness',
        'speechiness', 'loudness_normalized',
    ]

    rec.feature_matrix = rec.df[feature_cols].values
    rec.feature_matrix_scaled = rec.scaler.fit_transform(rec.feature_matrix)

    # Build KNN model (cosine distance)
    rec.build_knn_model(n_neighbors=10)

    # Demo: all 4 recommendation modes
    print("\n--- recommend_by_mood('party') ---")
    print(rec.recommend_by_mood('party', n_songs=5)[
        ['track_name', 'valence', 'energy']
    ].to_string())

    print("\n--- recommend_by_tempo('fast') ---")
    print(rec.recommend_by_tempo('fast', n_songs=5)[
        ['track_name', 'tempo']
    ].to_string())

    print("\n--- recommend_by_mood_and_tempo('party', 'fast') ---")
    print(rec.recommend_by_mood_and_tempo('party', 'fast', n_songs=5)[
        ['track_name', 'valence', 'energy', 'danceability', 'tempo']
    ].to_string())

    if len(rec.df) > 0:
        seed = rec.df.iloc[0]['track_id']
        seed_name = rec.df.iloc[0].get('track_name', seed)

        for method in ('knn', 'cosine', 'euclidean'):
            print(f"\n--- recommend_by_song('{seed_name}', method='{method}') ---")
            recs = rec.recommend_by_song(seed, method=method)
            print(recs[['track_name', 'similarity_score']].to_string())

    # Save model
    rec.save_model()
    print("\nRecommender complete!")

    return rec


if __name__ == "__main__":
    main()
