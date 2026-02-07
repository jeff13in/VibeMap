"""
Day 1-2: SQL Data Cleaning Script
Demonstrates SQL-based data cleaning techniques
"""

import sqlite3
import pandas as pd
from pathlib import Path


# Project root = directory containing this file (NO FOLDERS REQUIRED)
BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "spotify_data.db"
CSV_PATH = BASE_DIR / "songs_with_audio_features.csv"  # (not used in this script, but kept)


class SpotifyDataCleaner:
    """SQL-based data cleaning for Spotify dataset"""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    # -----------------------------
    # Helpers
    # -----------------------------

    def execute_query(self, query, description=""):
        """Execute a SQL query and return results (if any)."""
        if description:
            print(f"\n🔍 {description}")

        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()

            # Try to fetch results for SELECT queries
            try:
                results = cursor.fetchall()
                if results is not None and description:
                    print(f"   ✅ Returned {len(results)} rows")
                return results
            except Exception:
                if description:
                    print("   ✅ Query executed successfully")
                return None

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return None

    def get_table_columns(self, table_name="raw_songs"):
        """Return a list of column names for a table."""
        rows = self.execute_query(f"PRAGMA table_info({table_name});")
        if not rows:
            return []
        return [r[1] for r in rows]  # r[1] = name

    def resolve_artist_column(self, table_name="raw_songs"):
        """Find the correct artist column name (handles artist_name vs artists etc.)."""
        cols = self.get_table_columns(table_name)
        if not cols:
            raise RuntimeError(f"Could not read columns for table: {table_name}")

        candidates = [
            "artist_name",
            "artist",
            "artists",
            "artist_names",
            "artists_name",
            "artistName",
        ]
        for c in candidates:
            if c in cols:
                return c

        # fallback: any column containing "artist"
        for c in cols:
            if "artist" in c.lower():
                return c

        raise RuntimeError(f"No artist column found in {table_name}. Available columns: {cols}")

    def ensure_table_exists(self, table_name="raw_songs"):
        """Fail early if the table doesn't exist."""
        q = f"""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name='{table_name}';
        """
        r = self.execute_query(q)
        if not r:
            raise RuntimeError(
                f"Table '{table_name}' not found in DB. "
                f"Check your generator created the DB/table correctly."
            )

    def table_row_count(self, table_name):
        r = self.execute_query(f"SELECT COUNT(*) FROM {table_name};")
        return r[0][0] if r else 0

    # -----------------------------
    # Analysis
    # -----------------------------

    def analyze_data_quality(self):
        """Analyze data quality issues using SQL."""
        print("\n" + "=" * 60)
        print("📊 DATA QUALITY ANALYSIS")
        print("=" * 60)

        self.ensure_table_exists("raw_songs")

        raw_cols = self.get_table_columns("raw_songs")
        artist_col = self.resolve_artist_column("raw_songs")

        # 1. Count total records
        result = self.execute_query("SELECT COUNT(*) as total_records FROM raw_songs", "Counting total records")
        if result:
            print(f"   Total records: {result[0][0]}")

        # 2. Check for missing values (only if those cols exist)
        print("\n   Missing Values by Column:")
        checks = [artist_col, "tempo", "valence", "energy", "danceability"]
        for col in checks:
            if col in raw_cols:
                r = self.execute_query(f"SELECT COUNT(*) FROM raw_songs WHERE {col} IS NULL")
                if r:
                    print(f"      - {col}: {r[0][0]} missing")
            else:
                print(f"      - {col}: (skipped - column not found)")

        # 3. Check for duplicates (only if required columns exist)
        needed = {"track_id", "track_name", artist_col}
        if needed.issubset(set(raw_cols)):
            query = f"""
            SELECT track_id, track_name, {artist_col}, COUNT(*) as count
            FROM raw_songs
            GROUP BY track_id, track_name, {artist_col}
            HAVING COUNT(*) > 1
            """
            result = self.execute_query(query, "Finding duplicate records")
            if result is not None:
                print(f"   Duplicate groups found: {len(result)}")
        else:
            print("\n   ⚠️ Skipping duplicate check: missing one of track_id / track_name / artist column")

        # 4. Check for outliers (only if cols exist)
        outlier_cols = {"tempo", "valence", "energy"}
        if outlier_cols.issubset(set(raw_cols)):
            query = """
            SELECT 
                SUM(CASE WHEN tempo > 200 OR tempo < 50 THEN 1 ELSE 0 END) as tempo_outliers,
                SUM(CASE WHEN valence < 0 OR valence > 1 THEN 1 ELSE 0 END) as valence_outliers,
                SUM(CASE WHEN energy < 0 OR energy > 1 THEN 1 ELSE 0 END) as energy_outliers
            FROM raw_songs
            """
            result = self.execute_query(query, "Checking for outliers")
            if result:
                print(f"   Tempo outliers: {result[0][0]}")
                print(f"   Valence outliers: {result[0][1]}")
                print(f"   Energy outliers: {result[0][2]}")
        else:
            print("\n   ⚠️ Skipping outlier check: tempo/valence/energy not all present")

    # -----------------------------
    # Cleaning
    # -----------------------------

    def clean_data(self):
        """Perform SQL-based data cleaning."""
        print("\n" + "=" * 60)
        print("🧹 DATA CLEANING OPERATIONS")
        print("=" * 60)

        self.ensure_table_exists("raw_songs")
        raw_cols = self.get_table_columns("raw_songs")
        artist_col = self.resolve_artist_column("raw_songs")

        # Recreate cleaned_songs fresh each run (prevents duplicates from re-running)
        self.execute_query("DROP TABLE IF EXISTS cleaned_songs;", "Dropping old cleaned_songs (if any)")
        self.execute_query("CREATE TABLE cleaned_songs AS SELECT * FROM raw_songs WHERE 0;", "Creating cleaned_songs")

        # Build a safe column list (so we don't accidentally insert rn column)
        col_list = ", ".join([f'"{c}"' for c in raw_cols])

        # Step 1: Remove duplicates using ROW_NUMBER (only if keys exist)
        if {"track_id", "track_name", artist_col}.issubset(set(raw_cols)):
            order_col = "popularity" if "popularity" in raw_cols else "track_id"
            query = f"""
        INSERT INTO cleaned_songs ({col_list})
        SELECT {col_list}
        FROM (
            SELECT {col_list},
                ROW_NUMBER() OVER (
                    PARTITION BY track_id, track_name, "{artist_col}"
                    ORDER BY "{order_col}" DESC
                ) AS rn
            FROM raw_songs
        )
        WHERE rn = 1;
            """
            self.execute_query(query, "Removing duplicate records (ROW_NUMBER)")
        else:
            # If missing keys, just copy everything
            self.execute_query(f'INSERT INTO cleaned_songs ({col_list}) SELECT {col_list} FROM raw_songs;', 
                               "Copying raw_songs (duplicate keys missing)")

        # Step 2: Remove records with missing artist value (only if col exists)
        if artist_col in raw_cols:
            self.execute_query(f'DELETE FROM cleaned_songs WHERE "{artist_col}" IS NULL;', 
                               "Removing records with missing artist values")

        # Step 3: Fill missing tempo with MEAN (comment corrected)
        if "tempo" in raw_cols:
            query = """
            UPDATE cleaned_songs
            SET tempo = (
                SELECT ROUND(AVG(tempo), 2)
                FROM cleaned_songs
                WHERE tempo IS NOT NULL
                  AND tempo BETWEEN 50 AND 200
            )
            WHERE tempo IS NULL;
            """
            self.execute_query(query, "Filling missing tempo values with mean")

        # Step 4: Fill missing valence with MEAN
        if "valence" in raw_cols:
            query = """
            UPDATE cleaned_songs
            SET valence = (
                SELECT ROUND(AVG(valence), 4)
                FROM cleaned_songs
                WHERE valence IS NOT NULL
                  AND valence BETWEEN 0 AND 1
            )
            WHERE valence IS NULL;
            """
            self.execute_query(query, "Filling missing valence values with mean")

        # Step 4b: Fill missing energy with MEAN (optional but helpful)
        if "energy" in raw_cols:
            query = """
            UPDATE cleaned_songs
            SET energy = (
                SELECT ROUND(AVG(energy), 4)
                FROM cleaned_songs
                WHERE energy IS NOT NULL
                  AND energy BETWEEN 0 AND 1
            )
            WHERE energy IS NULL;
            """
            self.execute_query(query, "Filling missing energy values with mean")

        # Step 5: Remove outliers - tempo
        if "tempo" in raw_cols:
            self.execute_query(
                "DELETE FROM cleaned_songs WHERE tempo < 50 OR tempo > 200;",
                "Removing invalid tempo values"
            )

        # Step 6-7: Remove outliers for all audio features that exist
        feature_cols = [
            "valence", "energy", "danceability", "acousticness",
            "instrumentalness", "liveness", "speechiness"
        ]
        conditions = []
        for c in feature_cols:
            if c in raw_cols:
                conditions.append(f"{c} < 0 OR {c} > 1")

        if conditions:
            self.execute_query(
                "DELETE FROM cleaned_songs WHERE " + " OR ".join(conditions) + ";",
                "Ensuring all audio features are in valid 0..1 range"
            )

        # Final record count
        count = self.table_row_count("cleaned_songs")
        print(f"\n   ✅ Clean dataset has {count} records")

    # -----------------------------
    # Summary Stats
    # -----------------------------

    def create_summary_statistics(self):
        """Create summary statistics using SQL."""
        print("\n" + "=" * 60)
        print("📈 SUMMARY STATISTICS")
        print("=" * 60)

        self.ensure_table_exists("cleaned_songs")
        cleaned_cols = self.get_table_columns("cleaned_songs")
        artist_col = self.resolve_artist_column("cleaned_songs")

        # If artist col somehow missing, handle gracefully
        unique_artist_expr = f'COUNT(DISTINCT "{artist_col}")' if artist_col in cleaned_cols else "NULL"

        query = f"""
        SELECT 
            COUNT(*) as total_songs,
            {unique_artist_expr} as unique_artists,
            ROUND(AVG(valence), 3) as avg_valence,
            ROUND(AVG(energy), 3) as avg_energy,
            ROUND(AVG(tempo), 2) as avg_tempo,
            ROUND(AVG(danceability), 3) as avg_danceability,
            ROUND(MIN(tempo), 2) as min_tempo,
            ROUND(MAX(tempo), 2) as max_tempo
        FROM cleaned_songs;
        """

        result = self.execute_query(query, "Computing summary statistics")
        if result:
            stats = result[0]
            print(f"\n   Total Songs: {stats[0]}")
            print(f"   Unique Artists: {stats[1]}")
            print(f"   Average Valence: {stats[2]}")
            print(f"   Average Energy: {stats[3]}")
            print(f"   Average Tempo: {stats[4]} BPM")
            print(f"   Average Danceability: {stats[5]}")
            print(f"   Tempo Range: {stats[6]} - {stats[7]} BPM")

    # -----------------------------
    # Export
    # -----------------------------

    def export_cleaned_data(self):
        """Export cleaned data to CSV (in the SAME ROOT folder, no data/ directory)."""
        self.ensure_table_exists("cleaned_songs")
        df = pd.read_sql_query("SELECT * FROM cleaned_songs", self.conn)

        output_path = BASE_DIR / "cleaned_spotify_data.csv"
        df.to_csv(output_path, index=False)

        print(f"\n✅ Exported cleaned data to {output_path}")
        print(f"   Shape: {df.shape}")

        return df


def main():
    """Main execution function."""
    print("\n🎵 SPOTIFY DATA CLEANING WITH SQL")
    print("=" * 60)

    # Quick sanity print
    print(f"DB_PATH: {DB_PATH}")
    print(f"DB exists: {DB_PATH.exists()}")

    with SpotifyDataCleaner() as cleaner:
        cleaner.analyze_data_quality()
        cleaner.clean_data()
        cleaner.create_summary_statistics()
        df = cleaner.export_cleaned_data()

    print("\n✨ Data cleaning complete!")
    return df


if __name__ == "__main__":
    main()
