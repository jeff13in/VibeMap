"""
SCRUM-85: Exploratory Data Analysis (EDA)

Purpose:
- Load cleaned Spotify dataset
- Perform a complete EDA run end-to-end
- Generate basic statistics and core visualizations

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

# Project paths (simple version for now)
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT
OUTPUT_DIR = PROJECT_ROOT / "notebooks" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class SpotifyEDA:
    """Basic EDA pipeline for SCRUM-85"""

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

    def run(self):
        """Run complete EDA"""
        print("\n🎵 RUNNING EXPLORATORY DATA ANALYSIS")

        self.basic_info()
        self.descriptive_stats()
        self.correlation_analysis()
        self.feature_distributions()

        print("\n✅ SCRUM-85 COMPLETE: EDA ran end-to-end")


def main():
    data_path = DATA_DIR / "cleaned_spotify_data.csv"

    if not data_path.exists():
        raise FileNotFoundError("cleaned_spotify_data.csv not found")

    eda = SpotifyEDA(data_path)
    eda.run()


if __name__ == "__main__":
    main()
