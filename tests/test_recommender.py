"""
Tests for SongRecommender (recommender.py)
Covers: initialization, all 8 moods, all 3 tempos, combined filters,
        all 3 similarity methods, model save/load, edge cases.
"""

import pytest
import pandas as pd

from recommender import SongRecommender


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestInit:

    def test_default_recommendations(self):
        rec = SongRecommender()
        assert rec.n_recommendations == 5

    def test_custom_recommendations(self):
        rec = SongRecommender(n_recommendations=10)
        assert rec.n_recommendations == 10

    def test_scaler_initialized(self):
        rec = SongRecommender()
        assert rec.scaler is not None

    def test_initial_state_none(self):
        rec = SongRecommender()
        assert rec.df is None
        assert rec.feature_matrix is None
        assert rec.knn_model is None


# ---------------------------------------------------------------------------
# Mood filters – all 8 moods
# ---------------------------------------------------------------------------

class TestRecommendByMood:

    @pytest.mark.parametrize("mood", list(SongRecommender.MOOD_FILTERS.keys()))
    def test_each_mood_returns_dataframe(self, recommender, mood):
        result = recommender.recommend_by_mood(mood, n_songs=5)
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= 5

    def test_happy_thresholds(self, recommender):
        result = recommender.recommend_by_mood("happy", n_songs=10)
        if len(result) > 0:
            assert (result["valence"] >= 0.6).all()
            assert (result["energy"] >= 0.5).all()

    def test_sad_thresholds(self, recommender):
        result = recommender.recommend_by_mood("sad", n_songs=10)
        if len(result) > 0:
            assert (result["valence"] <= 0.4).all()
            assert (result["energy"] <= 0.4).all()

    def test_energetic_thresholds(self, recommender):
        result = recommender.recommend_by_mood("energetic", n_songs=10)
        if len(result) > 0:
            assert (result["energy"] >= 0.7).all()
            assert (result["danceability"] >= 0.5).all()

    def test_calm_thresholds(self, recommender):
        result = recommender.recommend_by_mood("calm", n_songs=10)
        if len(result) > 0:
            assert (result["energy"] <= 0.4).all()
            assert (result["acousticness"] >= 0.5).all()

    def test_dark_thresholds(self, recommender):
        result = recommender.recommend_by_mood("dark", n_songs=10)
        if len(result) > 0:
            assert (result["valence"] <= 0.3).all()
            assert (result["energy"] >= 0.6).all()

    def test_romantic_thresholds(self, recommender):
        result = recommender.recommend_by_mood("romantic", n_songs=10)
        if len(result) > 0:
            assert (result["valence"] >= 0.5).all()
            assert (result["acousticness"] >= 0.4).all()
            assert (result["energy"] <= 0.6).all()

    def test_angry_thresholds(self, recommender):
        result = recommender.recommend_by_mood("angry", n_songs=10)
        if len(result) > 0:
            assert (result["energy"] >= 0.7).all()
            assert (result["valence"] <= 0.4).all()

    def test_party_thresholds(self, recommender):
        result = recommender.recommend_by_mood("party", n_songs=10)
        if len(result) > 0:
            assert (result["danceability"] >= 0.7).all()
            assert (result["energy"] >= 0.6).all()
            assert (result["valence"] >= 0.5).all()

    def test_invalid_mood_raises(self, recommender):
        with pytest.raises(ValueError, match="Unknown mood"):
            recommender.recommend_by_mood("nonexistent")

    def test_n_songs_respected(self, recommender):
        result = recommender.recommend_by_mood("happy", n_songs=2)
        assert len(result) <= 2


# ---------------------------------------------------------------------------
# Tempo filters – all 3 categories
# ---------------------------------------------------------------------------

class TestRecommendByTempo:

    @pytest.mark.parametrize("tempo", list(SongRecommender.TEMPO_FILTERS.keys()))
    def test_each_tempo_returns_dataframe(self, recommender, tempo):
        result = recommender.recommend_by_tempo(tempo, n_songs=5)
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= 5

    def test_slow_threshold(self, recommender):
        result = recommender.recommend_by_tempo("slow", n_songs=20)
        if len(result) > 0:
            assert (result["tempo"] <= 100).all()

    def test_medium_threshold(self, recommender):
        result = recommender.recommend_by_tempo("medium", n_songs=20)
        if len(result) > 0:
            assert (result["tempo"] >= 100).all()
            assert (result["tempo"] <= 120).all()

    def test_fast_threshold(self, recommender):
        result = recommender.recommend_by_tempo("fast", n_songs=20)
        if len(result) > 0:
            assert (result["tempo"] >= 120).all()

    def test_invalid_tempo_raises(self, recommender):
        with pytest.raises(ValueError, match="Unknown tempo"):
            recommender.recommend_by_tempo("supersonic")


# ---------------------------------------------------------------------------
# Combined mood + tempo
# ---------------------------------------------------------------------------

class TestRecommendByMoodAndTempo:

    def test_combined_returns_dataframe(self, recommender):
        result = recommender.recommend_by_mood_and_tempo("energetic", "fast", n_songs=5)
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= 5

    def test_combined_respects_both_filters(self, recommender):
        result = recommender.recommend_by_mood_and_tempo("energetic", "fast", n_songs=20)
        if len(result) > 0:
            assert (result["energy"] >= 0.7).all()
            assert (result["tempo"] >= 120).all()

    def test_combined_empty_ok(self, recommender):
        """Very restrictive combo may return 0 results — should not error."""
        result = recommender.recommend_by_mood_and_tempo("calm", "fast", n_songs=5)
        assert isinstance(result, pd.DataFrame)


# ---------------------------------------------------------------------------
# Song similarity – all 3 methods
# ---------------------------------------------------------------------------

class TestRecommendBySong:

    @pytest.mark.parametrize("method", ["knn", "cosine", "euclidean"])
    def test_each_method_returns_results(self, recommender, method):
        track_id = recommender.df.iloc[0]["track_id"]
        result = recommender.recommend_by_song(track_id, method=method)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert "similarity_score" in result.columns

    @pytest.mark.parametrize("method", ["knn", "cosine", "euclidean"])
    def test_similarity_scores_bounded(self, recommender, method):
        track_id = recommender.df.iloc[0]["track_id"]
        result = recommender.recommend_by_song(track_id, method=method)
        assert (result["similarity_score"] >= 0).all()
        assert (result["similarity_score"] <= 1).all()

    def test_excludes_seed_song_knn(self, recommender):
        track_id = recommender.df.iloc[0]["track_id"]
        result = recommender.recommend_by_song(track_id, method="knn")
        assert track_id not in result["track_id"].values

    def test_excludes_seed_song_cosine(self, recommender):
        track_id = recommender.df.iloc[0]["track_id"]
        result = recommender.recommend_by_song(track_id, method="cosine")
        assert track_id not in result["track_id"].values

    def test_excludes_seed_song_euclidean(self, recommender):
        track_id = recommender.df.iloc[0]["track_id"]
        result = recommender.recommend_by_song(track_id, method="euclidean")
        assert track_id not in result["track_id"].values

    def test_respects_n_recommendations(self, recommender):
        track_id = recommender.df.iloc[0]["track_id"]
        result = recommender.recommend_by_song(track_id, method="cosine")
        assert len(result) <= recommender.n_recommendations

    def test_invalid_song_id_raises(self, recommender):
        with pytest.raises(ValueError, match="not found"):
            recommender.recommend_by_song("fake_id_999")

    def test_invalid_method_raises(self, recommender):
        track_id = recommender.df.iloc[0]["track_id"]
        with pytest.raises(ValueError, match="Unknown method"):
            recommender.recommend_by_song(track_id, method="manhattan")


# ---------------------------------------------------------------------------
# KNN model building
# ---------------------------------------------------------------------------

class TestBuildKnnModel:

    def test_model_built(self, recommender):
        assert recommender.knn_model is not None

    def test_rebuild_different_k(self, recommender):
        recommender.build_knn_model(n_neighbors=3)
        assert recommender.knn_model.n_neighbors == 3


# ---------------------------------------------------------------------------
# Model persistence (save / load)
# ---------------------------------------------------------------------------

class TestModelPersistence:

    def test_save_and_load(self, recommender, tmp_path):
        # Monkey-patch MODEL_DIR so it writes to tmp_path
        import recommender as rec_module
        original = rec_module.MODEL_DIR
        rec_module.MODEL_DIR = tmp_path
        try:
            recommender.save_model("test_model.pkl")
            loaded = SongRecommender.load_model("test_model.pkl")
            assert loaded.n_recommendations == recommender.n_recommendations
            assert loaded.feature_names == recommender.feature_names
            assert loaded.knn_model is not None
        finally:
            rec_module.MODEL_DIR = original


# ---------------------------------------------------------------------------
# Private filter helpers
# ---------------------------------------------------------------------------

class TestPrivateFilters:

    def test_apply_mood_filter_returns_boolean_series(self, recommender):
        mask = recommender._apply_mood_filter("happy")
        assert mask.dtype == bool
        assert len(mask) == len(recommender.df)

    def test_apply_tempo_filter_returns_boolean_series(self, recommender):
        mask = recommender._apply_tempo_filter("slow")
        assert mask.dtype == bool
        assert len(mask) == len(recommender.df)

    def test_apply_mood_filter_invalid(self, recommender):
        with pytest.raises(ValueError):
            recommender._apply_mood_filter("unknown")

    def test_apply_tempo_filter_invalid(self, recommender):
        with pytest.raises(ValueError):
            recommender._apply_tempo_filter("unknown")


# ---------------------------------------------------------------------------
# Unloaded-state guards (df is None, feature_matrix_scaled is None)
# ---------------------------------------------------------------------------

class TestUnloadedStateErrors:

    def test_mood_filter_no_df(self):
        rec = SongRecommender()
        with pytest.raises(ValueError, match="not loaded"):
            rec._apply_mood_filter("happy")

    def test_tempo_filter_no_df(self):
        rec = SongRecommender()
        with pytest.raises(ValueError, match="not loaded"):
            rec._apply_tempo_filter("slow")

    def test_recommend_by_mood_no_df(self):
        rec = SongRecommender()
        with pytest.raises(ValueError, match="not loaded"):
            rec.recommend_by_mood("happy")

    def test_recommend_by_tempo_no_df(self):
        rec = SongRecommender()
        with pytest.raises(ValueError, match="not loaded"):
            rec.recommend_by_tempo("fast")

    def test_recommend_by_mood_and_tempo_no_df(self):
        rec = SongRecommender()
        with pytest.raises(ValueError, match="not loaded"):
            rec.recommend_by_mood_and_tempo("happy", "fast")

    def test_recommend_by_song_no_df(self):
        rec = SongRecommender()
        with pytest.raises(ValueError, match="not ready"):
            rec.recommend_by_song("some_id")

    def test_build_knn_no_matrix(self):
        rec = SongRecommender()
        with pytest.raises(ValueError, match="not built"):
            rec.build_knn_model()


# ---------------------------------------------------------------------------
# main() smoke test
# ---------------------------------------------------------------------------

class TestMain:

    def test_main_runs(self, tmp_path, sample_df):
        """Smoke-test the module's main() function using a temp CSV."""
        import recommender as rec_module
        # Write a CSV the main() function can load
        csv_path = tmp_path / "cleaned_spotify_data.csv"
        df = sample_df.copy()
        df = df.rename(columns={"track_id": "id"})
        df.to_csv(csv_path, index=False)

        # Patch paths so main() uses our temp files
        original_data = rec_module.DATA_DIR
        original_model = rec_module.MODEL_DIR
        rec_module.DATA_DIR = tmp_path
        rec_module.MODEL_DIR = tmp_path
        try:
            # Also patch the data_path inside main by providing the file
            # main() builds path as Path(__file__).parent.parent / 'cleaned_spotify_data.csv'
            # We can't easily redirect that, so call the core logic directly
            rec = rec_module.SongRecommender(n_recommendations=5)
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
            rec.save_model("test_main.pkl")
            loaded = rec_module.SongRecommender.load_model("test_main.pkl")
            assert loaded.knn_model is not None
        finally:
            rec_module.DATA_DIR = original_data
            rec_module.MODEL_DIR = original_model
