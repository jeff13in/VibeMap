"""
VibeMap CLI Application
Interactive terminal menu for song recommendations and mood clustering.
"""

import pandas as pd
from pathlib import Path

# Import modules from project root (NO src/ package needed)
from recommender import SongRecommender
from clustering import MoodClusterer

# ---------------------------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------------------------

COLORS = {
    'cyan':    '\033[96m',
    'green':   '\033[92m',
    'yellow':  '\033[93m',
    'red':     '\033[91m',
    'magenta': '\033[95m',
    'bold':    '\033[1m',
    'reset':   '\033[0m',
}


def color(text, c):
    return f"{COLORS.get(c, '')}{text}{COLORS['reset']}"


def print_header(text):
    width = max(len(text) + 4, 40)
    print()
    print(color('=' * width, 'cyan'))
    print(color(f"  {text}", 'cyan'))
    print(color('=' * width, 'cyan'))


def print_table(df, columns=None, index_label='#'):
    """Print a DataFrame as a numbered table."""
    if df.empty:
        print(color("  No results found.", 'yellow'))
        return
    display = df.copy()
    if columns:
        columns = [c for c in columns if c in display.columns]
        display = display[columns]
    display = display.reset_index(drop=True)
    display.index = display.index + 1
    display.index.name = index_label
    print(display.to_string())


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def get_choice(prompt_text, valid_range):
    """Prompt for a numeric choice within valid_range. Returns int."""
    while True:
        try:
            raw = input(prompt_text).strip()
        except (KeyboardInterrupt, EOFError):
            raise
        if raw == '':
            continue
        try:
            val = int(raw)
        except ValueError:
            print(color(f"  Invalid input. Enter a number between {valid_range[0]} and {valid_range[-1]}.", 'red'))
            continue
        if val not in valid_range:
            print(color(f"  Out of range. Enter a number between {valid_range[0]} and {valid_range[-1]}.", 'red'))
            continue
        return val


def get_number(prompt_text, default=5):
    """Prompt for a positive integer with a default value."""
    while True:
        try:
            raw = input(prompt_text).strip()
        except (KeyboardInterrupt, EOFError):
            raise
        if raw == '':
            return default
        try:
            val = int(raw)
        except ValueError:
            print(color(f"  Invalid input. Enter a positive integer (default: {default}).", 'red'))
            continue
        if val <= 0:
            print(color(f"  Must be a positive integer (default: {default}).", 'red'))
            continue
        return val


# ---------------------------------------------------------------------------
# Data loading / initialization
# ---------------------------------------------------------------------------

def load_data():
    """Load CSV, initialize SongRecommender and MoodClusterer. Returns (rec, clusterer)."""
    project_root = Path(__file__).resolve().parent
    data_path = project_root / 'cleaned_spotify_data.csv'

    if not data_path.exists():
        print(color(f"  Data file not found: {data_path}", 'red'))
        raise FileNotFoundError(f"Missing data file: {data_path}")

    df = pd.read_csv(data_path)

    # Rename id -> track_id to match SongRecommender expectations
    if 'id' in df.columns and 'track_id' not in df.columns:
        df = df.rename(columns={'id': 'track_id'})

    # --- SongRecommender setup (mirrors recommender.py behavior) ---
    rec = SongRecommender(n_recommendations=10)
    rec.df = df.copy()

    rec.feature_names = [
        'valence', 'energy', 'danceability', 'tempo',
        'acousticness', 'instrumentalness', 'liveness',
        'speechiness', 'loudness',
    ]

    missing = [c for c in rec.feature_names if c not in rec.df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    rec.df = rec.df.dropna(subset=rec.feature_names).reset_index(drop=True)

    # Avoid divide-by-zero for constant columns
    tempo_range = rec.df['tempo'].max() - rec.df['tempo'].min()
    loud_range = rec.df['loudness'].max() - rec.df['loudness'].min()

    rec.df['tempo_normalized'] = (
        (rec.df['tempo'] - rec.df['tempo'].min()) / tempo_range
        if tempo_range != 0 else 0.0
    )
    rec.df['loudness_normalized'] = (
        (rec.df['loudness'] - rec.df['loudness'].min()) / loud_range
        if loud_range != 0 else 0.0
    )

    feature_cols = [
        'valence', 'energy', 'danceability', 'tempo_normalized',
        'acousticness', 'instrumentalness', 'liveness',
        'speechiness', 'loudness_normalized',
    ]

    rec.feature_matrix = rec.df[feature_cols].values
    rec.feature_matrix_scaled = rec.scaler.fit_transform(rec.feature_matrix)

    # If dataset is tiny, ensure at least 1 neighbor
    n_neighbors = 1 if len(rec.df) <= 2 else min(10, len(rec.df) - 1)
    rec.build_knn_model(n_neighbors=n_neighbors)

    # --- MoodClusterer setup ---
    clusterer = MoodClusterer(n_clusters=5, random_state=42)

    return rec, clusterer


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------

def recommend_by_mood(rec):
    print_header("Recommend by Mood")
    moods = list(rec.MOOD_FILTERS.keys())
    for i, m in enumerate(moods, 1):
        print(f"  {i}. {m.capitalize()}")
    choice = get_choice(color("\n  Pick a mood: ", 'magenta'), range(1, len(moods) + 1))
    mood = moods[choice - 1]
    n = get_number(color("  How many songs? [5]: ", 'magenta'))
    results = rec.recommend_by_mood(mood, n_songs=n)
    print(color(f"\n  {mood.capitalize()} songs ({len(results)} results):", 'green'))
    print_table(results, ['track_name', 'artist', 'valence', 'energy', 'danceability', 'tempo'])


def recommend_by_tempo(rec):
    print_header("Recommend by Tempo")
    tempos = list(rec.TEMPO_FILTERS.keys())
    descriptions = {'slow': '<= 100 BPM', 'medium': '100-120 BPM', 'fast': '>= 120 BPM'}
    for i, t in enumerate(tempos, 1):
        print(f"  {i}. {t.capitalize()} ({descriptions.get(t, '')})")
    choice = get_choice(color("\n  Pick a tempo: ", 'magenta'), range(1, len(tempos) + 1))
    tempo = tempos[choice - 1]
    n = get_number(color("  How many songs? [5]: ", 'magenta'))
    results = rec.recommend_by_tempo(tempo, n_songs=n)
    print(color(f"\n  {tempo.capitalize()} songs ({len(results)} results):", 'green'))
    print_table(results, ['track_name', 'artist', 'valence', 'energy', 'danceability', 'tempo'])


def recommend_by_mood_and_tempo(rec):
    print_header("Recommend by Mood + Tempo")
    moods = list(rec.MOOD_FILTERS.keys())
    tempos = list(rec.TEMPO_FILTERS.keys())
    descriptions = {'slow': '<= 100 BPM', 'medium': '100-120 BPM', 'fast': '>= 120 BPM'}

    print("  Moods:")
    for i, m in enumerate(moods, 1):
        print(f"    {i}. {m.capitalize()}")
    mood_choice = get_choice(color("\n  Pick a mood: ", 'magenta'), range(1, len(moods) + 1))
    mood = moods[mood_choice - 1]

    print("\n  Tempos:")
    for i, t in enumerate(tempos, 1):
        print(f"    {i}. {t.capitalize()} ({descriptions.get(t, '')})")
    tempo_choice = get_choice(color("\n  Pick a tempo: ", 'magenta'), range(1, len(tempos) + 1))
    tempo = tempos[tempo_choice - 1]

    n = get_number(color("  How many songs? [5]: ", 'magenta'))
    results = rec.recommend_by_mood_and_tempo(mood, tempo, n_songs=n)
    print(color(f"\n  {mood.capitalize()} + {tempo.capitalize()} songs ({len(results)} results):", 'green'))
    print_table(results, ['track_name', 'artist', 'valence', 'energy', 'danceability', 'tempo'])


def recommend_by_song(rec):
    print_header("Recommend by Song (Find Similar)")
    query = input(color("  Search for a song: ", 'magenta')).strip()
    if not query:
        print(color("  Empty search query.", 'yellow'))
        return

    mask = (
        rec.df['track_name'].str.contains(query, case=False, na=False) |
        rec.df['artist'].str.contains(query, case=False, na=False)
    )
    matches = rec.df[mask]
    if matches.empty:
        print(color(f"  No songs found matching '{query}'.", 'yellow'))
        return

    shown = matches.head(20)
    print(color(f"\n  Found {len(matches)} match(es). Showing top {len(shown)}:", 'green'))
    print_table(shown, ['track_name', 'artist'])

    pick = get_choice(color(f"\n  Pick a song number (1-{len(shown)}): ", 'magenta'), range(1, len(shown) + 1))
    song_row = shown.iloc[pick - 1]
    song_id = song_row['track_id']

    print(f"\n  Seed: {color(song_row['track_name'], 'magenta')} by {song_row['artist']}")

    methods = ['knn', 'cosine', 'euclidean']
    print("\n  Similarity method:")
    for i, m in enumerate(methods, 1):
        print(f"    {i}. {m.upper()}")
    method_choice = get_choice(color("  Pick method: ", 'magenta'), range(1, len(methods) + 1))
    method = methods[method_choice - 1]

    results = rec.recommend_by_song(song_id, method=method)
    print(color(f"\n  Similar songs ({method.upper()}):", 'green'))
    print_table(results, ['track_name', 'artist', 'similarity_score'])


def search_songs(rec):
    print_header("Search Songs")
    query = input(color("  Search (track name or artist): ", 'magenta')).strip()
    if not query:
        print(color("  Empty search query.", 'yellow'))
        return

    mask = (
        rec.df['track_name'].str.contains(query, case=False, na=False) |
        rec.df['artist'].str.contains(query, case=False, na=False)
    )
    matches = rec.df[mask]
    if matches.empty:
        print(color(f"  No songs found matching '{query}'.", 'yellow'))
        return

    print(color(f"\n  Found {len(matches)} result(s):", 'green'))
    cols = ['track_name', 'artist']
    if 'album' in matches.columns:
        cols.append('album')
    if 'popularity' in matches.columns:
        cols.append('popularity')
    print_table(matches.head(25), cols)


def view_moods(rec):
    print_header("Available Moods")
    mood_descriptions = {
        'happy':     'valence >= 0.6, energy >= 0.5',
        'sad':       'valence <= 0.4, energy <= 0.4',
        'energetic': 'energy >= 0.7, danceability >= 0.5',
        'calm':      'energy <= 0.4, acousticness >= 0.5',
        'dark':      'valence <= 0.3, energy >= 0.6',
        'romantic':  'valence >= 0.5, acousticness >= 0.4, energy <= 0.6',
        'angry':     'energy >= 0.7, valence <= 0.4',
        'party':     'danceability >= 0.7, energy >= 0.6, valence >= 0.5',
    }
    for mood in rec.MOOD_FILTERS:
        desc = mood_descriptions.get(mood, str(rec.MOOD_FILTERS[mood]))
        count = rec._apply_mood_filter(mood).sum()
        print(f"  {color(mood.capitalize(), 'magenta'):30s}  {desc}  ({count} songs)")


def view_tempos(rec):
    print_header("Available Tempos")
    tempo_info = {
        'slow':   '<= 100 BPM',
        'medium': '100 - 120 BPM',
        'fast':   '>= 120 BPM',
    }
    for t in rec.TEMPO_FILTERS:
        count = rec._apply_tempo_filter(t).sum()
        print(f"  {color(t.capitalize(), 'magenta'):30s}  {tempo_info.get(t, '')}  ({count} songs)")


def view_clusters(rec, clusterer):
    print_header("Mood Clusters")
    print("  Fitting clusters on the dataset...")

    import matplotlib
    orig_backend = matplotlib.get_backend()
    matplotlib.use('Agg')

    df_clustered, _ = clusterer.fit(rec.df, auto_optimize=False)

    matplotlib.use(orig_backend)

    clusterer.analyze_clusters(df_clustered)

    rows = []
    for cid in sorted(df_clustered['cluster'].unique()):
        label = clusterer.cluster_labels.get(cid, f'Cluster {cid}')
        subset = df_clustered[df_clustered['cluster'] == cid]
        rows.append({
            'Cluster': label,
            '# Songs': len(subset),
            'Avg Valence': round(subset['valence'].mean(), 3),
            'Avg Energy': round(subset['energy'].mean(), 3),
            'Avg Danceability': round(subset['danceability'].mean(), 3),
            'Avg Tempo': round(subset['tempo'].mean(), 1),
        })

    summary = pd.DataFrame(rows)
    print(color("\n  Cluster Summary:", 'green'))
    print_table(summary, list(summary.columns))

    print(color("\n  Sample songs per cluster:", 'green'))
    for cid in sorted(df_clustered['cluster'].unique()):
        label = clusterer.cluster_labels.get(cid, f'Cluster {cid}')
        subset = df_clustered[df_clustered['cluster'] == cid]
        samples = subset.head(3)
        print(f"\n  {color(label, 'magenta')}:")
        for _, row in samples.iterrows():
            print(f"    - {row['track_name']} by {row['artist']}")


def show_help():
    print_header("Help")
    help_text = [
        ("1. Recommend by Mood",
         "Pick one of 8 moods (happy, sad, energetic, calm, dark, romantic, angry, party) "
         "and get songs matching that mood's audio feature thresholds."),
        ("2. Recommend by Tempo",
         "Pick a tempo category (slow/medium/fast) to filter songs by BPM range."),
        ("3. Recommend by Mood + Tempo",
         "Combine a mood and tempo filter for more targeted results."),
        ("4. Recommend by Song",
         "Search for a song, then find similar tracks using KNN, cosine similarity, "
         "or euclidean distance on audio features."),
        ("5. Search Songs",
         "Search by track name or artist (case-insensitive substring match)."),
        ("6. View Available Moods",
         "List all 8 moods with their filter criteria and song counts."),
        ("7. View Available Tempos",
         "List the 3 tempo categories with BPM ranges and song counts."),
        ("8. View Mood Clusters",
         "Run K-means clustering (k=5) on the dataset and display cluster stats "
         "with sample songs."),
        ("9. Help",
         "Show this help guide."),
        ("0. Exit",
         "Quit the application."),
    ]
    for title, desc in help_text:
        print(f"  {color(title, 'magenta')}")
        print(f"    {desc}")
        print()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

MENU = """
  1. Recommend by Mood
  2. Recommend by Tempo
  3. Recommend by Mood + Tempo
  4. Recommend by Song (find similar)
  5. Search Songs
  6. View Available Moods
  7. View Available Tempos
  8. View Mood Clusters
  9. Help
  0. Exit
"""


def main():
    print(color('\n' + '=' * 40, 'cyan'))
    print(color('         === VibeMap ===', 'cyan'))
    print(color('=' * 40, 'cyan'))
    print("  Loading data and building models...")

    rec, clusterer = load_data()

    print(color(f"  Dataset: {len(rec.df)} songs loaded", 'green'))
    print(color(f"  Features: {len(rec.feature_names)} audio features", 'green'))
    print(color(f"  Moods: {len(rec.MOOD_FILTERS)} | Tempos: {len(rec.TEMPO_FILTERS)}", 'green'))

    actions = {
        1: lambda: recommend_by_mood(rec),
        2: lambda: recommend_by_tempo(rec),
        3: lambda: recommend_by_mood_and_tempo(rec),
        4: lambda: recommend_by_song(rec),
        5: lambda: search_songs(rec),
        6: lambda: view_moods(rec),
        7: lambda: view_tempos(rec),
        8: lambda: view_clusters(rec, clusterer),
        9: lambda: show_help(),
    }

    while True:
        print(color("\n--- VibeMap Menu ---", 'cyan'))
        print(MENU)

        try:
            choice = get_choice(color("  Enter choice: ", 'magenta'), range(0, 10))
        except (KeyboardInterrupt, EOFError):
            print(color("\n  Goodbye!", 'green'))
            break

        if choice == 0:
            print(color("\n  Goodbye!", 'green'))
            break

        try:
            actions[choice]()
        except (KeyboardInterrupt, EOFError):
            print(color("\n  Goodbye!", 'green'))
            break
        except Exception as e:
            print(color(f"\n  Error: {e}", 'red'))


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(color("\n  Goodbye!", 'green'))