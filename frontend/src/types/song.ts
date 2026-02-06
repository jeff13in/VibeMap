export interface Song {
  track_id: string;
  track_name: string;
  artist: string;
  album?: string;
  valence: number;
  energy: number;
  danceability: number;
  tempo: number;
  acousticness: number;
  instrumentalness: number;
  liveness: number;
  speechiness: number;
  loudness: number;
  popularity: number;
  spotify_url?: string;
  similarity_score?: number;
  mood_score?: number;
  cluster?: number;
  year?: number;
}

export interface RecommendationResponse {
  success: boolean;
  count: number;
  filters: {
    mood?: string;
    tempo?: string;
    method?: string;
    count?: number;
  };
  recommendations: Song[];
}

export interface SearchResponse {
  success: boolean;
  query: string;
  count: number;
  results: Song[];
}

export type MoodType =
  | 'happy'
  | 'sad'
  | 'energetic'
  | 'calm'
  | 'party'
  | 'dark'
  | 'romantic'
  | 'angry';

export type TempoType = 'slow' | 'medium' | 'fast';

export type AlgorithmType = 'knn' | 'cosine' | 'euclidean';

export interface FilterState {
  mood: MoodType | null;
  tempo: TempoType | null;
  count: number;
  algorithm: AlgorithmType;
}
