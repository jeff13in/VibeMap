import { create } from 'zustand';
import type { Song, FilterState } from '@/types/song';

interface RecommendationStore {
  recommendations: Song[];
  loading: boolean;
  error: string | null;
  filters: FilterState;
  selectedSong: Song | null;

  setRecommendations: (songs: Song[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setFilters: (filters: Partial<FilterState>) => void;
  setSelectedSong: (song: Song | null) => void;
  clearRecommendations: () => void;
  clearFilters: () => void;
}

const initialFilters: FilterState = {
  mood: null,
  tempo: null,
  count: 10,
  algorithm: 'knn',
};

export const useRecommendationStore = create<RecommendationStore>((set) => ({
  recommendations: [],
  loading: false,
  error: null,
  filters: initialFilters,
  selectedSong: null,

  setRecommendations: (songs) => set({ recommendations: songs, error: null }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),
  setSelectedSong: (song) => set({ selectedSong: song }),
  clearRecommendations: () => set({ recommendations: [], error: null }),
  clearFilters: () => set({ filters: initialFilters }),
}));
