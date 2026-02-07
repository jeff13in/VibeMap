import { Github, Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="border-t border-dark-highlight bg-dark-elevated mt-auto">
      <div className="container flex h-16 items-center justify-between py-4">
        <p className="text-sm text-text-secondary">
          Built with <Heart className="inline h-4 w-4 text-red-500" /> using React, TypeScript,
          shadcn/ui, and GSAP
        </p>
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-text-secondary hover:text-spotify-green transition-colors"
        >
          <Github className="h-5 w-5" />
        </a>
      </div>
    </footer>
  );
};

export default Footer;
