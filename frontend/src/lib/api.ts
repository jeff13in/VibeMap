import axios from 'axios';
import type { Song, RecommendationResponse, SearchResponse, MoodType, TempoType, AlgorithmType } from '@/types/song';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  getMoodRecommendations: async (mood: MoodType, count: number = 10): Promise<Song[]> => {
    const response = await apiClient.get<RecommendationResponse>(
      `/api/recommendations/mood`,
      { params: { mood, count } }
    );
    return response.data.recommendations;
  },

  getTempoRecommendations: async (tempo: TempoType, count: number = 10): Promise<Song[]> => {
    const response = await apiClient.get<RecommendationResponse>(
      `/api/recommendations/tempo`,
      { params: { tempo, count } }
    );
    return response.data.recommendations;
  },

  getCombinedRecommendations: async (
    mood: MoodType,
    tempo: TempoType,
    count: number = 10
  ): Promise<Song[]> => {
    const response = await apiClient.get<RecommendationResponse>(
      `/api/recommendations/combined`,
      { params: { mood, tempo, count } }
    );
    return response.data.recommendations;
  },

  getSimilarSongs: async (
    songId: string,
    method: AlgorithmType = 'knn',
    count: number = 10
  ): Promise<Song[]> => {
    const response = await apiClient.get<RecommendationResponse>(
      `/api/recommendations/similar`,
      { params: { song_id: songId, method, count } }
    );
    return response.data.recommendations;
  },

  searchSongs: async (query: string, limit: number = 20): Promise<Song[]> => {
    const response = await apiClient.get<SearchResponse>(
      `/api/songs/search`,
      { params: { query, limit } }
    );
    return response.data.results;
  },

  getSongDetails: async (trackId: string): Promise<Song> => {
    const response = await apiClient.get<{ success: boolean; song: Song }>(
      `/api/songs/${trackId}`
    );
    return response.data.song;
  },

  getAvailableMoods: async (): Promise<string[]> => {
    const response = await apiClient.get<{ moods: string[] }>('/api/moods');
    return response.data.moods;
  },

  getAvailableTempos: async (): Promise<string[]> => {
    const response = await apiClient.get<{ tempos: string[] }>('/api/tempos');
    return response.data.tempos;
  },

  healthCheck: async (): Promise<boolean> => {
    try {
      const response = await apiClient.get('/health');
      return response.data.status === 'healthy';
    } catch {
      return false;
    }
  },
};

export default apiClient;
