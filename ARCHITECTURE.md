# VibeMap - System Architecture

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            USER                                         │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Vercel)                                   │
│                                                                         │
│  React 18 + TypeScript + Vite + Tailwind CSS                           │
│                                                                         │
│  ┌──────────┐   ┌──────────────────┐   ┌────────────────────┐          │
│  │ Landing  │   │ Recommendations  │   │AnalyticsDashboard  │          │
│  │  Page    │──▶│     Page         │──▶│   (ECharts)        │          │
│  └──────────┘   └────────┬─────────┘   └────────────────────┘          │
│                          │                                              │
│              ┌───────────▼───────────┐                                  │
│              │  useRecommendations   │  (Custom Hook)                   │
│              └───────────┬───────────┘                                  │
│                          │                                              │
│              ┌───────────▼───────────┐                                  │
│              │  Zustand Store        │  (State Management)              │
│              └───────────┬───────────┘                                  │
│                          │                                              │
│              ┌───────────▼───────────┐                                  │
│              │  Axios API Client     │  (lib/api.ts)                    │
│              │  Timeout: 60s         │                                  │
│              └───────────┬───────────┘                                  │
└──────────────────────────┼──────────────────────────────────────────────┘
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      BACKEND (Render)                                   │
│                                                                         │
│  Flask + Gunicorn (2 workers, 120s timeout)                            │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                   api_server.py                               │       │
│  │                                                               │       │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐   │       │
│  │  │ CORS        │  │ Security     │  │ Input Validation  │   │       │
│  │  │ Middleware   │  │ Headers      │  │ & Clamping        │   │       │
│  │  └─────────────┘  └──────────────┘  └───────────────────┘   │       │
│  │                                                               │       │
│  │  Routes:                                                      │       │
│  │  GET /health                    GET /api/moods                │       │
│  │  GET /api/tempos                GET /api/songs/search         │       │
│  │  GET /api/songs/<id>            GET /api/recommendations/*    │       │
│  └──────────────────────────┬───────────────────────────────────┘       │
│                             │                                           │
│                  ┌──────────▼──────────┐                                │
│                  │  SongRecommender    │  (recommender.py)              │
│                  │                     │                                │
│                  │  • 8 Mood Filters   │                                │
│                  │  • 3 Tempo Filters  │                                │
│                  │  • KNN Model        │                                │
│                  │  • Cosine Similarity│                                │
│                  │  • Euclidean Dist.  │                                │
│                  └──────────┬──────────┘                                │
│                             │                                           │
│              ┌──────────────▼──────────────┐                            │
│              │       SQLite Database       │                            │
│              │      (spotify_data.db)      │                            │
│              │                              │                            │
│              │  ┌──────────┐ ┌───────────┐ │                            │
│              │  │raw_songs │ │cleaned_   │ │                            │
│              │  │          │ │songs      │ │                            │
│              │  └──────────┘ └───────────┘ │                            │
│              └─────────────────────────────┘                            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     main.tsx (Entry)                         │
│                         │                                    │
│                    ┌────▼────┐                               │
│                    │ App.tsx │                               │
│                    │ Router  │                               │
│                    └────┬────┘                               │
│                         │                                    │
│           ┌─────────────┼─────────────┐                     │
│           ▼             ▼             ▼                      │
│    ┌────────────┐ ┌───────────┐ ┌──────────┐               │
│    │  Landing   │ │  Recom-   │ │  Home    │               │
│    │  (/)      │ │  menda-   │ │  (/home) │               │
│    │           │ │  tions    │ │          │               │
│    └────────────┘ └─────┬─────┘ └──────────┘               │
│                         │                                    │
│         ┌───────────────┼───────────────┐                   │
│         ▼               ▼               ▼                   │
│  ┌─────────────┐ ┌───────────┐ ┌──────────────────┐       │
│  │MoodSelector │ │ SongCard  │ │AnalyticsDashboard│       │
│  │ (8 moods)   │ │ (results) │ │ (ECharts)        │       │
│  └─────────────┘ └───────────┘ └──────────────────┘       │
│                                                              │
│  Layout:  ┌──────────┐  ┌──────────┐                       │
│           │ Header   │  │ Footer   │                       │
│           └──────────┘  └──────────┘                       │
│                                                              │
│  UI Primitives (Radix/Shadcn):                              │
│  button │ card │ tabs │ slider │ badge │ input              │
└─────────────────────────────────────────────────────────────┘
```

### State & Data Flow

```
  User Action (select mood/tempo)
         │
         ▼
┌─────────────────┐     ┌──────────────────────┐
│  Recommendations│────▶│  useRecommendations  │
│  Page           │     │  (Custom Hook)       │
└─────────────────┘     └──────────┬───────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   Zustand Store              │
                    │                              │
                    │  recommendations: Song[]     │
                    │  loading: boolean            │
                    │  error: string | null        │
                    │  filters: {                  │
                    │    mood: MoodType            │
                    │    tempo: TempoType          │
                    │    count: number             │
                    │    algorithm: AlgorithmType  │
                    │  }                           │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  Axios Client (lib/api.ts)  │
                    │  Base: VITE_API_URL         │
                    │  Timeout: 60s               │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                          Flask REST API
```

---

## API Endpoints

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flask REST API                            │
│                      (api_server.py:8000)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Health & Metadata                                               │
│  ─────────────────                                               │
│  GET /              → { status, songs_loaded }                   │
│  GET /health        → { status, songs_loaded }                   │
│  GET /api/moods     → { moods: string[] }                        │
│  GET /api/tempos    → { tempos: string[] }                       │
│                                                                  │
│  Recommendations                                                 │
│  ───────────────                                                 │
│  GET /api/recommendations/mood                                   │
│      ?mood={happy|sad|energetic|calm|party|dark|romantic|angry}  │
│      &count={1-100}                                              │
│                                                                  │
│  GET /api/recommendations/tempo                                  │
│      ?tempo={slow|medium|fast}                                   │
│      &count={1-100}                                              │
│                                                                  │
│  GET /api/recommendations/combined                               │
│      ?mood={...}&tempo={...}&count={1-100}                       │
│                                                                  │
│  GET /api/recommendations/similar                                │
│      ?song_id={id}&method={knn|cosine|euclidean}&count={1-100}  │
│                                                                  │
│  Search & Details                                                │
│  ────────────────                                                │
│  GET /api/songs/search  ?query={text}&limit={1-50}              │
│  GET /api/songs/<track_id>                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Pipeline

```
┌───────────────────────┐
│  Kaggle CSV           │
│  (1000 Spotify tracks)│
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐     ┌────────────────────────────────┐
│  data_generator.py    │     │  Injects quality issues:       │
│                       │────▶│  • Nulls / missing values      │
│  Synthetic audio      │     │  • Duplicate records           │
│  feature generation   │     │  • Outliers                    │
└──────────┬────────────┘     └────────────────────────────────┘
           │
           ▼
    ┌──────────────┐
    │  SQLite DB   │
    │  raw_songs   │
    └──────┬───────┘
           │
           ▼
┌───────────────────────┐     ┌────────────────────────────────┐
│  data_cleaner.py      │     │  SQL Operations:               │
│                       │────▶│  • ROW_NUMBER() dedup          │
│  SpotifyDataCleaner   │     │  • Mean imputation             │
│  (SQL-based)          │     │  • Outlier removal             │
└──────────┬────────────┘     └────────────────────────────────┘
           │
           ▼
    ┌──────────────┐     ┌──────────────────────┐
    │  SQLite DB   │     │ cleaned_spotify_     │
    │  cleaned_    │────▶│ data.csv             │
    │  songs       │     └──────────────────────┘
    └──────┬───────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌──────────┐ ┌──────────────┐
│clustering│ │recommender.py│
│.py       │ │              │
└────┬─────┘ └──────┬───────┘
     │               │
     ▼               ▼
┌──────────┐ ┌──────────────┐
│mood_     │ │song_         │
│clusterer │ │recommender   │
│.pkl      │ │.pkl          │
└──────────┘ └──────────────┘
```

---

## ML Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLUSTERING MODULE                            │
│                     (clustering.py)                               │
│                                                                  │
│  Features: valence, energy, danceability, tempo_norm,            │
│            acousticness                                          │
│                                                                  │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────────┐   │
│  │ Feature     │───▶│ Find Optimal │───▶│ K-Means           │   │
│  │ Selection & │    │ k (2-10)     │    │ Clustering        │   │
│  │ Scaling     │    │ Silhouette   │    │ (5 clusters)      │   │
│  └─────────────┘    └──────────────┘    └─────────┬─────────┘   │
│                                                   │              │
│                                         ┌─────────▼─────────┐   │
│                                         │ Cluster Labels:   │   │
│                                         │                   │   │
│                                         │ 0: Energetic &    │   │
│                                         │    Happy          │   │
│                                         │ 1: Calm &         │   │
│                                         │    Peaceful       │   │
│                                         │ 2: Melancholic    │   │
│                                         │ 3: Party & Dance  │   │
│                                         │ 4: Intense & Dark │   │
│                                         └───────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   RECOMMENDATION MODULE                          │
│                   (recommender.py)                                │
│                                                                  │
│  9 Features: valence, energy, danceability, tempo_norm,          │
│              acousticness, instrumentalness, liveness,           │
│              speechiness, loudness_norm                          │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │              SongRecommender                              │   │
│  │                                                           │   │
│  │  ┌─────────────────┐   ┌─────────────────────────────┐   │   │
│  │  │  Filter-based   │   │  Similarity-based           │   │   │
│  │  │                 │   │                             │   │   │
│  │  │  By Mood (8)    │   │  KNN (cosine distance)     │   │   │
│  │  │  By Tempo (3)   │   │  Cosine Similarity         │   │   │
│  │  │  Combined       │   │  Euclidean Distance        │   │   │
│  │  └─────────────────┘   └─────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Mood Filter Thresholds

```
┌────────────┬───────────────────────────────────────────┐
│   Mood     │   Filter Criteria                         │
├────────────┼───────────────────────────────────────────┤
│ Happy      │ valence ≥ 0.6  AND  energy ≥ 0.5         │
│ Sad        │ valence ≤ 0.4  AND  energy ≤ 0.4         │
│ Energetic  │ energy ≥ 0.7   AND  danceability ≥ 0.5   │
│ Calm       │ energy ≤ 0.4   AND  acousticness ≥ 0.5   │
│ Dark       │ valence ≤ 0.3  AND  energy ≥ 0.6         │
│ Romantic   │ valence ≥ 0.5  AND  acousticness ≥ 0.4   │
│            │                AND  energy ≤ 0.6          │
│ Angry      │ energy ≥ 0.7   AND  valence ≤ 0.4        │
│ Party      │ danceability ≥ 0.7 AND energy ≥ 0.6      │
│            │                AND  valence ≥ 0.5         │
├────────────┼───────────────────────────────────────────┤
│ Slow       │ tempo ≤ 100 BPM                          │
│ Medium     │ 100 < tempo < 120 BPM                    │
│ Fast       │ tempo ≥ 120 BPM                          │
└────────────┴───────────────────────────────────────────┘
```

---

## Deployment Architecture

```
┌──────────────────┐         ┌──────────────────────────────┐
│                  │  HTTPS  │                              │
│     Browser      │◀───────▶│        Vercel CDN            │
│                  │         │                              │
│                  │         │  React SPA (Static)          │
│                  │         │  • HTML/CSS/JS bundle        │
│                  │         │  • SPA rewrites (vercel.json)│
│                  │         │  • Env: VITE_API_URL         │
└──────────────────┘         └──────────────────────────────┘
                                        │
                                        │ API Calls (HTTPS)
                                        ▼
                             ┌──────────────────────────────┐
                             │       Render (Free Tier)     │
                             │                              │
                             │  Gunicorn + Flask            │
                             │  • 2 Workers                 │
                             │  • 120s Timeout              │
                             │  • Python 3.11               │
                             │  • Root: /backend            │
                             │                              │
                             │  ┌────────────────────────┐  │
                             │  │    api_server.py       │  │
                             │  │                        │  │
                             │  │  ┌──────────────────┐  │  │
                             │  │  │ SongRecommender  │  │  │
                             │  │  └────────┬─────────┘  │  │
                             │  │           │            │  │
                             │  │  ┌────────▼─────────┐  │  │
                             │  │  │  SQLite DB       │  │  │
                             │  │  │  (bundled)       │  │  │
                             │  │  └──────────────────┘  │  │
                             │  └────────────────────────┘  │
                             └──────────────────────────────┘
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: CORS                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Allowed Origins (configurable via CORS_ORIGINS):    │    │
│  │ • http://localhost:5173 (dev frontend)              │    │
│  │ • http://localhost:3000 (alt dev)                   │    │
│  │ • Production Vercel URL                             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 2: Security Headers                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ X-Content-Type-Options: nosniff                     │    │
│  │ X-Frame-Options: DENY                               │    │
│  │ X-XSS-Protection: 1; mode=block                     │    │
│  │ Referrer-Policy: strict-origin-when-cross-origin    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 3: Input Validation                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • count clamped to [1, 100]                         │    │
│  │ • limit clamped to [1, 50]                          │    │
│  │ • query length capped at 200 chars                  │    │
│  │ • mood/tempo validated against allowed lists        │    │
│  │ • regex=False on string searches (ReDoS prevention) │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 4: Data Safety                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • SQL: Table name allowlist, parameterized queries  │    │
│  │ • Models: Path traversal prevention on load         │    │
│  │ • Errors: Sanitized messages, no internal leaks     │    │
│  │ • Debug: Disabled by default                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND                        │  BACKEND                 │
├──────────────────────────────────┼──────────────────────────┤
│  React 18          UI Framework  │  Flask        Web API    │
│  TypeScript 5.3    Type Safety   │  Gunicorn     WSGI       │
│  Vite 5.0          Build Tool    │  SQLite       Database   │
│  Tailwind CSS 3.3  Styling       │  Pandas       DataFrames │
│  Zustand 4.4       State Mgmt   │  Scikit-learn ML Models  │
│  Axios 1.6         HTTP Client   │  SciPy        Distances  │
│  React Router 6    Routing       │  Joblib       Model I/O  │
│  ECharts 6.0       Charts        │  NumPy        Numerics   │
│  GSAP 3.12         Animations    │  Matplotlib   Plots      │
│  Radix UI          Primitives    │  Flask-CORS   CORS       │
│  Lucide React      Icons         │  python-dotenv Env Vars  │
├──────────────────────────────────┼──────────────────────────┤
│  DEPLOYMENT                      │  TESTING                 │
├──────────────────────────────────┼──────────────────────────┤
│  Vercel            Frontend CDN  │  Pytest       Framework  │
│  Render            Backend Host  │  pytest-cov   Coverage   │
│  GitHub            Source Ctrl   │  125 tests    Total      │
│                                  │  88%          Coverage   │
└──────────────────────────────────┴──────────────────────────┘
```
