import { useCallback } from 'react';
import { api } from '@/lib/api';
import { useRecommendationStore } from '@/store/recommendationStore';
import type { MoodType, TempoType, AlgorithmType } from '@/types/song';

export const useRecommendations = () => {
  const {
    recommendations,
    loading,
    error,
    filters,
    setRecommendations,
    setLoading,
    setError,
    setFilters,
    clearRecommendations,
  } = useRecommendationStore();

  const fetchByMood = useCallback(async (mood: MoodType, count?: number) => {
    setLoading(true);
    setError(null);
    try {
      const songs = await api.getMoodRecommendations(mood, count || filters.count);
      setRecommendations(songs);
      setFilters({ mood, tempo: null });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fetch recommendations';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [filters.count, setLoading, setError, setRecommendations, setFilters]);

  const fetchByTempo = useCallback(async (tempo: TempoType, count?: number) => {
    setLoading(true);
    setError(null);
    try {
      const songs = await api.getTempoRecommendations(tempo, count || filters.count);
      setRecommendations(songs);
      setFilters({ tempo, mood: null });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fetch recommendations';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [filters.count, setLoading, setError, setRecommendations, setFilters]);

  const fetchCombined = useCallback(async (
    mood: MoodType,
    tempo: TempoType,
    count?: number
  ) => {
    setLoading(true);
    setError(null);
    try {
      const songs = await api.getCombinedRecommendations(mood, tempo, count || filters.count);
      setRecommendations(songs);
      setFilters({ mood, tempo });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fetch recommendations';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [filters.count, setLoading, setError, setRecommendations, setFilters]);

  const fetchSimilar = useCallback(async (
    songId: string,
    method?: AlgorithmType,
    count?: number
  ) => {
    setLoading(true);
    setError(null);
    try {
      const songs = await api.getSimilarSongs(
        songId,
        method || filters.algorithm,
        count || filters.count
      );
      setRecommendations(songs);
      setFilters({ mood: null, tempo: null, algorithm: method || filters.algorithm });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fetch similar songs';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [filters.count, filters.algorithm, setLoading, setError, setRecommendations, setFilters]);

  return {
    recommendations,
    loading,
    error,
    filters,
    fetchByMood,
    fetchByTempo,
    fetchCombined,
    fetchSimilar,
    clearRecommendations,
    setFilters,
  };
};
