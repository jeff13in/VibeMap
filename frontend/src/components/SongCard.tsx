import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { Music2, TrendingUp, ExternalLink, Check, Copy } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Song } from '@/types/song';

interface SongCardProps {
  song: Song;
  onClick?: () => void;
  showScore?: boolean;
}

const SongCard = ({ song, onClick, showScore = true }: SongCardProps) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const card = cardRef.current;
    if (!card) return;

    const handleMouseEnter = () => {
      gsap.to(card, {
        y: -8,
        scale: 1.02,
        duration: 0.3,
        ease: 'power2.out',
      });
    };

    const handleMouseLeave = () => {
      gsap.to(card, {
        y: 0,
        scale: 1,
        duration: 0.3,
        ease: 'power2.out',
      });
    };

    card.addEventListener('mouseenter', handleMouseEnter);
    card.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      card.removeEventListener('mouseenter', handleMouseEnter);
      card.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  const getMoodColor = (valence: number) => {
    if (valence > 0.7) return 'bg-mood-happy';
    if (valence > 0.5) return 'bg-spotify-green';
    if (valence > 0.3) return 'bg-mood-calm';
    return 'bg-mood-sad';
  };

  const handleShare = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!song.spotify_url) return;

    navigator.clipboard.writeText(song.spotify_url).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <Card
      ref={cardRef}
      className="bg-dark-elevated border-dark-highlight cursor-pointer hover:border-spotify-green transition-colors"
      onClick={onClick}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg text-text-primary line-clamp-1">
              {song.track_name}
            </CardTitle>
            <p className="text-sm text-text-secondary mt-1">{song.artist}</p>
          </div>
          <div className="flex items-center gap-1.5 flex-shrink-0 ml-2">
            {song.spotify_url && (
              <>
                <a
                  href={song.spotify_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="p-1.5 rounded-full hover:bg-spotify-green/20 transition-colors"
                  title="Open in Spotify"
                >
                  <ExternalLink className="h-4 w-4 text-spotify-green" />
                </a>
                <button
                  onClick={handleShare}
                  className="p-1.5 rounded-full hover:bg-spotify-green/20 transition-colors"
                  title="Copy Spotify link"
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-spotify-green" />
                  ) : (
                    <Copy className="h-4 w-4 text-text-tertiary hover:text-spotify-green" />
                  )}
                </button>
              </>
            )}
            {!song.spotify_url && (
              <Music2 className="h-5 w-5 text-spotify-green" />
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-text-tertiary">Valence:</span>
              <div className="flex items-center gap-2 mt-1">
                <div className="flex-1 h-1.5 bg-dark-highlight rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getMoodColor(song.valence)}`}
                    style={{ width: `${song.valence * 100}%` }}
                  />
                </div>
                <span className="text-text-secondary w-8 text-right">
                  {(song.valence * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            <div>
              <span className="text-text-tertiary">Energy:</span>
              <div className="flex items-center gap-2 mt-1">
                <div className="flex-1 h-1.5 bg-dark-highlight rounded-full overflow-hidden">
                  <div
                    className="h-full bg-mood-energetic"
                    style={{ width: `${song.energy * 100}%` }}
                  />
                </div>
                <span className="text-text-secondary w-8 text-right">
                  {(song.energy * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-dark-highlight">
            <div className="flex items-center gap-1 text-xs text-text-tertiary">
              <TrendingUp className="h-3 w-3" />
              <span>{song.tempo.toFixed(0)} BPM</span>
            </div>

            {showScore && (song.similarity_score || song.mood_score) && (
              <Badge variant="secondary" className="bg-spotify-green/20 text-spotify-green">
                {((song.similarity_score || song.mood_score || 0) * 100).toFixed(0)}% Match
              </Badge>
            )}

            {!showScore && (
              <Badge variant="secondary" className="bg-dark-highlight text-text-secondary">
                Popularity: {song.popularity}
              </Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SongCard;
