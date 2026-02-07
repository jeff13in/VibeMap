import { Link, useLocation } from 'react-router-dom';
import vibemapLogo from '@/assets/vibemaap.png';
import { Button } from '@/components/ui/button';

const Header = () => {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-dark-highlight bg-dark-elevated/95 backdrop-blur supports-[backdrop-filter]:bg-dark-elevated/60">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center space-x-2">
          <div
            className="h-14 w-14 bg-contain bg-center bg-no-repeat"
            style={{ backgroundImage: `url(${vibemapLogo})` }}
            role="img"
            aria-label="VibeMap"
          />
          <span className="text-xl font-bold">VibeMap</span>
        </Link>

        <nav className="flex items-center space-x-6">
          <Link
            to="/"
            className={`text-sm font-medium transition-colors hover:text-spotify-green ${
              location.pathname === '/' ? 'text-spotify-green' : 'text-text-secondary'
            }`}
          >
            Home
          </Link>
          <Link
            to="/recommendations"
            className={`text-sm font-medium transition-colors hover:text-spotify-green ${
              location.pathname === '/recommendations'
                ? 'text-spotify-green'
                : 'text-text-secondary'
            }`}
          >
            Recommendations
          </Link>
          <Button
            variant="default"
            className="bg-spotify-green hover:bg-spotify-green-dark"
            asChild
          >
            <Link to="/recommendations">Get Started</Link>
          </Button>
        </nav>
      </div>
    </header>
  );
};

export default Header;
