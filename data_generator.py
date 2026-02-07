"""
data_generator.py

Reads a base Spotify tracks CSV and adds synthetic audio features.
Intentionally injects data quality issues (nulls, duplicates, outliers)
to simulate real-world imperfections for the SQL cleaning pipeline.

Outputs:
- CSV (dirty/raw dataset)
- SQLite DB table (optional)

Usage:
  python data_generator.py \
    --input-csv spotify_top_1000_tracks.csv \
    --out-csv songs_with_audio_features.csv \
    --out-db spotify_data.db \
    --table raw_songs \
    --seed 42 \
    --null-frac 0.05 \
    --dup-frac 0.05 \
    --outlier-frac 0.05
"""

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


# -----------------------------
# Config
# -----------------------------

@dataclass(frozen=True)
class Config:
    input_csv: str
    out_csv: str
    out_db: str | None
    table: str
    seed: int
    null_frac: float
    dup_frac: float
    outlier_frac: float


AUDIO_FEATURE_COLS = [
    "energy",
    "valence",
    "danceability",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
]

NULL_TARGET_COLS = ["tempo", "valence", "energy", "danceability"]


# -----------------------------
# Utilities
# -----------------------------

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def clamp01(x: np.ndarray) -> np.ndarray:
    return np.clip(x, 0.0, 1.0)


def safe_popularity_norm(popularity: pd.Series) -> np.ndarray:
    pmin = float(popularity.min())
    pmax = float(popularity.max())
    denom = (pmax - pmin) if (pmax - pmin) != 0 else 1.0
    return ((popularity.astype(float) - pmin) / denom).to_numpy()


# -----------------------------
# Core generation
# -----------------------------

def add_synthetic_audio_features(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """
    Adds Spotify-like audio features with slight correlation to popularity.
    """
    required = {"popularity"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in input CSV: {sorted(missing)}")

    out = df.copy()

    pop_norm = safe_popularity_norm(out["popularity"])

    out["energy"] = clamp01(rng.normal(0.55 + 0.20 * pop_norm, 0.18, size=len(out)))
    out["valence"] = clamp01(rng.normal(0.50 + 0.10 * pop_norm, 0.22, size=len(out)))
    out["danceability"] = clamp01(rng.normal(0.58 + 0.10 * pop_norm, 0.17, size=len(out)))
    out["acousticness"] = clamp01(rng.normal(0.35 - 0.15 * pop_norm, 0.25, size=len(out)))
    out["instrumentalness"] = clamp01(rng.normal(0.10, 0.20, size=len(out)))
    out["liveness"] = clamp01(rng.normal(0.18, 0.12, size=len(out)))
    out["speechiness"] = clamp01(rng.normal(0.08, 0.06, size=len(out)))

    # Tempo in BPM (mostly within 60–200 initially)
    out["tempo"] = np.clip(
        rng.normal(115 + 25 * (out["energy"] - 0.5), 18, size=len(out)),
        60,
        200,
    ).round(2)

    # Optional: loudness in dB (negative values)
    out["loudness"] = np.clip(
        rng.normal(-8 + 6 * (out["energy"] - 0.5), 3, size=len(out)),
        -30,
        0,
    ).round(2)

    # Round 0..1 features for neatness
    for col in AUDIO_FEATURE_COLS:
        out[col] = out[col].round(4)

    return out


# -----------------------------
# Intentional data quality issues
# -----------------------------

def inject_nulls(df: pd.DataFrame, columns: Iterable[str], frac: float, rng: np.random.Generator) -> pd.DataFrame:
    if frac <= 0:
        return df
    out = df.copy()
    n_rows = len(out)
    n_nulls = max(1, int(n_rows * frac))

    for col in columns:
        if col not in out.columns:
            continue
        idx = rng.choice(out.index, size=n_nulls, replace=False)
        out.loc[idx, col] = np.nan

    return out


def inject_duplicates(df: pd.DataFrame, frac: float, rng: np.random.Generator) -> pd.DataFrame:
    if frac <= 0:
        return df
    n_dups = max(1, int(len(df) * frac))
    dup_rows = df.sample(n=n_dups, random_state=int(rng.integers(0, 1_000_000_000)))
    return pd.concat([df, dup_rows], ignore_index=True)


def inject_outliers(df: pd.DataFrame, frac: float, rng: np.random.Generator) -> pd.DataFrame:
    """
    Creates out-of-range values for cleaning tests:
    - tempo: <50 or >200
    - audio features: <0 or >1
    """
    if frac <= 0:
        return df

    out = df.copy()
    k = max(1, int(len(out) * frac))
    idx = rng.choice(out.index, size=k, replace=False)

    half = k // 2
    idx_tempo = idx[:half]
    idx_feat = idx[half:]

    if "tempo" in out.columns and len(idx_tempo) > 0:
        out.loc[idx_tempo, "tempo"] = rng.choice([10, 30, 250, 320], size=len(idx_tempo))

    for col in AUDIO_FEATURE_COLS:
        if col in out.columns and len(idx_feat) > 0:
            out.loc[idx_feat, col] = rng.choice([-0.4, -0.1, 1.2, 1.6], size=len(idx_feat))

    return out


# -----------------------------
# Output
# -----------------------------

def save_csv(df: pd.DataFrame, path: str) -> None:
    ensure_parent_dir(path)
    df.to_csv(path, index=False)


def save_sqlite(df: pd.DataFrame, db_path: str, table: str) -> None:
    ensure_parent_dir(db_path)
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table, conn, if_exists="replace", index=False)


# -----------------------------
# CLI + main
# -----------------------------

def parse_args() -> Config:
    p = argparse.ArgumentParser(description="Generate synthetic Spotify-style dataset with intentional data issues.")
    p.add_argument("--input-csv", default="spotify_top_1000_tracks.csv")
    p.add_argument("--out-csv", default="songs_with_audio_features.csv")
    p.add_argument("--out-db", default=None, help="Optional SQLite DB path (ex: data/spotify_data.db)")
    p.add_argument("--table", default="raw_songs", help="SQLite table name if --out-db is provided")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--null-frac", type=float, default=0.05)
    p.add_argument("--dup-frac", type=float, default=0.05)
    p.add_argument("--outlier-frac", type=float, default=0.05)

    a = p.parse_args()

    return Config(
        input_csv=a.input_csv,
        out_csv=a.out_csv,
        out_db=a.out_db,
        table=a.table,
        seed=a.seed,
        null_frac=a.null_frac,
        dup_frac=a.dup_frac,
        outlier_frac=a.outlier_frac,
    )


def main() -> int:
    setup_logging()
    cfg = parse_args()
    rng = np.random.default_rng(cfg.seed)

    logging.info("Reading input CSV: %s", cfg.input_csv)
    df = pd.read_csv(cfg.input_csv)
    logging.info("Loaded %d rows, %d columns", len(df), df.shape[1])

    logging.info("Generating synthetic audio features...")
    df = add_synthetic_audio_features(df, rng)

    logging.info("Injecting data quality issues: nulls=%.2f, dups=%.2f, outliers=%.2f",
                 cfg.null_frac, cfg.dup_frac, cfg.outlier_frac)

    before_rows = len(df)
    df = inject_nulls(df, NULL_TARGET_COLS, cfg.null_frac, rng)
    df = inject_outliers(df, cfg.outlier_frac, rng)
    df = inject_duplicates(df, cfg.dup_frac, rng)
    after_rows = len(df)

    logging.info("Row count: %d -> %d (after adding duplicates)", before_rows, after_rows)
    logging.info("Saving CSV: %s", cfg.out_csv)
    save_csv(df, cfg.out_csv)

    if cfg.out_db:
        logging.info("Saving SQLite DB: %s (table=%s)", cfg.out_db, cfg.table)
        save_sqlite(df, cfg.out_db, cfg.table)

    logging.info("Done. Output rows=%d cols=%d", len(df), df.shape[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
