# VibeMap 🎵

VibeMap is a full-stack **music recommendation system** that analyzes songs by **mood** and **tempo** using Spotify audio features from Kaggle. Songs are clustered into mood groups using K-Means, recommended via KNN/cosine/euclidean similarity, and accessible through a React web app, Flask REST API, and interactive CLI.

> For detailed system diagrams, see [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Summary

- **Frontend (Vercel):** React + TypeScript SPA with Tailwind CSS, Zustand state management, and ECharts analytics. Users pick from 8 moods and 3 tempo categories, results display as song cards with audio feature bars.

- **Backend (Render):** Flask REST API (8 endpoints) served by Gunicorn with 2 workers. Uses a `SongRecommender` class that supports filter-based recommendations (mood/tempo/combined) and similarity-based recommendations (KNN, cosine, euclidean distance).

- **Data Pipeline:** Kaggle CSV → synthetic data generation with injected quality issues → SQL-based cleaning (dedup, imputation, outlier removal) → K-Means clustering (5 mood clusters) → KNN model training. All stored in SQLite with models serialized via joblib.

- **ML:** 9 audio features (valence, energy, danceability, tempo, acousticness, instrumentalness, liveness, speechiness, loudness) power both clustering and recommendations. Songs are filtered by threshold rules (e.g., happy = valence ≥ 0.6 + energy ≥ 0.5) or ranked by similarity scores.

- **Security:** 4 layers — CORS origin whitelist, security headers, input validation/clamping, and SQL injection/path traversal prevention.

- **Testing:** 125 unit tests at 88% coverage across data cleaning, recommender, and clustering modules.

---

## Features

- Synthetic Spotify-style dataset generation
- SQL-based data cleaning and validation
- Exploratory Data Analysis (EDA) with visualizations
- Mood-based clustering using K-Means (5 clusters)
- Multi-algorithm recommendation engine:
  - K-Nearest Neighbors (KNN)
  - Cosine Similarity
  - Euclidean Distance
- 8 mood filters (happy, sad, energetic, calm, party, dark, romantic, angry)
- 3 tempo categories (slow, medium, fast)
- React frontend with live analytics dashboard (ECharts)
- Flask REST API (8 endpoints)
- Interactive Command Line Interface (CLI)
- Automated testing (125 tests, 88% coverage)

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, TypeScript 5.3, Vite 5.0, Tailwind CSS 3.3, Zustand, Axios, ECharts, GSAP, Radix UI |
| **Backend** | Flask, Gunicorn, SQLite, Pandas, NumPy |
| **ML** | scikit-learn (K-Means, KNN, StandardScaler), SciPy, Joblib |
| **Visualization** | Matplotlib, Seaborn, Plotly, ECharts |
| **Testing** | Pytest, pytest-cov |
| **Deployment** | Vercel (frontend), Render (backend), GitHub |

---

## Quick Start

### 1. Clone & Setup Environment

```bash
git clone <your-repo-url>
cd vibemap
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 2. Run Full Pipeline

```bash
python run_pipeline.py
```

### 3. Run Full-Stack App (Development)

```bash
# Terminal 1: Start the Flask API
cd backend && python api_server.py

# Terminal 2: Start the React frontend
cd frontend && npm install && npm run dev
```

The frontend runs at `http://localhost:5173` and proxies API calls to `http://localhost:8000`.

### 4. Run CLI Application

```bash
python -m src.cli_app
```

### 5. Run Tests

```bash
pytest tests/ -v
pytest tests/ --cov=data_cleaner --cov=recommender --cov=clustering --cov-report=term-missing
```

---

## Core Modules

| Module | File | Description |
|---|---|---|
| Data Generator | `data_generator.py` | Generates synthetic Spotify-like song data with injected quality issues. Outputs to CSV and SQLite. |
| Data Cleaner | `data_cleaner.py` | SQL-based cleaning — removes duplicates (`ROW_NUMBER()`), imputes nulls with means, removes outliers. |
| Clustering | `clustering.py` | K-Means clustering on 5 audio features. Finds optimal k via silhouette score. Produces 5 mood clusters. |
| Recommender | `recommender.py` | 4 recommendation modes — by mood (8), by tempo (3), combined, and by song similarity (KNN/cosine/euclidean). |
| API Server | `api_server.py` | Flask REST API with 8 endpoints, input validation, security headers, and restricted CORS. |
| CLI App | `cli_app.py` | Interactive terminal app with 10-option menu and ANSI-colored output. |
| Pipeline | `run_pipeline.py` | Master orchestrator running all stages in sequence with progress indicators. |

---

## Deployment

| Component | Platform | Status |
|---|---|---|
| Frontend | Vercel | Done |
| Backend | Render | Done |
| Database | SQLite (bundled) | Done |
