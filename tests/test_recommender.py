"""
Unit Tests for Spotify Song Recommender
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from recommender import SongRecommender
from clustering import MoodClusterer


class TestSongRecommender:
    """Test cases for SongRecommender class"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample dataset for testing"""
        np.random.seed(42)
        data = {
            'track_id': [f'track_{i:03d}' for i in range(100)],
            'track_name': [f'Song {i}' for i in range(100)],
            'artist_name': [f'Artist {i % 10}' for i in range(100)],
            'valence': np.random.rand(100),
            'energy': np.random.rand(100),
            'danceability': np.random.rand(100),
            'tempo': np.random.uniform(80, 160, 100),
            'acousticness': np.random.rand(100),
            'instrumentalness': np.random.rand(100),
            'liveness': np.random.rand(100),
            'speechiness': np.random.rand(100),
            'loudness': np.random.uniform(-30, -5, 100),
            'popularity': np.random.randint(0, 100, 100),
            'year': np.random.choice(range(2015, 2024), 100),
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def recommender(self, sample_data, tmp_path):
        """Create recommender instance with sample data"""
        # Save sample data
        data_path = tmp_path / "test_data.csv"
        sample_data.to_csv(data_path, index=False)
        
        # Initialize recommender
        rec = SongRecommender(n_recommendations=5)
        rec.df = sample_data
        
        # Prepare features
        rec.feature_names = [
            'valence', 'energy', 'danceability', 'tempo',
            'acousticness', 'instrumentalness', 'liveness',
            'speechiness', 'loudness'
        ]
        
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
            'speechiness', 'loudness_normalized'
        ]
        
        rec.feature_matrix = rec.df[feature_cols].values
        from sklearn.preprocessing import StandardScaler
        rec.scaler = StandardScaler()
        rec.feature_matrix_scaled = rec.scaler.fit_transform(rec.feature_matrix)
        
        rec.build_knn_model(n_neighbors=10)
        
        return rec
    
    def test_initialization(self):
        """Test recommender initialization"""
        rec = SongRecommender(n_recommendations=10)
        assert rec.n_recommendations == 10
        assert rec.scaler is not None
    
    def test_recommend_by_mood(self, recommender):
        """Test mood-based recommendations"""
        recs = recommender.recommend_by_mood('happy', n_songs=5)
        
        assert len(recs) <= 5
        assert all(recs['valence'] >= 0.6)
        assert all(recs['energy'] >= 0.5)
    
    def test_recommend_by_tempo(self, recommender):
        """Test tempo-based recommendations"""
        recs = recommender.recommend_by_tempo('fast', n_songs=5)
        
        assert len(recs) <= 5
        assert all(recs['tempo'] >= 120)
    
    def test_recommend_by_song(self, recommender):
        """Test song similarity recommendations"""
        track_id = recommender.df.iloc[0]['track_id']
        recs = recommender.recommend_by_song(song_id=track_id, method='knn')
        
        assert len(recs) <= recommender.n_recommendations
        assert 'similarity_score' in recs.columns
    
    def test_recommend_by_mood_and_tempo(self, recommender):
        """Test combined mood and tempo recommendations"""
        recs = recommender.recommend_by_mood_and_tempo('energetic', 'fast', n_songs=5)
        
        assert len(recs) <= 5
        if len(recs) > 0:
            assert all(recs['energy'] >= 0.7)
            assert all(recs['tempo'] >= 120)
    
    def test_invalid_mood(self, recommender):
        """Test handling of invalid mood"""
        with pytest.raises(ValueError):
            recommender.recommend_by_mood('invalid_mood')
    
    def test_invalid_tempo(self, recommender):
        """Test handling of invalid tempo"""
        with pytest.raises(ValueError):
            recommender.recommend_by_tempo('invalid_tempo')
    
    def test_cosine_similarity(self, recommender):
        """Test cosine similarity method"""
        track_id = recommender.df.iloc[0]['track_id']
        recs = recommender.recommend_by_song(song_id=track_id, method='cosine')
        
        assert len(recs) > 0
        assert 'similarity_score' in recs.columns
    
    def test_euclidean_distance(self, recommender):
        """Test euclidean distance method"""
        track_id = recommender.df.iloc[0]['track_id']
        recs = recommender.recommend_by_song(song_id=track_id, method='euclidean')
        
        assert len(recs) > 0
        assert 'similarity_score' in recs.columns


class TestMoodClusterer:
    """Test cases for MoodClusterer class"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample dataset for testing"""
        np.random.seed(42)
        data = {
            'track_id': [f'track_{i:03d}' for i in range(100)],
            'track_name': [f'Song {i}' for i in range(100)],
            'artist_name': [f'Artist {i % 10}' for i in range(100)],
            'valence': np.random.rand(100),
            'energy': np.random.rand(100),
            'danceability': np.random.rand(100),
            'tempo': np.random.uniform(80, 160, 100),
            'acousticness': np.random.rand(100),
        }
        return pd.DataFrame(data)
    
    def test_initialization(self):
        """Test clusterer initialization"""
        clusterer = MoodClusterer(n_clusters=5)
        assert clusterer.n_clusters == 5
        assert clusterer.scaler is not None
    
    def test_feature_selection(self, sample_data):
        """Test feature selection"""
        clusterer = MoodClusterer(n_clusters=5)
        X, df_features = clusterer.select_features(sample_data)
        
        assert X.shape[0] == len(sample_data)
        assert len(clusterer.feature_names) > 0
    
    def test_fit(self, sample_data):
        """Test clustering fit"""
        clusterer = MoodClusterer(n_clusters=3)
        df_clustered, X_scaled = clusterer.fit(sample_data)
        
        assert 'cluster' in df_clustered.columns
        assert len(df_clustered['cluster'].unique()) <= 3


def test_data_quality():
    """Test data quality checks"""
    np.random.seed(42)
    data = {
        'valence': np.random.rand(100),
        'energy': np.random.rand(100),
        'tempo': np.random.uniform(60, 180, 100),
    }
    df = pd.DataFrame(data)
    
    # Check ranges
    assert all(df['valence'].between(0, 1))
    assert all(df['energy'].between(0, 1))
    assert all(df['tempo'].between(50, 200))


if __name__ == "__main__":
    pytest.main([__file__, '-v'])