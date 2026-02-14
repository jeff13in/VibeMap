import { useState, useEffect, useRef, useMemo } from 'react';
import gsap from 'gsap';
import { Filter, Loader2, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import MoodSelector from '@/components/MoodSelector';
import SongCard from '@/components/SongCard';
import AnalyticsDashboard from '@/components/AnalyticsDashboard';
import { useRecommendations } from '@/hooks/useRecommendations';
import type { MoodType, TempoType } from '@/types/song';

const Recommendations = () => {
  const [selectedMood, setSelectedMood] = useState<MoodType | null>(null);
  const [selectedTempo, setSelectedTempo] = useState<TempoType>('medium');
  const [count, setCount] = useState<number[]>([10]);
  const gridRef = useRef<HTMLDivElement | null>(null);

  const {
    recommendations,
    loading,
    error,
    fetchByMood,
    fetchByTempo,
    fetchCombined,
  } = useRecommendations();

  // Animate new results
  useEffect(() => {
    if (recommendations.length > 0 && gridRef.current) {
      gsap.from('.recommendation-card', {
        scale: 0.8,
        opacity: 0,
        stagger: 0.05,
        duration: 0.5,
        ease: 'back.out',
      });
    }
  }, [recommendations]);

  const handleMoodRecommendations = () => {
    if (selectedMood) fetchByMood(selectedMood, count[0]);
  };

  const handleTempoRecommendations = () => {
    fetchByTempo(selectedTempo, count[0]);
  };

  const handleCombinedRecommendations = () => {
    if (selectedMood) fetchCombined(selectedMood, selectedTempo, count[0]);
  };

  /**
   * Map your API/DB song objects -> what the dashboard expects.
   * Dashboard expects: track_name, artist_name, tempo, valence, energy (at minimum)
   *
   * If your song fields differ, adjust the mapping here (ONLY here).
   */
  const dashboardSongs = useMemo(() => {
    return (recommendations || []).map((s: any) => ({
      // keep original id if present
      track_id: s.track_id ?? s.id ?? `${s.track_name ?? 'track'}-${s.artist_name ?? 'artist'}`,

      // normalize names (some datasets use artist vs artist_name)
      track_name: s.track_name ?? s.name ?? s.title ?? '',
      artist_name: s.artist_name ?? s.artist ?? s.artists ?? '',

      // normalize numeric fields
      tempo: Number(s.tempo ?? s.bpm),
      valence: Number(s.valence),
      energy: Number(s.energy),

      // optional extras (if you want to show more later)
      danceability: s.danceability != null ? Number(s.danceability) : undefined,
      popularity: s.popularity != null ? Number(s.popularity) : undefined,
      score: s.score != null ? Number(s.score) : undefined,
    }));
  }, [recommendations]);

  return (
    <div className="container overflow-x-hidden py-6 sm:py-8">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold sm:text-4xl">Discover Music</h1>
        <p className="text-text-secondary">
          Find your next favorite song with AI-powered recommendations
        </p>
      </div>

      <Tabs defaultValue="mood" className="space-y-8">
        <TabsList className="bg-dark-elevated border border-dark-highlight">
          <TabsTrigger value="mood">By Mood</TabsTrigger>
          <TabsTrigger value="tempo">By Tempo</TabsTrigger>
          <TabsTrigger value="combined">Mood + Tempo</TabsTrigger>
        </TabsList>

        {/* Mood Tab */}
        <TabsContent value="mood" className="space-y-6">
          <Card className="bg-dark-elevated border-dark-highlight overflow-hidden">
            <CardContent className="pt-6 min-w-0 overflow-x-hidden">
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Select a Mood</h3>
                  <MoodSelector value={selectedMood} onChange={setSelectedMood} />
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">
                    Number of Recommendations: {count[0]}
                  </h3>
                  <Slider
                    value={count}
                    onValueChange={setCount}
                    min={5}
                    max={50}
                    step={5}
                    className="w-full"
                  />
                </div>

                <Button
                  onClick={handleMoodRecommendations}
                  disabled={!selectedMood || loading}
                  className="w-full bg-spotify-green hover:bg-spotify-green-dark"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    'Get Recommendations'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tempo Tab */}
        <TabsContent value="tempo" className="space-y-6">
          <Card className="bg-dark-elevated border-dark-highlight">
            <CardContent className="pt-6">
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Select Tempo</h3>
                  <div className="grid grid-cols-3 gap-4">
                    {(['slow', 'medium', 'fast'] as TempoType[]).map((tempo) => (
                      <Button
                        key={tempo}
                        variant={selectedTempo === tempo ? 'default' : 'outline'}
                        className={
                          selectedTempo === tempo
                            ? 'bg-spotify-green hover:bg-spotify-green-dark'
                            : 'border-dark-highlight hover:border-spotify-green'
                        }
                        onClick={() => setSelectedTempo(tempo)}
                      >
                        {tempo.charAt(0).toUpperCase() + tempo.slice(1)}
                      </Button>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">
                    Number of Recommendations: {count[0]}
                  </h3>
                  <Slider
                    value={count}
                    onValueChange={setCount}
                    min={5}
                    max={50}
                    step={5}
                    className="w-full"
                  />
                </div>

                <Button
                  onClick={handleTempoRecommendations}
                  disabled={loading}
                  className="w-full bg-spotify-green hover:bg-spotify-green-dark"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    'Get Recommendations'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Combined Tab */}
        <TabsContent value="combined" className="space-y-6">
          <Card className="bg-dark-elevated border-dark-highlight">
            <CardContent className="pt-6">
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Select a Mood</h3>
                  <MoodSelector value={selectedMood} onChange={setSelectedMood} />
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Select Tempo</h3>
                  <div className="grid grid-cols-3 gap-4">
                    {(['slow', 'medium', 'fast'] as TempoType[]).map((tempo) => (
                      <Button
                        key={tempo}
                        variant={selectedTempo === tempo ? 'default' : 'outline'}
                        className={
                          selectedTempo === tempo
                            ? 'bg-spotify-green hover:bg-spotify-green-dark'
                            : 'border-dark-highlight hover:border-spotify-green'
                        }
                        onClick={() => setSelectedTempo(tempo)}
                      >
                        {tempo.charAt(0).toUpperCase() + tempo.slice(1)}
                      </Button>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">
                    Number of Recommendations: {count[0]}
                  </h3>
                  <Slider
                    value={count}
                    onValueChange={setCount}
                    min={5}
                    max={50}
                    step={5}
                    className="w-full"
                  />
                </div>

                <Button
                  onClick={handleCombinedRecommendations}
                  disabled={!selectedMood || loading}
                  className="w-full bg-spotify-green hover:bg-spotify-green-dark"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    'Get Recommendations'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Errors */}
      {error && (
        <div className="mt-8 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p className="text-red-500">{error}</p>
        </div>
      )}

      {/* Results */}
      {recommendations.length > 0 && (
        <div className="mt-8 space-y-8">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">
              {recommendations.length} Recommendations
            </h2>
          </div>

          {/* Song Cards */}
          <div
            ref={gridRef}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
          >
            {recommendations.map((song: any, idx: number) => (
              <div
                key={song.track_id ?? song.id ?? `${song.track_name}-${song.artist_name}-${idx}`}
                className="recommendation-card"
              >
                <SongCard song={song} showScore />
              </div>
            ))}
          </div>

          {/* Dynamic Analytics Dashboard (based on current recommendations) */}
          <Card className="bg-dark-elevated border-dark-highlight">
            <CardContent className="pt-6">
              <div className="mb-4 flex flex-wrap items-center gap-2">
                <BarChart3 className="h-5 w-5 text-spotify-green" />
                <h3 className="text-lg sm:text-xl font-semibold">Live Analytics</h3>
                <span className="hidden text-text-secondary text-sm sm:inline">
                  (updates every time you generate recommendations)
                </span>
              </div>

              <AnalyticsDashboard songs={dashboardSongs} />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Empty State */}
      {!loading && recommendations.length === 0 && !error && (
        <div className="mt-8 text-center py-12">
          <Filter className="h-16 w-16 text-text-tertiary mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Recommendations Yet</h3>
          <p className="text-text-secondary">
            Select your preferences above to get started
          </p>
        </div>
      )}
    </div>
  );
};

export default Recommendations;
