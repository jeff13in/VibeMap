# VibeMap - Spotify Song Recommendation & Mood Clustering

A full-stack music recommendation system that analyzes songs by mood and tempo using Spotify audio features from Kaggle. Songs are clustered into mood groups using K-means, recommended via KNN/cosine/euclidean similarity, and accessible through a React web app, Flask REST API, and interactive CLI.

---

## Project Structure

```
VibeMap/
├── frontend/                        # React TypeScript web application
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.tsx          # Landing page with hero, benefits, moods, features
│   │   │   ├── Recommendations.tsx  # Main recommendations page (mood/tempo/combined tabs)
│   │   │   └── Home.tsx             # Alternative home page
│   │   ├── components/
│   │   │   ├── MoodSelector.tsx     # Mood selection grid (8 moods)
│   │   │   ├── SongCard.tsx         # Song display card with audio feature bars
│   │   │   ├── AnalyticsDashboard.tsx # Live analytics with ECharts visualizations
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx       # Navigation header with logo
│   │   │   │   └── Footer.tsx       # Footer component
│   │   │   └── ui/                  # Shadcn/Radix UI components (button, card, slider, etc.)
│   │   ├── hooks/
│   │   │   └── useRecommendations.ts # Custom hook for API calls and state
│   │   ├── store/
│   │   │   └── recommendationStore.ts # Zustand state management
│   │   ├── lib/
│   │   │   ├── api.ts               # Axios API client for all endpoints
│   │   │   └── utils.ts             # Helper utilities
│   │   ├── types/
│   │   │   └── song.ts              # TypeScript interfaces (Song, MoodType, TempoType, etc.)
│   │   ├── App.tsx                  # Root app with React Router
│   │   └── main.tsx                 # React entry point
│   ├── package.json                 # Frontend dependencies
│   ├── vite.config.ts               # Vite build config with API proxy
│   ├── tailwind.config.js           # Tailwind CSS theme (mood colors, Spotify green)
│   ├── tsconfig.json                # TypeScript config with path aliases
│   └── index.html                   # HTML entry point
│
├── src/                             # Core Python modules (mirror)
│   ├── __init__.py
│   ├── cli.py                       # CLI entry point
│   ├── clustering.py                # K-means mood clustering engine
│   ├── data_cleaner.py              # SQL-based data cleaning pipeline
│   ├── data_generator.py            # Synthetic Spotify data generator
│   └── recommender.py               # Song recommendation engine
│
├── tests/                           # Unit tests (125 tests)
│   ├── conftest.py                  # Shared fixtures (sample data, DB, recommender, clusterer)
│   ├── test_data_cleaning.py        # Tests for SQL cleaning pipeline (32 tests)
│   ├── test_recommender.py          # Tests for recommendation engine (55 tests)
│   └── test_clustering.py           # Tests for clustering module (38 tests)
│
├── models/                          # Trained ML models
│   ├── mood_clusterer.pkl           # Serialized K-means model
│   └── song_recommender.pkl         # Serialized KNN recommender model
│
├── notebooks/
│   └── figures/                     # Generated visualizations
│       ├── cluster_optimization.png
│       └── cluster_visualization.png
│
├── api_server.py                    # Flask REST API (8 endpoints, port 8000)
├── cli_app.py                       # Interactive CLI application (10-option menu)
├── recommender.py                   # Song recommendation engine
├── clustering.py                    # K-means mood clustering
├── data_cleaner.py                  # SQL-based data cleaning
├── data_generator.py                # Data generator with quality issues
├── run_pipeline.py                  # Master pipeline orchestrator
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Pytest configuration
├── vercel.json                      # Vercel deployment config
├── spotify_data.db                  # SQLite database
└── cleaned_spotify_data.csv         # Cleaned CSV (949 songs)
```

---

## Frontend

### Tech Stack

| Technology | Purpose |
|---|---|
| React 18.2 | UI framework |
| TypeScript 5.3 | Type safety |
| Vite 5.0 | Build tool and dev server |
| Tailwind CSS 3.3 | Utility-first styling |
| Zustand 4.4 | Lightweight state management |
| Axios 1.6 | HTTP client for API calls |
| React Router DOM 6.20 | Client-side routing |
| GSAP 3.12 | Animations and scroll triggers |
| ECharts 6.0 | Interactive charts (tempo histogram, mood scatter, artist bars) |
| Radix UI | Accessible UI primitives (dialog, slider, tabs, tooltip, select) |
| Lucide React | Icon library |

### Pages

| Page | Route | Description |
|---|---|---|
| Landing | `/` | Marketing landing page with hero section, benefits grid, mood showcase, feature walkthrough, comparison table, testimonial, and CTA |
| Recommendations | `/recommendations` | Main app page with tabbed filters (By Mood, By Tempo, Mood + Tempo), song card grid, and live analytics dashboard |

### Key Components

| Component | Description |
|---|---|
| `MoodSelector` | 8-mood grid selector (happy, sad, energetic, calm, party, dark, romantic, angry) with icons |
| `SongCard` | Song display with valence/energy progress bars, BPM, similarity score badge, Spotify link, and copy-to-clipboard |
| `AnalyticsDashboard` | Live analytics panel with KPI cards, tempo distribution histogram, valence vs energy scatter plot, top artists bar chart, distribution insights, searchable/sortable result table, CSV/PNG export |

### Deployment

- **Hosted on:** Vercel (static frontend)
- **Config:** `vercel.json` with SPA rewrites for React Router
- **API URL:** Configurable via `VITE_API_URL` environment variable (defaults to `http://localhost:8000`)

---

## Backend

### Flask REST API

**File:** `api_server.py` | **Port:** 8000

| Route | Method | Params | Description |
|---|---|---|---|
| `/health` | GET | - | Health check |
| `/api/moods` | GET | - | List available moods |
| `/api/tempos` | GET | - | List available tempos |
| `/api/recommendations/mood` | GET | `mood`, `count` | Recommend by mood |
| `/api/recommendations/tempo` | GET | `tempo`, `count` | Recommend by tempo |
| `/api/recommendations/combined` | GET | `mood`, `tempo`, `count` | Combined mood + tempo |
| `/api/recommendations/similar` | GET | `song_id`, `method`, `count` | Similar songs (KNN/cosine/euclidean) |
| `/api/songs/search` | GET | `query`, `limit` | Search songs by name/artist |
| `/api/songs/<track_id>` | GET | - | Get single song details |

### Security

| Measure | Description |
|---|---|
| CORS restriction | Origins restricted to allowed list (configurable via `CORS_ORIGINS` env var) |
| Debug mode off | Disabled by default, enabled only via `FLASK_DEBUG=true` env var |
| Localhost binding | Binds to `127.0.0.1` instead of `0.0.0.0` |
| Security headers | `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy` |
| Input validation | `count` clamped to [1, 100], `limit` clamped to [1, 50] |
| ReDoS prevention | `regex=False` on all user-input string searches |
| SQL injection prevention | Table name allowlist, parameterized queries, column name validation |
| Path traversal prevention | Model `load_model()` validates filenames against trusted directory |
| Error sanitization | Generic error messages returned to clients, no internal details leaked |
| Thread safety | `recommend_by_song()` accepts `n_results` param instead of mutating shared state |

### Data Pipeline

| Module | File | Description |
|---|---|---|
| Data Generator | `data_generator.py` | Generates synthetic Spotify songs with audio features (energy, valence, danceability, tempo, etc.). Injects data quality issues (nulls, duplicates, outliers) for pipeline testing. Supports CLI with configurable parameters. Outputs to CSV and SQLite. |
| Data Cleaner | `data_cleaner.py` | SQL-based cleaning using SQLite. Removes duplicates via `ROW_NUMBER()`, imputes missing values with column means, detects/removes outliers, computes summary statistics. Uses context manager pattern for DB connections. Table name allowlist for SQL injection prevention. |
| Clustering | `clustering.py` | `MoodClusterer` class implementing K-means clustering. Selects 5 audio features (valence, energy, danceability, tempo_normalized, acousticness), finds optimal cluster count via silhouette score, generates visualizations, persists models with joblib. |
| Recommender | `recommender.py` | `SongRecommender` class with 4 recommendation modes: by mood (8 moods), by tempo (3 categories), by mood+tempo (combined), and by song similarity (KNN, cosine, euclidean). Normalizes 9 audio features, builds KNN model with cosine distance, persists models with joblib. |
| API Server | `api_server.py` | Flask REST API bridging the React frontend to the SongRecommender backend. 8 endpoints with input validation, security headers, and restricted CORS. |
| CLI App | `cli_app.py` | Interactive terminal application with 10-option menu. Wraps all recommendation and clustering functionality with ANSI-colored output, input validation, and graceful error handling. |
| Pipeline | `run_pipeline.py` | Master orchestrator that runs all pipeline stages in sequence with progress indicators, timing, output verification, and summary generation. |

### Database

- **SQLite** (`spotify_data.db`) with tables: `raw_songs`, `cleaned_songs`
- CSV-based data interchange between pipeline stages

### ML Models

- **K-means Clustering** for mood detection (5 clusters: Energetic & Happy, Calm & Peaceful, Melancholic, Party & Dance, Intense & Dark)
- **KNN** (cosine distance) for song similarity recommendations
- **Cosine Similarity** (sklearn pairwise) as alternative similarity method
- **Euclidean Distance** (scipy spatial) as alternative similarity method

### Backend Packages

| Package | Purpose |
|---|---|
| `flask` | REST API web framework |
| `flask-cors` | Cross-origin resource sharing |
| `pandas` | DataFrames, CSV I/O, data manipulation |
| `numpy` | Numerical operations, random data generation |
| `scikit-learn` | K-means clustering, StandardScaler, KNN, silhouette/Davies-Bouldin metrics |
| `scipy` | Scientific computing, distance calculations |
| `joblib` | Model serialization (save/load .pkl files) |
| `spotipy` | Spotify Web API wrapper (planned) |
| `requests` | HTTP client for API calls |
| `python-dotenv` | Environment variable management (.env loading) |
| `sqlite3` | Database engine (stdlib) |
| `matplotlib` | Static charts (cluster optimization, scatter plots) |
| `seaborn` | Statistical visualization (cluster coloring, palettes) |
| `plotly` | Interactive charts |

---

## Data Model

Each song record contains:

| Field | Type | Range | Description |
|---|---|---|---|
| `track_id` | string | - | Unique identifier |
| `track_name` | string | - | Song title |
| `artist` | string | - | Artist name |
| `album` | string | - | Album name |
| `valence` | float | 0.0 - 1.0 | Happiness / positivity |
| `energy` | float | 0.0 - 1.0 | Intensity / activity |
| `danceability` | float | 0.0 - 1.0 | Dance suitability |
| `tempo` | float | 60 - 200 | BPM |
| `acousticness` | float | 0.0 - 1.0 | Acoustic vs electronic |
| `instrumentalness` | float | 0.0 - 1.0 | Vocal presence |
| `liveness` | float | 0.0 - 1.0 | Live audience presence |
| `speechiness` | float | 0.0 - 1.0 | Spoken word content |
| `loudness` | float | -30 - 0 | Volume in dB |
| `popularity` | int | 0 - 100 | Popularity score |
| `year` | int | 2015 - 2024 | Release year |
| `spotify_url` | string | - | Link to Spotify track |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `FLASK_DEBUG` | `false` | Enable Flask debug mode (`true`/`false`) |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Comma-separated allowed CORS origins |
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL for the frontend |

When Spotify API integration is added, the following will also be required:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

Currently data is sourced from Kaggle (CSV); no API credentials are needed.

---

## Setup

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

---

## Usage

### Run the full-stack app (development)

```bash
# Terminal 1: Start the Flask API
python3 api_server.py

# Terminal 2: Start the React frontend
cd frontend && npm run dev
```

The frontend runs at `http://localhost:5173` and proxies API calls to `http://localhost:8000`.

### Run the data pipeline

```bash
# Run the full pipeline
python3 run_pipeline.py

# Run individual modules
python3 data_generator.py
python3 data_cleaner.py
python3 clustering.py
python3 recommender.py

# Skip specific steps
python3 run_pipeline.py --skip-generate
python3 run_pipeline.py --skip-eda
python3 run_pipeline.py --only recommender
```

### Launch interactive CLI

```bash
python3 cli_app.py
```

```
=== VibeMap ===
1. Recommend by Mood        (8 moods: happy, sad, energetic, calm, dark, romantic, angry, party)
2. Recommend by Tempo        (slow <= 100 BPM, medium 100-120, fast >= 120)
3. Recommend by Mood + Tempo (combined filtering)
4. Recommend by Song         (find similar via KNN/cosine/euclidean)
5. Search Songs              (case-insensitive search by track name or artist)
6. View Available Moods      (list moods with filter criteria and song counts)
7. View Available Tempos     (list tempo categories with BPM ranges)
8. View Mood Clusters        (K-means cluster stats and sample songs)
9. Help
0. Exit
```

### Run tests

```bash
pytest tests/ -v
pytest tests/ --cov=data_cleaner --cov=recommender --cov=clustering --cov-report=term-missing
```

---

## Testing

| Test File | Module Tested | Tests | Coverage |
|---|---|---|---|
| `test_data_cleaning.py` | `data_cleaner.py` | 32 | 90% |
| `test_recommender.py` | `recommender.py` | 55 | 77% |
| `test_clustering.py` | `clustering.py` | 38 | 93% |
| **Total** | | **125** | **88%** |

Tests cover:
- All 8 mood filters with threshold validation
- All 3 tempo categories with BPM range checks
- All 3 similarity methods (KNN, cosine, euclidean) with score bound checks
- SQL cleaning operations (dedup, null fills, outlier removal)
- Model save/load using `tmp_path` fixtures
- Edge cases: invalid inputs, empty results, missing columns, unloaded state
- Cluster interpretation for all 7 mood categories
- Shared fixtures in `conftest.py` (sample DataFrames, SQLite DBs, pre-built recommender/clusterer)

---

## Development & Testing Packages

| Package | Purpose |
|---|---|
| `pytest` | Test framework (125 test cases across 3 files) |
| `pytest-cov` | Test coverage reporting (88% overall) |
| `black` | Code formatter |
| `flake8` | Linting and style checking |

---

## Deployment

| Component | Platform | Notes |
|---|---|---|
| Frontend | Vercel | Static site with SPA rewrites via `vercel.json` |
| Backend | Local / Render / Railway | Flask API requires Python runtime (not supported on Vercel) |
| Database | SQLite (bundled) | Ships with the backend |

### Vercel Environment Variables

Set in Vercel Dashboard > Project > Settings > Environment Variables:

| Variable | Value |
|---|---|
| `VITE_API_URL` | URL of your deployed Flask backend (e.g., `https://vibemap-api.onrender.com`) |

---

## Implementation Status

| Component | Status |
|---|---|
| Data Generator | Done |
| Data Cleaner (SQL) | Done |
| K-means Clustering | Done |
| Song Recommender | Done |
| CLI Application | Done |
| Unit Tests (125 tests, 88% coverage) | Done |
| Pytest Configuration | Done |
| Flask REST API (8 endpoints) | Done |
| React Frontend (Vite + TypeScript) | Done |
| Live Analytics Dashboard (ECharts) | Done |
| Security Hardening | Done |
| Vercel Deployment (frontend) | Done |
| Backend Deployment (Render/Railway) | Not started |
| Spotify API Integration | Not started |
| CI/CD Pipeline | Not started |
| Docker Deployment | Not started |
