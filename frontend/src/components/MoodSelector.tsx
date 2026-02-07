import { Smile, Frown, Zap, Wind, PartyPopper, Moon, Heart, Flame } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { MoodType } from '@/types/song';

interface MoodSelectorProps {
  value: MoodType | null;
  onChange: (mood: MoodType) => void;
}

const moods: { value: MoodType; label: string; icon: React.ComponentType<{ className?: string }>; color: string }[] = [
  { value: 'happy', label: 'Happy', icon: Smile, color: 'mood-happy' },
  { value: 'sad', label: 'Sad', icon: Frown, color: 'mood-sad' },
  { value: 'energetic', label: 'Energetic', icon: Zap, color: 'mood-energetic' },
  { value: 'calm', label: 'Calm', icon: Wind, color: 'mood-calm' },
  { value: 'party', label: 'Party', icon: PartyPopper, color: 'mood-party' },
  { value: 'dark', label: 'Dark', icon: Moon, color: 'mood-dark' },
  { value: 'romantic', label: 'Romantic', icon: Heart, color: 'mood-romantic' },
  { value: 'angry', label: 'Angry', icon: Flame, color: 'mood-angry' },
];

const MoodSelector = ({ value, onChange }: MoodSelectorProps) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {moods.map((mood) => {
        const Icon = mood.icon;
        const isSelected = value === mood.value;

        return (
          <Button
            key={mood.value}
            variant={isSelected ? 'default' : 'outline'}
            className={`h-20 flex flex-col items-center justify-center gap-2 transition-all ${
              isSelected
                ? 'bg-spotify-green hover:bg-spotify-green-dark border-spotify-green'
                : 'border-dark-highlight hover:border-spotify-green bg-dark-elevated'
            }`}
            onClick={() => onChange(mood.value)}
          >
            <Icon className={`h-6 w-6 ${isSelected ? 'text-white' : `text-${mood.color}`}`} />
            <span className={`text-sm ${isSelected ? 'text-white' : 'text-text-secondary'}`}>
              {mood.label}
            </span>
          </Button>
        );
      })}
    </div>
  );
};

export default MoodSelector;
