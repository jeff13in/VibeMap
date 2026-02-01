"""
Optional: Unit Tests for Data Generator
Only add this if you want comprehensive test coverage
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_generator import generate_spotify_dataset


class TestDataGenerator:
    """Tests for data generation module"""
    
    def test_generate_dataset_shape(self):
        """Test that dataset has correct shape"""
        df = generate_spotify_dataset(num_songs=100)
        
        assert df.shape[0] == 100  # Should have 100 rows
        assert df.shape[1] >= 12   # Should have at least 12 columns
    
    def test_required_columns_exist(self):
        """Test that all required columns are present"""
        df = generate_spotify_dataset(num_songs=50)
        
        required_cols = [
            'track_id', 'track_name', 'artist_name', 'popularity',
            'valence', 'energy', 'danceability', 'tempo',
            'acousticness', 'instrumentalness', 'liveness', 'speechiness'
        ]
        
        for col in required_cols:
            assert col in df.columns, f"Missing required column: {col}"
    
    def test_audio_features_in_valid_range(self):
        """Test that audio features are in valid ranges"""
        df = generate_spotify_dataset(num_songs=100)
        
        # Features that should be 0-1
        features_0_1 = ['valence', 'energy', 'danceability', 
                        'acousticness', 'instrumentalness', 
                        'liveness', 'speechiness']
        
        for feature in features_0_1:
            # Allow some outliers since we intentionally add them
            valid_ratio = (df[feature].between(0, 1)).sum() / len(df)
            assert valid_ratio > 0.9, f"{feature} has too many values outside 0-1 range"
    
    def test_tempo_in_valid_range(self):
        """Test that tempo is in valid range"""
        df = generate_spotify_dataset(num_songs=100)
        
        # Most tempos should be between 50-200, allowing for outliers
        valid_ratio = (df['tempo'].between(50, 200)).sum() / len(df)
        assert valid_ratio > 0.9, "Too many tempo values outside valid range"
    
    def test_unique_track_ids(self):
        """Test that track IDs are unique"""
        df = generate_spotify_dataset(num_songs=100)
        
        assert df['track_id'].nunique() == len(df), "Track IDs should be unique"
    
    def test_data_types(self):
        """Test that columns have correct data types"""
        df = generate_spotify_dataset(num_songs=50)
        
        # String columns
        assert df['track_id'].dtype == 'object'
        assert df['track_name'].dtype == 'object'
        assert df['artist_name'].dtype == 'object'
        
        # Numeric columns
        assert pd.api.types.is_numeric_dtype(df['valence'])
        assert pd.api.types.is_numeric_dtype(df['energy'])
        assert pd.api.types.is_numeric_dtype(df['tempo'])
        assert pd.api.types.is_numeric_dtype(df['popularity'])
    
    def test_missing_values_present(self):
        """Test that some missing values are intentionally added"""
        df = generate_spotify_dataset(num_songs=100)
        
        # Should have some nulls (we intentionally add ~5%)
        total_nulls = df.isnull().sum().sum()
        assert total_nulls > 0, "Should have some missing values for testing cleaning"
    
    def test_duplicates_present(self):
        """Test that some duplicates are intentionally added"""
        df = generate_spotify_dataset(num_songs=100)
        
        # Should have some duplicates
        assert df.duplicated().sum() > 0, "Should have some duplicates for testing cleaning"
    
    def test_reproducibility(self):
        """Test that same seed produces same data"""
        np.random.seed(42)
        df1 = generate_spotify_dataset(num_songs=50)
        
        np.random.seed(42)
        df2 = generate_spotify_dataset(num_songs=50)
        
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_configurable_size(self):
        """Test that dataset size is configurable"""
        sizes = [10, 50, 100, 500]
        
        for size in sizes:
            df = generate_spotify_dataset(num_songs=size)
            assert len(df) >= size, f"Dataset should have at least {size} songs"


if __name__ == "__main__":
    pytest.main([__file__, '-v'])