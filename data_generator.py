import pandas as pd
import numpy as np

INPUT_CSV = "spotify_top_1000_tracks.csv"
OUTPUT_CSV = "songs_with_audio_features.csv"

rng = np.random.default_rng(42)

def clamp(x, lo=0.0, hi=1.0):
    return np.minimum(np.maximum(x, lo), hi)

df = pd.read_csv(INPUT_CSV)

# Generate plausible audio features (0..1) + tempo
# Slight correlation with popularity just to make clustering less random
pop_norm = (df["popularity"] - df["popularity"].min()) / (df["popularity"].max() - df["popularity"].min() + 1e-9)

df["energy"] = clamp(rng.normal(0.55 + 0.20 * pop_norm, 0.18, size=len(df)))
df["valence"] = clamp(rng.normal(0.50 + 0.10 * pop_norm, 0.22, size=len(df)))
df["danceability"] = clamp(rng.normal(0.58 + 0.10 * pop_norm, 0.17, size=len(df)))
df["acousticness"] = clamp(rng.normal(0.35 - 0.15 * pop_norm, 0.25, size=len(df)))
df["instrumentalness"] = clamp(rng.normal(0.10, 0.20, size=len(df)))
df["liveness"] = clamp(rng.normal(0.18, 0.12, size=len(df)))
df["speechiness"] = clamp(rng.normal(0.08, 0.06, size=len(df)))

# Tempo in BPM (roughly 60–200)
df["tempo"] = np.clip(rng.normal(115 + 25 * (df["energy"] - 0.5), 18, size=len(df)), 60, 200)

# Optional: loudness in dB (negative values)
df["loudness"] = np.clip(rng.normal(-8 + 6 * (df["energy"] - 0.5), 3, size=len(df)), -30, 0)

df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved: {OUTPUT_CSV} with {len(df)} rows and {df.shape[1]} columns")
