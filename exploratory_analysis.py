"""
SCRUM-85: Exploratory Data Analysis (EDA)

Purpose:
- Load cleaned Spotify dataset
- Perform a complete EDA run end-to-end
- Generate basic statistics and core visualizations

SCRUM-94:
- Define mood quadrants using valence (positivity) and energy (intensity)
- Save a mood space plot

SCRUM-95:
- Create tempo categories (Slow/Medium/Fast) using BPM tempo
- Save a tempo category plot

Run:
    python exploratory_analysis.py
"""

from pathlib import Path
import warnings

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# Config
# -----------------------------
warnings.filterwarnings("ignore")

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT
OUTPUT_DIR = PROJECT_ROOT / "notebooks" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class SpotifyEDA:
    """Basic EDA pipeline for SCRUM-85 + SCRUM-94 + SCRUM-95"""

    def __init__(self, data_path: Path):
        self.df = pd.read_csv(data_path)

        self.audio_features = [
            "valence",
            "energy",
            "danceability",
            "tempo",
            "acousticness",
            "instrumentalness",
            "liveness",
            "speechiness",
            "loudness",
        ]

        print(f"✅ Dataset loaded: {self.df.shape}")

    def basic_info(self):
        """Dataset overview"""
        print("\n=== BASIC INFO ===")
        print(self.df.info())
        print("\nSample rows:")
        print(self.df.head())

    def descriptive_stats(self):
        """Basic statistics"""
        print("\n=== DESCRIPTIVE STATISTICS ===")
        print(self.df[self.audio_features].describe().round(3))

    def correlation_analysis(self):
        """Correlation heatmap"""
        print("\n=== CORRELATION ANALYSIS ===")

        corr = self.df[self.audio_features].corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap="coolwarm", center=0)
        plt.title("Audio Feature Correlations")

        out = OUTPUT_DIR / "correlation_heatmap.png"
        plt.savefig(out, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"Saved correlation heatmap → {out}")

    def feature_distributions(self):
        """Distribution plots"""
        print("\n=== FEATURE DISTRIBUTIONS ===")

        fig, axes = plt.subplots(3, 3, figsize=(15, 12))
        axes = axes.flatten()

        for i, feature in enumerate(self.audio_features):
            sns.histplot(self.df[feature], kde=True, ax=axes[i])
            axes[i].set_title(feature)

        plt.tight_layout()
        out = OUTPUT_DIR / "feature_distributions.png"
        plt.savefig(out, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"Saved feature distributions → {out}")

    def mood_quadrants(self):
        """
        SCRUM-94: Create mood quadrants using valence and energy.

        Quadrants:
          - Happy & Energetic (valence >= 0.5, energy >= 0.5)
          - Happy & Calm      (valence >= 0.5, energy <  0.5)
          - Sad & Energetic   (valence <  0.5, energy >= 0.5)
          - Sad & Calm        (valence <  0.5, energy <  0.5)

        Saves plot to: notebooks/figures/mood_space.png
        """
        print("\n=== MOOD QUADRANTS (SCRUM-94) ===")

        required_cols = {"valence", "energy"}
        missing = required_cols - set(self.df.columns)
        if missing:
            raise ValueError(f"Missing required columns for mood quadrants: {sorted(missing)}")

        self.df["mood_quadrant"] = "Unknown"

        self.df.loc[
            (self.df["valence"] >= 0.5) & (self.df["energy"] >= 0.5),
            "mood_quadrant",
        ] = "Happy & Energetic"

        self.df.loc[
            (self.df["valence"] >= 0.5) & (self.df["energy"] < 0.5),
            "mood_quadrant",
        ] = "Happy & Calm"

        self.df.loc[
            (self.df["valence"] < 0.5) & (self.df["energy"] >= 0.5),
            "mood_quadrant",
        ] = "Sad & Energetic"

        self.df.loc[
            (self.df["valence"] < 0.5) & (self.df["energy"] < 0.5),
            "mood_quadrant",
        ] = "Sad & Calm"

        counts = self.df["mood_quadrant"].value_counts()
        total = len(self.df)

        print("\nSongs by Mood Quadrant:")
        for label, count in counts.items():
            print(f"  {label}: {count} ({count / total * 100:.1f}%)")

        plt.figure(figsize=(12, 8))
        sns.scatterplot(
            data=self.df,
            x="valence",
            y="energy",
            hue="mood_quadrant",
            alpha=0.7,
        )

        plt.axvline(0.5, color="gray", linestyle="--", linewidth=1)
        plt.axhline(0.5, color="gray", linestyle="--", linewidth=1)

        plt.title("Song Distribution in Mood Space (Valence vs Energy)", fontweight="bold")
        plt.xlabel("Valence (Positivity)")
        plt.ylabel("Energy (Intensity)")
        plt.tight_layout()

        out = OUTPUT_DIR / "mood_space.png"
        plt.savefig(out, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"\n✅ Saved mood space plot → {out}")

    def tempo_categories(self, slow_max: float = 90.0, fast_min: float = 130.0):
        """
        SCRUM-95: Create tempo categories using BPM tempo.

        Rules (default):
          - Slow:   tempo <  90 BPM
          - Medium: 90 <= tempo < 130 BPM
          - Fast:   tempo >= 130 BPM

        Saves plot to: notebooks/figures/tempo_categories.png
        """
        print("\n=== TEMPO CATEGORIES (SCRUM-95) ===")

        if "tempo" not in self.df.columns:
            raise ValueError("Missing required column: 'tempo'")

        # Convert to numeric safely (in case any weird values slipped in)
        tempo = pd.to_numeric(self.df["tempo"], errors="coerce")
        self.df["tempo"] = tempo

        # Optional: drop NaN tempos from categorization/plotting
        valid_df = self.df.dropna(subset=["tempo"]).copy()

        # Categorize
        valid_df["tempo_category"] = pd.cut(
            valid_df["tempo"],
            bins=[-float("inf"), slow_max, fast_min, float("inf")],
            labels=["Slow", "Medium", "Fast"],
            right=False,  # slow: < slow_max, medium: [slow_max, fast_min), fast: >= fast_min
        )

        # Write categories back to main df (align by index)
        self.df["tempo_category"] = None
        self.df.loc[valid_df.index, "tempo_category"] = valid_df["tempo_category"].astype(str)

        # Print counts + percentages
        counts = valid_df["tempo_category"].value_counts()
        total = len(valid_df)

        print(f"\nTempo thresholds: Slow < {slow_max} | Medium {slow_max}-{fast_min-1e-9:.0f} | Fast >= {fast_min}")
        print("Songs by Tempo Category:")
        for label, count in counts.items():
            print(f"  {label}: {count} ({count / total * 100:.1f}%)")

        # Plot: histogram colored by tempo_category
        plt.figure(figsize=(12, 6))
        sns.histplot(
            data=valid_df,
            x="tempo",
            hue="tempo_category",
            bins=30,
            kde=True,
            multiple="stack",
        )
        plt.title("Tempo Distribution by Category (SCRUM-95)", fontweight="bold")
        plt.xlabel("Tempo (BPM)")
        plt.ylabel("Count")
        plt.tight_layout()

        out = OUTPUT_DIR / "tempo_categories.png"
        plt.savefig(out, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"\n✅ Saved tempo categories plot → {out}")

    def run(self):
        """Run complete EDA"""
        print("\n🎵 RUNNING EXPLORATORY DATA ANALYSIS")

        self.basic_info()
        self.descriptive_stats()
        self.correlation_analysis()
        self.feature_distributions()

        # SCRUM-94
        self.mood_quadrants()

        # SCRUM-95
        self.tempo_categories()

        print("\n✅ SCRUM-85 + SCRUM-94 + SCRUM-95 COMPLETE")


def main():
    data_path = DATA_DIR / "cleaned_spotify_data.csv"

    if not data_path.exists():
        raise FileNotFoundError("cleaned_spotify_data.csv not found")

    eda = SpotifyEDA(data_path)
    eda.run()


if __name__ == "__main__":
    main()
