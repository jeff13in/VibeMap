"""
Day 3-4: Clustering Module
K-means clustering for mood-based song grouping
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT              # where cleaned_spotify_data.csv currently is
MODEL_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "notebooks" / "figures"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)



class MoodClusterer:
    """K-means clustering for mood-based song grouping"""
    
    def __init__(self, n_clusters=5, random_state=42):
        """
        Initialize clusterer
        
        Args:
            n_clusters: Number of mood clusters to create
            random_state: Random seed for reproducibility
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.kmeans = None
        self.feature_names = None
        self.cluster_labels = {
            0: 'Energetic & Happy',
            1: 'Calm & Peaceful',
            2: 'Melancholic',
            3: 'Party & Dance',
            4: 'Intense & Dark'
        }
    
    def select_features(self, df):
        """
        Select features for clustering
        
        Primary mood features:
        - valence: happiness/positivity
        - energy: intensity
        - danceability: dance suitability
        
        Secondary features:
        - tempo: speed
        - acousticness: acoustic vs electronic
        """
        # Primary mood features (weighted higher)
        primary_features = ['valence', 'energy', 'danceability']
        
        # Secondary features
        secondary_features = ['tempo', 'acousticness']
        
        # Normalize tempo to 0-1 range
        df_features = df.copy()
        df_features['tempo_normalized'] = (df_features['tempo'] - df_features['tempo'].min()) / \
                                          (df_features['tempo'].max() - df_features['tempo'].min())
        
        # Select features for clustering
        self.feature_names = primary_features + ['tempo_normalized', 'acousticness']

        # Drop rows with NaN in selected features
        df_features = df_features.dropna(subset=self.feature_names).reset_index(drop=True)
        X = df_features[self.feature_names].values
        
        print(f"✅ Selected {len(self.feature_names)} features for clustering:")
        for feat in self.feature_names:
            print(f"   - {feat}")
        
        return X, df_features
    
    def find_optimal_clusters(self, X, max_clusters=10):
        """
        Find optimal number of clusters using elbow method and silhouette score
        
        Args:
            X: Feature matrix
            max_clusters: Maximum number of clusters to test
        """
        print("\n" + "="*60)
        print("🔍 FINDING OPTIMAL NUMBER OF CLUSTERS")
        print("="*60)
        
        inertias = []
        silhouette_scores = []
        davies_bouldin_scores = []
        K_range = range(2, max_clusters + 1)
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            kmeans.fit(X)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X, kmeans.labels_))
            davies_bouldin_scores.append(davies_bouldin_score(X, kmeans.labels_))
            
            print(f"   k={k}: Inertia={kmeans.inertia_:.2f}, "
                  f"Silhouette={silhouette_scores[-1]:.3f}, "
                  f"Davies-Bouldin={davies_bouldin_scores[-1]:.3f}")
        
        # Visualize metrics
        fig, axes = plt.subplots(1, 3, figsize=(16, 4))
        
        # Elbow plot
        axes[0].plot(K_range, inertias, 'bo-', linewidth=2)
        axes[0].set_xlabel('Number of Clusters (k)', fontweight='bold')
        axes[0].set_ylabel('Inertia', fontweight='bold')
        axes[0].set_title('Elbow Method', fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # Silhouette score (higher is better)
        axes[1].plot(K_range, silhouette_scores, 'go-', linewidth=2)
        axes[1].set_xlabel('Number of Clusters (k)', fontweight='bold')
        axes[1].set_ylabel('Silhouette Score', fontweight='bold')
        axes[1].set_title('Silhouette Score (Higher is Better)', fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        
        # Davies-Bouldin score (lower is better)
        axes[2].plot(K_range, davies_bouldin_scores, 'ro-', linewidth=2)
        axes[2].set_xlabel('Number of Clusters (k)', fontweight='bold')
        axes[2].set_ylabel('Davies-Bouldin Score', fontweight='bold')
        axes[2].set_title('Davies-Bouldin Score (Lower is Better)', fontweight='bold')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = OUTPUT_DIR / 'cluster_optimization.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"\n   ✅ Saved cluster optimization plot to {output_path}")
        plt.close()
        
        # Find optimal k (max silhouette score)
        optimal_k = K_range[np.argmax(silhouette_scores)]
        print(f"\n   🎯 Optimal number of clusters: {optimal_k} "
              f"(Silhouette Score: {max(silhouette_scores):.3f})")
        
        return optimal_k
    
    def fit(self, df, auto_optimize=False):
        """
        Fit K-means clustering model
        
        Args:
            df: DataFrame with audio features
            auto_optimize: Whether to automatically find optimal k
        """
        print("\n" + "="*60)
        print("🎯 FITTING CLUSTERING MODEL")
        print("="*60)
        
        # Select and scale features
        X, df_features = self.select_features(df)
        X_scaled = self.scaler.fit_transform(X)
        
        # Find optimal clusters if requested
        if auto_optimize:
            self.n_clusters = self.find_optimal_clusters(X_scaled)
        
        # Fit K-means
        print(f"\n   Training K-means with {self.n_clusters} clusters...")
        self.kmeans = KMeans(n_clusters=self.n_clusters, 
                            random_state=self.random_state,
                            n_init=20,
                            max_iter=500)
        cluster_labels = self.kmeans.fit_predict(X_scaled)
        
        # Evaluate clustering
        silhouette_avg = silhouette_score(X_scaled, cluster_labels)
        davies_bouldin = davies_bouldin_score(X_scaled, cluster_labels)
        
        print(f"\n   ✅ Clustering complete!")
        print(f"   Silhouette Score: {silhouette_avg:.3f}")
        print(f"   Davies-Bouldin Score: {davies_bouldin:.3f}")
        print(f"   Inertia: {self.kmeans.inertia_:.2f}")
        
        # Add cluster labels to dataframe
        df_features['cluster'] = cluster_labels
        
        return df_features, X_scaled
    
    def analyze_clusters(self, df_clustered):
        """Analyze characteristics of each cluster"""
        print("\n" + "="*60)
        print("📊 CLUSTER ANALYSIS")
        print("="*60)
        
        # Cluster distribution
        print("\n--- Cluster Distribution ---")
        cluster_counts = df_clustered['cluster'].value_counts().sort_index()
        for cluster_id, count in cluster_counts.items():
            label = self.cluster_labels.get(cluster_id, f'Cluster {cluster_id}')
            print(f"   Cluster {cluster_id} ({label}): {count} songs "
                  f"({count/len(df_clustered)*100:.1f}%)")
        
        # Average features per cluster
        print("\n--- Average Features per Cluster ---")
        cluster_means = df_clustered.groupby('cluster')[
            ['valence', 'energy', 'danceability', 'tempo', 'acousticness']
        ].mean()
        print(cluster_means.round(3))
        
        # Assign meaningful labels based on characteristics
        print("\n--- Cluster Interpretations ---")
        for cluster_id in range(self.n_clusters):
            cluster_data = cluster_means.loc[cluster_id]
            
            # Interpret cluster based on features
            interpretation = self._interpret_cluster(cluster_data)
            self.cluster_labels[cluster_id] = interpretation
            
            print(f"\n   Cluster {cluster_id}: {interpretation}")
            print(f"      Valence: {cluster_data['valence']:.3f}")
            print(f"      Energy: {cluster_data['energy']:.3f}")
            print(f"      Danceability: {cluster_data['danceability']:.3f}")
            print(f"      Tempo: {cluster_data['tempo']:.1f} BPM")
            print(f"      Acousticness: {cluster_data['acousticness']:.3f}")
        
        return cluster_means
    
    def _interpret_cluster(self, features):
        """Interpret cluster based on feature values"""
        valence = features['valence']
        energy = features['energy']
        danceability = features['danceability']
        tempo = features['tempo']
        acousticness = features['acousticness']
        
        # High energy, high valence, high danceability
        if energy > 0.6 and valence > 0.6 and danceability > 0.6:
            return 'Energetic & Happy'
        
        # High energy, low valence
        elif energy > 0.6 and valence < 0.4:
            return 'Intense & Dark'
        
        # Low energy, high valence
        elif energy < 0.4 and valence > 0.6:
            return 'Calm & Peaceful'
        
        # Low energy, low valence
        elif energy < 0.4 and valence < 0.4:
            return 'Melancholic'
        
        # High danceability
        elif danceability > 0.7:
            return 'Party & Dance'
        
        # High acousticness
        elif acousticness > 0.6:
            return 'Acoustic & Mellow'
        
        # Default
        else:
            return 'Balanced & Versatile'
    
    def visualize_clusters(self, df_clustered, X_scaled):
        """Visualize clusters in 2D space"""
        print("\n" + "="*60)
        print("📈 VISUALIZING CLUSTERS")
        print("="*60)
        
        # Create visualization with multiple views
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # Define color palette
        colors = sns.color_palette('husl', self.n_clusters)
        
        # 1. Valence vs Energy
        for cluster_id in range(self.n_clusters):
            mask = df_clustered['cluster'] == cluster_id
            label = self.cluster_labels.get(cluster_id, f'Cluster {cluster_id}')
            axes[0, 0].scatter(df_clustered.loc[mask, 'valence'],
                              df_clustered.loc[mask, 'energy'],
                              c=[colors[cluster_id]], label=label, alpha=0.6, s=50)
        
        axes[0, 0].set_xlabel('Valence (Happiness)', fontweight='bold')
        axes[0, 0].set_ylabel('Energy (Intensity)', fontweight='bold')
        axes[0, 0].set_title('Clusters: Valence vs Energy', fontweight='bold')
        axes[0, 0].legend(loc='best', frameon=True, fontsize=8)
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Danceability vs Tempo
        for cluster_id in range(self.n_clusters):
            mask = df_clustered['cluster'] == cluster_id
            axes[0, 1].scatter(df_clustered.loc[mask, 'danceability'],
                              df_clustered.loc[mask, 'tempo'],
                              c=[colors[cluster_id]], alpha=0.6, s=50)
        
        axes[0, 1].set_xlabel('Danceability', fontweight='bold')
        axes[0, 1].set_ylabel('Tempo (BPM)', fontweight='bold')
        axes[0, 1].set_title('Clusters: Danceability vs Tempo', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Energy vs Acousticness
        for cluster_id in range(self.n_clusters):
            mask = df_clustered['cluster'] == cluster_id
            axes[1, 0].scatter(df_clustered.loc[mask, 'energy'],
                              df_clustered.loc[mask, 'acousticness'],
                              c=[colors[cluster_id]], alpha=0.6, s=50)
        
        axes[1, 0].set_xlabel('Energy', fontweight='bold')
        axes[1, 0].set_ylabel('Acousticness', fontweight='bold')
        axes[1, 0].set_title('Clusters: Energy vs Acousticness', fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Cluster size distribution
        cluster_counts = df_clustered['cluster'].value_counts().sort_index()
        cluster_names = [self.cluster_labels.get(i, f'Cluster {i}') 
                        for i in range(self.n_clusters)]
        
        axes[1, 1].bar(range(self.n_clusters), cluster_counts.values, color=colors)
        axes[1, 1].set_xlabel('Cluster', fontweight='bold')
        axes[1, 1].set_ylabel('Number of Songs', fontweight='bold')
        axes[1, 1].set_title('Cluster Distribution', fontweight='bold')
        axes[1, 1].set_xticks(range(self.n_clusters))
        axes[1, 1].set_xticklabels(cluster_names, rotation=45, ha='right', fontsize=8)
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        output_path = OUTPUT_DIR / 'cluster_visualization.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"   ✅ Saved cluster visualization to {output_path}")
        plt.close()
    
    def save_model(self, filename='mood_clusterer.pkl'):
        """Save trained model and scaler"""
        model_path = MODEL_DIR / filename
        
        model_data = {
            'kmeans': self.kmeans,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'n_clusters': self.n_clusters,
            'cluster_labels': self.cluster_labels
        }
        
        joblib.dump(model_data, model_path)
        print(f"\n✅ Model saved to {model_path}")
    
    @classmethod
    def load_model(cls, filename='mood_clusterer.pkl'):
        """Load trained model from the trusted MODEL_DIR directory."""
        safe_name = Path(filename).name
        model_path = (MODEL_DIR / safe_name).resolve()
        if not model_path.is_relative_to(MODEL_DIR.resolve()):
            raise ValueError("Invalid model filename")
        model_data = joblib.load(model_path)
        
        clusterer = cls(n_clusters=model_data['n_clusters'])
        clusterer.kmeans = model_data['kmeans']
        clusterer.scaler = model_data['scaler']
        clusterer.feature_names = model_data['feature_names']
        clusterer.cluster_labels = model_data['cluster_labels']
        
        print(f"✅ Model loaded from {model_path}")
        return clusterer


def main():
    """Main execution function"""
    print("\n🎵 SPOTIFY SONG CLUSTERING")
    
    # Load processed data
    data_path = DATA_DIR / 'cleaned_spotify_data.csv'
    df = pd.read_csv(data_path)
    print(f"✅ Loaded dataset: {df.shape}")
    
    # Initialize and train clusterer
    clusterer = MoodClusterer(n_clusters=5, random_state=42)
    
    # Fit model (with auto-optimization)
    df_clustered, X_scaled = clusterer.fit(df, auto_optimize=True)
    
    # Analyze clusters
    cluster_means = clusterer.analyze_clusters(df_clustered)
    
    # Visualize clusters
    clusterer.visualize_clusters(df_clustered, X_scaled)
    
    # Save model
    clusterer.save_model()
    
    # Save clustered data
    output_path = DATA_DIR / 'clustered_spotify_data.csv'
    df_clustered.to_csv(output_path, index=False)
    print(f"\n✅ Clustered data saved to {output_path}")
    
    print("\n✨ Clustering complete!")
    
    return clusterer, df_clustered


if __name__ == "__main__":
    main()