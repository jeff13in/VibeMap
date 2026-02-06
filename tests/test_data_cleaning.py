"""
Tests for SpotifyDataCleaner (data_cleaner.py)
Covers: SQL execution, data quality analysis, cleaning pipeline, summary stats, export.
"""

import sqlite3

import pytest
import pandas as pd

from data_cleaner import SpotifyDataCleaner


# ---------------------------------------------------------------------------
# Context manager & helpers
# ---------------------------------------------------------------------------

class TestContextManager:
    """SpotifyDataCleaner as a context manager."""

    def test_enter_opens_connection(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as cleaner:
            assert cleaner.conn is not None

    def test_exit_closes_connection(self, sample_db):
        cleaner = SpotifyDataCleaner(db_path=sample_db)
        cleaner.__enter__()
        conn = cleaner.conn
        cleaner.__exit__(None, None, None)
        # After close, executing should raise
        with pytest.raises(Exception):
            conn.execute("SELECT 1")


class TestExecuteQuery:
    """execute_query helper."""

    def test_select_returns_rows(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            rows = c.execute_query("SELECT COUNT(*) FROM raw_songs")
            assert rows is not None
            assert rows[0][0] == 100

    def test_invalid_sql_returns_none(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            result = c.execute_query("SELECT * FROM nonexistent_table")
            assert result is None


class TestTableHelpers:
    """get_table_columns, resolve_artist_column, ensure_table_exists, table_row_count."""

    def test_get_table_columns(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            cols = c.get_table_columns("raw_songs")
            assert "track_id" in cols
            assert "valence" in cols
            assert "artist" in cols

    def test_get_table_columns_missing_table(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            cols = c.get_table_columns("no_such_table")
            assert cols == []

    def test_resolve_artist_column(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            col = c.resolve_artist_column("raw_songs")
            assert col == "artist"

    def test_resolve_artist_column_artist_name(self, tmp_path):
        """Table that uses 'artist_name' instead of 'artist'."""
        db = tmp_path / "alt.db"
        conn = sqlite3.connect(db)
        conn.execute("CREATE TABLE raw_songs (track_id TEXT, artist_name TEXT)")
        conn.execute("INSERT INTO raw_songs VALUES ('1', 'TestArtist')")
        conn.commit()
        conn.close()

        with SpotifyDataCleaner(db_path=db) as c:
            assert c.resolve_artist_column("raw_songs") == "artist_name"

    def test_resolve_artist_column_missing_raises(self, tmp_path):
        db = tmp_path / "no_artist.db"
        conn = sqlite3.connect(db)
        conn.execute("CREATE TABLE raw_songs (track_id TEXT, name TEXT)")
        conn.execute("INSERT INTO raw_songs VALUES ('1', 'X')")
        conn.commit()
        conn.close()

        with SpotifyDataCleaner(db_path=db) as c:
            with pytest.raises(RuntimeError, match="No artist column"):
                c.resolve_artist_column("raw_songs")

    def test_ensure_table_exists_success(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            c.ensure_table_exists("raw_songs")  # should not raise

    def test_ensure_table_exists_failure(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            with pytest.raises(RuntimeError, match="not found"):
                c.ensure_table_exists("missing_table")

    def test_table_row_count(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            assert c.table_row_count("raw_songs") == 100


# ---------------------------------------------------------------------------
# Data quality analysis
# ---------------------------------------------------------------------------

class TestAnalyzeDataQuality:

    def test_runs_without_error(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            c.analyze_data_quality()  # should print and not raise

    def test_missing_table_raises(self, tmp_path):
        db = tmp_path / "empty.db"
        conn = sqlite3.connect(db)
        conn.close()
        with SpotifyDataCleaner(db_path=db) as c:
            with pytest.raises(RuntimeError):
                c.analyze_data_quality()


# ---------------------------------------------------------------------------
# Cleaning pipeline
# ---------------------------------------------------------------------------

class TestCleanData:

    def test_creates_cleaned_songs_table(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            c.clean_data()
            count = c.table_row_count("cleaned_songs")
            assert count > 0

    def test_removes_null_artist(self, dirty_db):
        with SpotifyDataCleaner(db_path=dirty_db) as c:
            c.clean_data()
            rows = c.execute_query(
                "SELECT COUNT(*) FROM cleaned_songs WHERE artist IS NULL"
            )
            assert rows[0][0] == 0

    def test_fills_null_tempo(self, dirty_db):
        with SpotifyDataCleaner(db_path=dirty_db) as c:
            c.clean_data()
            rows = c.execute_query(
                "SELECT COUNT(*) FROM cleaned_songs WHERE tempo IS NULL"
            )
            assert rows[0][0] == 0

    def test_fills_null_valence(self, dirty_db):
        with SpotifyDataCleaner(db_path=dirty_db) as c:
            c.clean_data()
            rows = c.execute_query(
                "SELECT COUNT(*) FROM cleaned_songs WHERE valence IS NULL"
            )
            assert rows[0][0] == 0

    def test_fills_null_energy(self, dirty_db):
        with SpotifyDataCleaner(db_path=dirty_db) as c:
            c.clean_data()
            rows = c.execute_query(
                "SELECT COUNT(*) FROM cleaned_songs WHERE energy IS NULL"
            )
            assert rows[0][0] == 0

    def test_removes_tempo_outliers(self, dirty_db):
        with SpotifyDataCleaner(db_path=dirty_db) as c:
            c.clean_data()
            rows = c.execute_query(
                "SELECT COUNT(*) FROM cleaned_songs WHERE tempo < 50 OR tempo > 200"
            )
            assert rows[0][0] == 0

    def test_removes_feature_outliers(self, dirty_db):
        with SpotifyDataCleaner(db_path=dirty_db) as c:
            c.clean_data()
            rows = c.execute_query(
                "SELECT COUNT(*) FROM cleaned_songs WHERE valence < 0 OR valence > 1"
            )
            assert rows[0][0] == 0
            rows = c.execute_query(
                "SELECT COUNT(*) FROM cleaned_songs WHERE energy < 0 OR energy > 1"
            )
            assert rows[0][0] == 0

    def test_cleaned_count_less_than_dirty(self, dirty_db):
        with SpotifyDataCleaner(db_path=dirty_db) as c:
            raw_count = c.table_row_count("raw_songs")
            c.clean_data()
            clean_count = c.table_row_count("cleaned_songs")
            assert clean_count < raw_count

    def test_idempotent_clean(self, sample_db):
        """Running clean_data twice produces same result (table is recreated)."""
        with SpotifyDataCleaner(db_path=sample_db) as c:
            c.clean_data()
            count1 = c.table_row_count("cleaned_songs")
            c.clean_data()
            count2 = c.table_row_count("cleaned_songs")
            assert count1 == count2


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------

class TestSummaryStatistics:

    def test_runs_after_cleaning(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            c.clean_data()
            c.create_summary_statistics()  # should not raise

    def test_raises_without_cleaned_table(self, tmp_path):
        db = tmp_path / "no_clean.db"
        conn = sqlite3.connect(db)
        conn.execute("CREATE TABLE raw_songs (track_id TEXT, artist TEXT)")
        conn.commit()
        conn.close()
        with SpotifyDataCleaner(db_path=db) as c:
            with pytest.raises(RuntimeError):
                c.create_summary_statistics()


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

class TestExportCleanedData:

    def test_exports_csv(self, sample_db):
        with SpotifyDataCleaner(db_path=sample_db) as c:
            c.clean_data()
            df = c.export_cleaned_data()
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0

    def test_raises_without_cleaned_table(self, tmp_path):
        db = tmp_path / "no_clean2.db"
        conn = sqlite3.connect(db)
        conn.execute("CREATE TABLE raw_songs (track_id TEXT, artist TEXT)")
        conn.commit()
        conn.close()
        with SpotifyDataCleaner(db_path=db) as c:
            with pytest.raises(RuntimeError):
                c.export_cleaned_data()


# ---------------------------------------------------------------------------
# Fallback code paths
# ---------------------------------------------------------------------------

class TestFallbackPaths:

    def test_clean_without_duplicate_keys(self, tmp_path):
        """Table missing track_id: should copy all rows instead of dedup."""
        db = tmp_path / "nokeys.db"
        conn = sqlite3.connect(db)
        conn.execute(
            "CREATE TABLE raw_songs (name TEXT, artist TEXT, tempo REAL, "
            "valence REAL, energy REAL, danceability REAL)"
        )
        conn.execute(
            "INSERT INTO raw_songs VALUES ('A','Art1',120,0.5,0.5,0.5)"
        )
        conn.execute(
            "INSERT INTO raw_songs VALUES ('B','Art2',100,0.6,0.6,0.6)"
        )
        conn.commit()
        conn.close()
        with SpotifyDataCleaner(db_path=db) as c:
            c.clean_data()
            assert c.table_row_count("cleaned_songs") > 0

    def test_analyze_with_missing_columns(self, tmp_path):
        """Columns like 'danceability' missing — should skip gracefully."""
        db = tmp_path / "partial.db"
        conn = sqlite3.connect(db)
        conn.execute(
            "CREATE TABLE raw_songs (track_id TEXT, artist TEXT, tempo REAL)"
        )
        conn.execute("INSERT INTO raw_songs VALUES ('1','A',120)")
        conn.commit()
        conn.close()
        with SpotifyDataCleaner(db_path=db) as c:
            c.analyze_data_quality()  # should not raise

    def test_resolve_artist_fallback_substring(self, tmp_path):
        """Column containing 'artist' in name should be found."""
        db = tmp_path / "sub.db"
        conn = sqlite3.connect(db)
        conn.execute("CREATE TABLE raw_songs (track_id TEXT, main_artist TEXT)")
        conn.execute("INSERT INTO raw_songs VALUES ('1','X')")
        conn.commit()
        conn.close()
        with SpotifyDataCleaner(db_path=db) as c:
            assert c.resolve_artist_column("raw_songs") == "main_artist"

    def test_analyze_skips_dup_check_when_keys_missing(self, tmp_path):
        """No track_name column — duplicate check should be skipped, not error."""
        db = tmp_path / "notrack.db"
        conn = sqlite3.connect(db)
        conn.execute(
            "CREATE TABLE raw_songs (track_id TEXT, artist TEXT, "
            "tempo REAL, valence REAL, energy REAL)"
        )
        conn.execute("INSERT INTO raw_songs VALUES ('1','A',120,0.5,0.5)")
        conn.commit()
        conn.close()
        with SpotifyDataCleaner(db_path=db) as c:
            c.analyze_data_quality()  # should not raise

    def test_analyze_skips_outlier_check_when_cols_missing(self, tmp_path):
        """Missing valence/energy — outlier check should be skipped."""
        db = tmp_path / "nofeat.db"
        conn = sqlite3.connect(db)
        conn.execute("CREATE TABLE raw_songs (track_id TEXT, artist TEXT, tempo REAL)")
        conn.execute("INSERT INTO raw_songs VALUES ('1','A',120)")
        conn.commit()
        conn.close()
        with SpotifyDataCleaner(db_path=db) as c:
            c.analyze_data_quality()  # should not raise
