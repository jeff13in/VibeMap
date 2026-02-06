"""
Tests for MoodClusterer (clustering.py)
Covers: initialization, feature selection, fitting, cluster analysis,
        interpretation, model save/load, edge cases.
"""

import pytest
import numpy as np
import pandas as pd

from clustering import MoodClusterer


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestInit:

    def test_default_params(self):
        c = MoodClusterer()
        assert c.n_clusters == 5
        assert c.random_state == 42

    def test_custom_params(self):
        c = MoodClusterer(n_clusters=3, random_state=7)
        assert c.n_clusters == 3
        assert c.random_state == 7

    def test_scaler_initialized(self):
        c = MoodClusterer()
        assert c.scaler is not None

    def test_initial_kmeans_none(self):
        c = MoodClusterer()
        assert c.kmeans is None

    def test_default_cluster_labels(self):
        c = MoodClusterer()
        assert len(c.cluster_labels) == 5
        assert 0 in c.cluster_labels


# ---------------------------------------------------------------------------
# Feature selection
# ---------------------------------------------------------------------------

class TestSelectFeatures:

    def test_returns_matrix_and_df(self, sample_df, clusterer):
        X, df_feat = clusterer.select_features(sample_df)
        assert isinstance(X, np.ndarray)
        assert isinstance(df_feat, pd.DataFrame)

    def test_correct_feature_count(self, sample_df, clusterer):
        X, _ = clusterer.select_features(sample_df)
        # 5 features: valence, energy, danceability, tempo_normalized, acousticness
        assert X.shape[1] == 5

    def test_tempo_normalized_created(self, sample_df, clusterer):
        _, df_feat = clusterer.select_features(sample_df)
        assert "tempo_normalized" in df_feat.columns
        assert df_feat["tempo_normalized"].min() >= 0.0
        assert df_feat["tempo_normalized"].max() <= 1.0

    def test_row_count_preserved(self, sample_df, clusterer):
        X, df_feat = clusterer.select_features(sample_df)
        assert X.shape[0] == len(df_feat)

    def test_drops_nan_rows(self, sample_df, clusterer):
        df = sample_df.copy()
        df.loc[0, "valence"] = np.nan
        df.loc[1, "energy"] = np.nan
        _, df_feat = clusterer.select_features(df)
        assert len(df_feat) == len(sample_df) - 2

    def test_feature_names_stored(self, sample_df, clusterer):
        clusterer.select_features(sample_df)
        assert clusterer.feature_names is not None
        assert "valence" in clusterer.feature_names


# ---------------------------------------------------------------------------
# Fit
# ---------------------------------------------------------------------------

class TestFit:

    def test_returns_clustered_df_and_scaled(self, sample_df, clusterer):
        df_c, X_s = clusterer.fit(sample_df, auto_optimize=False)
        assert isinstance(df_c, pd.DataFrame)
        assert isinstance(X_s, np.ndarray)

    def test_cluster_column_added(self, sample_df, clusterer):
        df_c, _ = clusterer.fit(sample_df, auto_optimize=False)
        assert "cluster" in df_c.columns

    def test_cluster_count(self, sample_df, clusterer):
        df_c, _ = clusterer.fit(sample_df, auto_optimize=False)
        assert df_c["cluster"].nunique() <= clusterer.n_clusters

    def test_all_rows_assigned(self, sample_df, clusterer):
        df_c, _ = clusterer.fit(sample_df, auto_optimize=False)
        assert df_c["cluster"].isna().sum() == 0

    def test_kmeans_fitted(self, sample_df, clusterer):
        clusterer.fit(sample_df, auto_optimize=False)
        assert clusterer.kmeans is not None

    def test_different_n_clusters(self, sample_df):
        c = MoodClusterer(n_clusters=3, random_state=42)
        df_c, _ = c.fit(sample_df, auto_optimize=False)
        assert df_c["cluster"].nunique() <= 3

    def test_reproducible(self, sample_df):
        c1 = MoodClusterer(n_clusters=5, random_state=42)
        c2 = MoodClusterer(n_clusters=5, random_state=42)
        df1, _ = c1.fit(sample_df, auto_optimize=False)
        df2, _ = c2.fit(sample_df, auto_optimize=False)
        pd.testing.assert_series_equal(
            df1["cluster"].reset_index(drop=True),
            df2["cluster"].reset_index(drop=True),
        )


# ---------------------------------------------------------------------------
# Cluster analysis
# ---------------------------------------------------------------------------

class TestAnalyzeClusters:

    def test_returns_means_dataframe(self, sample_df, clusterer):
        df_c, _ = clusterer.fit(sample_df, auto_optimize=False)
        means = clusterer.analyze_clusters(df_c)
        assert isinstance(means, pd.DataFrame)

    def test_means_have_expected_columns(self, sample_df, clusterer):
        df_c, _ = clusterer.fit(sample_df, auto_optimize=False)
        means = clusterer.analyze_clusters(df_c)
        for col in ["valence", "energy", "danceability", "tempo", "acousticness"]:
            assert col in means.columns

    def test_labels_updated(self, sample_df, clusterer):
        df_c, _ = clusterer.fit(sample_df, auto_optimize=False)
        clusterer.analyze_clusters(df_c)
        # Every cluster ID should have a label
        for cid in df_c["cluster"].unique():
            assert cid in clusterer.cluster_labels


# ---------------------------------------------------------------------------
# Interpret cluster
# ---------------------------------------------------------------------------

class TestInterpretCluster:

    @pytest.fixture()
    def interp(self):
        return MoodClusterer()

    def test_energetic_happy(self, interp):
        feat = pd.Series({"valence": 0.8, "energy": 0.8, "danceability": 0.8, "tempo": 130, "acousticness": 0.2})
        assert interp._interpret_cluster(feat) == "Energetic & Happy"

    def test_intense_dark(self, interp):
        feat = pd.Series({"valence": 0.2, "energy": 0.8, "danceability": 0.5, "tempo": 140, "acousticness": 0.2})
        assert interp._interpret_cluster(feat) == "Intense & Dark"

    def test_calm_peaceful(self, interp):
        feat = pd.Series({"valence": 0.8, "energy": 0.2, "danceability": 0.3, "tempo": 80, "acousticness": 0.3})
        assert interp._interpret_cluster(feat) == "Calm & Peaceful"

    def test_melancholic(self, interp):
        feat = pd.Series({"valence": 0.2, "energy": 0.2, "danceability": 0.3, "tempo": 80, "acousticness": 0.3})
        assert interp._interpret_cluster(feat) == "Melancholic"

    def test_party_dance(self, interp):
        feat = pd.Series({"valence": 0.5, "energy": 0.5, "danceability": 0.9, "tempo": 120, "acousticness": 0.3})
        assert interp._interpret_cluster(feat) == "Party & Dance"

    def test_acoustic_mellow(self, interp):
        feat = pd.Series({"valence": 0.5, "energy": 0.5, "danceability": 0.5, "tempo": 110, "acousticness": 0.8})
        assert interp._interpret_cluster(feat) == "Acoustic & Mellow"

    def test_balanced_fallback(self, interp):
        feat = pd.Series({"valence": 0.5, "energy": 0.5, "danceability": 0.5, "tempo": 110, "acousticness": 0.3})
        assert interp._interpret_cluster(feat) == "Balanced & Versatile"


# ---------------------------------------------------------------------------
# Model persistence
# ---------------------------------------------------------------------------

class TestModelPersistence:

    def test_save_and_load(self, sample_df, clusterer, tmp_path):
        import clustering as clust_module
        original = clust_module.MODEL_DIR
        clust_module.MODEL_DIR = tmp_path
        try:
            clusterer.fit(sample_df, auto_optimize=False)
            clusterer.save_model("test_clusterer.pkl")
            loaded = MoodClusterer.load_model("test_clusterer.pkl")
            assert loaded.n_clusters == clusterer.n_clusters
            assert loaded.feature_names == clusterer.feature_names
            assert loaded.kmeans is not None
            assert loaded.cluster_labels == clusterer.cluster_labels
        finally:
            clust_module.MODEL_DIR = original


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_small_dataset(self):
        """Fit with fewer rows than clusters should still work (k adjusted internally)."""
        rng = np.random.RandomState(0)
        df = pd.DataFrame({
            "valence": rng.rand(8),
            "energy": rng.rand(8),
            "danceability": rng.rand(8),
            "tempo": rng.uniform(80, 160, 8),
            "acousticness": rng.rand(8),
        })
        c = MoodClusterer(n_clusters=3, random_state=42)
        df_c, _ = c.fit(df, auto_optimize=False)
        assert "cluster" in df_c.columns

    def test_near_uniform_data(self):
        """Very similar rows should still cluster without error."""
        rng = np.random.RandomState(0)
        n = 30
        df = pd.DataFrame({
            "valence": 0.5 + rng.normal(0, 0.001, n),
            "energy": 0.5 + rng.normal(0, 0.001, n),
            "danceability": 0.5 + rng.normal(0, 0.001, n),
            "tempo": 120.0 + rng.normal(0, 0.1, n),
            "acousticness": 0.5 + rng.normal(0, 0.001, n),
        })
        c = MoodClusterer(n_clusters=3, random_state=42)
        df_c, _ = c.fit(df, auto_optimize=False)
        assert "cluster" in df_c.columns


# ---------------------------------------------------------------------------
# find_optimal_clusters & auto_optimize
# ---------------------------------------------------------------------------

class TestFindOptimalClusters:

    def test_returns_optimal_k(self, sample_df, clusterer):
        import matplotlib
        matplotlib.use("Agg")
        X, _ = clusterer.select_features(sample_df)
        X_scaled = clusterer.scaler.fit_transform(X)
        optimal_k = clusterer.find_optimal_clusters(X_scaled, max_clusters=4)
        assert isinstance(optimal_k, (int, np.integer))
        assert 2 <= optimal_k <= 4

    def test_auto_optimize_in_fit(self, sample_df):
        import matplotlib
        matplotlib.use("Agg")
        c = MoodClusterer(n_clusters=5, random_state=42)
        df_c, _ = c.fit(sample_df, auto_optimize=True)
        assert "cluster" in df_c.columns
        assert c.n_clusters >= 2


# ---------------------------------------------------------------------------
# visualize_clusters
# ---------------------------------------------------------------------------

class TestVisualizeClusters:

    def test_runs_without_error(self, sample_df, clusterer):
        import matplotlib
        matplotlib.use("Agg")
        df_c, X_s = clusterer.fit(sample_df, auto_optimize=False)
        clusterer.analyze_clusters(df_c)
        clusterer.visualize_clusters(df_c, X_s)
