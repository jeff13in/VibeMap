# VibeMap 🎵

VibeMap is an end-to-end **music recommendation system** that suggests songs based on **mood** and **tempo**.  
The project is built using **Python, SQL, and machine learning**, following a **2-sprint (10-day) agile workflow** by a **Software Engineer and a Data Scientist**.

---

## Features

- Synthetic Spotify-style dataset generation
- SQL-based data cleaning and validation
- Exploratory Data Analysis (EDA) with visualizations
- Mood-based clustering using K-Means
- Multi-algorithm recommendation engine:
  - K-Nearest Neighbors (KNN)
  - Cosine Similarity
  - Euclidean Distance
- Interactive Command Line Interface (CLI)
- Streamlit web application (Sprint 2)
- Automated testing and CI/CD pipeline

---

## Tech Stack

- **Language**: Python 3.8+
- **Data**: Pandas, NumPy, SQLite
- **Machine Learning**: scikit-learn, SciPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Testing**: Pytest
- **Web UI**: Streamlit
- **CI/CD**: GitHub Actions

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

### 2. Run Full Pipeline
```bash
python run_pipeline.py

### 3. Run CLI Application
```bash
python -m src.cli_app

### 4. Run Streamlit Web App 
```bash
streamlit run src/streamlit_app.py

### 5.Testing
Run all unit tests: pytest -v
Run tests with coverage: pytest --cov=src --cov-report=term-missing

### Core Modules

Data Generation: data_generator.py
Generates realistic Spotify-like song data and stores it in CSV and SQLite.

Data Cleaning: data_cleaner.py
Performs SQL-based cleaning (duplicates, nulls, outliers, validation).

EDA: exploratory_analysis.py
Statistical analysis and visualizations of audio features.

Clustering: clustering.py
K-Means clustering to group songs into mood-based clusters.

Recommendation Engine: recommender.py
Provides similarity-based recommendations using multiple algorithms.

CLI: cli_app.py
Interactive terminal interface for recommendations.

Web App: streamlit_app.py
User-friendly Streamlit interface with interactive charts.



