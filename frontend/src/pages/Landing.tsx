import { useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import vibemapLogo from '@/assets/vibemaap.png';

gsap.registerPlugin(ScrollTrigger);

// Landing Header Component
const LandingHeader = () => {
  const headerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (!headerRef.current) return;
      if (window.scrollY > 50) {
        headerRef.current.classList.add('bg-dark-base/80', 'backdrop-blur-md', 'border-b', 'border-dark-highlight/50');
        headerRef.current.classList.remove('bg-transparent');
      } else {
        headerRef.current.classList.remove('bg-dark-base/80', 'backdrop-blur-md', 'border-b', 'border-dark-highlight/50');
        headerRef.current.classList.add('bg-transparent');
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      ref={headerRef}
      className="fixed top-0 left-0 right-0 z-50 bg-transparent transition-all duration-300"
    >
      <div className="container flex h-24 items-center justify-between px-6 max-w-7xl mx-auto">
        <Link to="/" className="flex items-center -space-x-2">
          <div
            className="h-36 w-36 bg-contain bg-center bg-no-repeat"
            style={{ backgroundImage: `url(${vibemapLogo})` }}
            role="img"
            aria-label="VibeMap"
          />
          <span className="text-xl font-bold text-white">VibeMap</span>
        </Link>

        <nav className="hidden md:flex items-center space-x-8">
          <a
            href="#benefits"
            className="text-sm font-medium text-white/70 hover:text-spotify-green transition-colors"
          >
            Benefits
          </a>
          <a
            href="#moods"
            className="text-sm font-medium text-white/70 hover:text-spotify-green transition-colors"
          >
            Moods
          </a>
          <a
            href="#how-it-works"
            className="text-sm font-medium text-white/70 hover:text-spotify-green transition-colors"
          >
            How It Works
          </a>
        </nav>

        <Link
          to="/recommendations"
          className="inline-flex items-center justify-center px-5 py-2.5 rounded-full bg-spotify-green text-white text-sm font-semibold hover:bg-spotify-green-dark transition-colors"
        >
          Get Started
        </Link>
      </div>
    </header>
  );
};

// Landing Footer Component
const LandingFooter = () => {
  return (
    <footer className="bg-dark-base border-t border-dark-highlight py-12">
      <div className="container px-6 max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center -space-x-1">
            <div
              className="h-16 w-16 bg-contain bg-center bg-no-repeat"
              style={{ backgroundImage: `url(${vibemapLogo})` }}
              role="img"
              aria-label="VibeMap"
            />
            <span className="font-bold text-white">VibeMap</span>
          </div>
          <div className="flex items-center gap-8">
            <a href="#benefits" className="text-sm text-text-secondary hover:text-spotify-green transition-colors">
              Benefits
            </a>
            <a href="#moods" className="text-sm text-text-secondary hover:text-spotify-green transition-colors">
              Moods
            </a>
            <a href="#how-it-works" className="text-sm text-text-secondary hover:text-spotify-green transition-colors">
              How It Works
            </a>
            <Link to="/recommendations" className="text-sm text-text-secondary hover:text-spotify-green transition-colors">
              Get Started
            </Link>
          </div>
          <p className="text-xs text-text-secondary">
            Powered by Machine Learning
          </p>
        </div>
      </div>
    </footer>
  );
};

// SVG Icon Components
const MusicNoteIcon = () => (
  <svg className="size-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
  </svg>
);

const HeartIcon = () => (
  <svg className="size-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
  </svg>
);

const BoltIcon = () => (
  <svg className="size-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
  </svg>
);

const SparklesIcon = () => (
  <svg className="size-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
  </svg>
);

const ArrowIcon = () => (
  <svg className="size-3" fill="currentColor" viewBox="0 0 12 12">
    <path d="M2 2h7v1H4.41l5.3 5.29-.71.71L3.71 3.71 4 8H3V2z" />
  </svg>
);

const CheckIcon = () => (
  <svg className="size-3" fill="currentColor" viewBox="0 0 12 12">
    <path d="M10.28 2.28L4.5 8.06 1.72 5.28.28 6.72l4.22 4.22 7.22-7.22-1.44-1.44z" />
  </svg>
);

const CloseIcon = () => (
  <svg className="size-3" fill="currentColor" viewBox="0 0 12 12">
    <path d="M6 4.59L10.59 0 12 1.41 7.41 6 12 10.59 10.59 12 6 7.41 1.41 12 0 10.59 4.59 6 0 1.41 1.41 0 6 4.59z" />
  </svg>
);

// Button Component
type ButtonProps = {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
  onClick?: () => void;
  className?: string;
};

const Button = ({ children, variant = 'primary', onClick, className = '' }: ButtonProps) => {
  const baseStyles = 'inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full font-semibold text-sm transition-all duration-300 cursor-pointer';
  const variants = {
    primary: 'bg-spotify-green text-white hover:bg-spotify-green-dark',
    secondary: 'bg-dark-elevated text-white hover:bg-dark-highlight border border-dark-highlight',
    outline: 'bg-transparent text-spotify-green border-2 border-spotify-green hover:bg-spotify-green hover:text-white',
  };

  return (
    <button className={`${baseStyles} ${variants[variant]} ${className}`} onClick={onClick}>
      {children}
    </button>
  );
};

// Hero Section
const HeroSection = ({ onGetStarted }: { onGetStarted: () => void }) => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-dark-base via-dark-elevated to-dark-base pt-16">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-spotify-green/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-mood-party/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-spotify-green/5 rounded-full blur-3xl" />
      </div>

      <div className="container relative z-10 px-6 py-24 text-center">
        <div className="flex flex-col items-center gap-8 max-w-4xl mx-auto">
          <p className="hero-label font-mono text-sm text-spotify-green tracking-widest uppercase">
            ML-Driven Personalized Recommendations
          </p>

          <h1 className="hero-title font-serif text-6xl md:text-8xl leading-none tracking-tight text-white">
            Feel The <span className="text-spotify-green">Vibe</span>
          </h1>

          <p className="hero-subtitle text-lg md:text-xl text-text-secondary max-w-2xl leading-relaxed">
            Discover music that matches your mood. VibeMap uses Machine Learning to recommend songs based on how you feel,
            whether you're seeking energy, calm, or anything in between.
          </p>

          <div className="hero-buttons flex flex-col sm:flex-row gap-4 mt-4">
            <Button variant="primary" onClick={onGetStarted}>
              Start Discovering
              <ArrowIcon />
            </Button>
            <Button variant="outline" onClick={onGetStarted}>
              Learn More
            </Button>
          </div>

          {/* Mood Pills */}
          <div className="hero-moods flex flex-wrap justify-center gap-3 mt-8">
            {['Happy', 'Energetic', 'Calm', 'Romantic', 'Party'].map((mood, i) => (
              <span
                key={mood}
                className="px-4 py-2 rounded-full text-xs font-medium bg-dark-highlight/50 text-text-secondary border border-dark-highlight hover:border-spotify-green hover:text-spotify-green transition-colors cursor-pointer"
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                {mood}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 rounded-full border-2 border-text-secondary/30 flex items-start justify-center p-2">
          <div className="w-1 h-2 bg-text-secondary/50 rounded-full" />
        </div>
      </div>
    </section>
  );
};

// Benefits Section
const BenefitsSection = () => {
  const benefits = [
    {
      icon: <HeartIcon />,
      title: 'Mood-Based Discovery',
      description: 'Choose from 8 distinct moods including happy, sad, energetic, calm, dark, romantic, angry, and party to find your perfect soundtrack.',
    },
    {
      icon: <BoltIcon />,
      title: 'Tempo Control',
      description: 'Filter by tempo - slow for relaxation, medium for focus, or fast for high-energy moments. Match the pace to your activity.',
    },
    {
      icon: <SparklesIcon />,
      title: 'ML-Powered Similarity',
      description: 'Find songs similar to your favorites using advanced machine learning algorithms including KNN and cosine similarity.',
    },
    {
      icon: <MusicNoteIcon />,
      title: 'Audio Feature Analysis',
      description: 'Deep analysis of valence, energy, danceability, and more to understand what makes each song unique.',
    },
  ];

  return (
    <section className="py-24 bg-dark-base">
      <div className="container px-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col gap-8 pb-16 border-t border-dark-highlight pt-20">
          <p className="font-mono text-xs text-spotify-green tracking-widest uppercase">Benefits</p>
          <h2 className="font-serif text-5xl md:text-6xl text-white leading-tight max-w-2xl">
            Music discovery, reimagined.
          </h2>
          <p className="text-text-secondary text-lg max-w-xl">
            VibeMap analyzes audio features to deliver personalized recommendations that actually match your mood.
          </p>
        </div>

        {/* Benefits Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-0 pt-10">
          {benefits.map((benefit) => (
            <div
              key={benefit.title}
              className="benefit-card border-t border-dark-highlight py-12 pr-8"
            >
              <div className="flex flex-col gap-6">
                <div className="size-12 rounded-lg bg-spotify-green/10 flex items-center justify-center text-spotify-green">
                  {benefit.icon}
                </div>
                <div className="flex flex-col gap-4">
                  <h3 className="font-serif text-xl text-white">{benefit.title}</h3>
                  <p className="text-text-secondary text-sm leading-relaxed">{benefit.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Mood Showcase Section
const MoodShowcase = () => {
  const moods = [
    { name: 'Happy', color: 'bg-mood-happy', emoji: '😊' },
    { name: 'Sad', color: 'bg-mood-sad', emoji: '😢' },
    { name: 'Energetic', color: 'bg-mood-energetic', emoji: '⚡' },
    { name: 'Calm', color: 'bg-mood-calm', emoji: '🧘' },
    { name: 'Dark', color: 'bg-mood-dark', emoji: '🌙' },
    { name: 'Romantic', color: 'bg-mood-romantic', emoji: '💕' },
    { name: 'Angry', color: 'bg-mood-angry', emoji: '😤' },
    { name: 'Party', color: 'bg-mood-party', emoji: '🎉' },
  ];

  return (
    <section className="py-24 bg-dark-elevated">
      <div className="container px-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <p className="font-mono text-xs text-spotify-green tracking-widest uppercase mb-6">Moods</p>
          <h2 className="font-serif text-5xl md:text-6xl text-white mb-6">8 Moods to Explore</h2>
          <p className="text-text-secondary text-lg max-w-2xl mx-auto">
            Each mood is carefully calibrated using audio features like valence, energy, and danceability
            to find songs that truly match how you feel.
          </p>
        </div>

        {/* Mood Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {moods.map((mood) => (
            <div
              key={mood.name}
              className="mood-card group relative overflow-hidden rounded-2xl bg-dark-highlight p-6 cursor-pointer hover:scale-105 transition-transform duration-300"
            >
              <div className={`absolute inset-0 ${mood.color} opacity-10 group-hover:opacity-20 transition-opacity`} />
              <div className="relative flex flex-col items-center gap-4">
                <span className="text-4xl">{mood.emoji}</span>
                <span className="font-medium text-white">{mood.name}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Features Section
const FeaturesSection = ({ onGetStarted }: { onGetStarted: () => void }) => {
  const features = [
    {
      number: '01',
      title: 'Select Your Mood',
      description: "Choose how you're feeling from 8 distinct moods. Our algorithm filters songs based on valence and energy levels.",
    },
    {
      number: '02',
      title: 'Set Your Tempo',
      description: 'Pick slow (under 100 BPM), medium (100-120 BPM), or fast (120+ BPM) to match your activity level.',
    },
    {
      number: '03',
      title: 'Discover Similar Songs',
      description: 'Found a song you love? Use our similarity search to find tracks with matching audio characteristics.',
    },
    {
      number: '04',
      title: 'Build Your Playlist',
      description: 'Combine mood, tempo, and similarity features to create the perfect playlist for any moment.',
    },
  ];

  return (
    <section className="py-24 bg-dark-base">
      <div className="container px-6 max-w-7xl mx-auto">
        <div className="border-t border-dark-highlight pt-16">
          {/* Header */}
          <div className="flex flex-col gap-10 mb-20">
            <h2 className="font-serif text-5xl md:text-6xl text-white max-w-2xl">
              How VibeMap Works
            </h2>
            <p className="text-text-secondary text-lg max-w-xl">
              VibeMap turns complex audio data into simple, actionable music recommendations. Here's how it works.
            </p>
          </div>

          {/* Feature List */}
          <div className="space-y-0">
            {features.map((feature) => (
              <div
                key={feature.number}
                className="feature-item flex gap-8 items-start py-6 border-t border-dark-highlight"
              >
                <span className="font-mono text-6xl text-dark-highlight/50">{feature.number}</span>
                <div className="flex flex-col gap-4 pt-4">
                  <h3 className="font-serif text-xl text-white">{feature.title}</h3>
                  <p className="text-text-secondary text-sm leading-relaxed max-w-md">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-12">
            <Button variant="secondary" onClick={onGetStarted}>
              Discover More
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

// Comparison Table Section
const ComparisonSection = () => {
  const features = [
    { name: 'Mood-based filtering', vibemap: true, others: false },
    { name: 'Tempo control', vibemap: true, others: true },
    { name: 'Audio feature analysis', vibemap: true, others: false },
    { name: 'No account required', vibemap: true, others: false },
    { name: 'Instant recommendations', vibemap: true, others: true },
  ];

  return (
    <section className="py-24 bg-dark-elevated">
      <div className="container px-6 max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <p className="font-mono text-xs text-spotify-green tracking-widest uppercase mb-6">Comparison</p>
          <h2 className="font-serif text-5xl md:text-6xl text-white mb-6">Why Choose VibeMap?</h2>
          <p className="text-text-secondary text-lg max-w-2xl mx-auto">
            VibeMap offers unique features that other music discovery tools simply don't have.
          </p>
        </div>

        {/* Comparison Table */}
        <div className="flex justify-center">
          <div className="bg-dark-base rounded-3xl overflow-hidden border border-dark-highlight">
            {/* Header Row */}
            <div className="grid grid-cols-3 border-b border-dark-highlight">
              <div className="p-6" />
              <div className="p-6 text-center border-l border-dark-highlight">
                <span className="font-semibold text-spotify-green text-lg">VibeMap</span>
              </div>
              <div className="p-6 text-center border-l border-dark-highlight">
                <span className="text-text-secondary">Others</span>
              </div>
            </div>

            {/* Feature Rows */}
            {features.map((feature, index) => (
              <div
                key={feature.name}
                className={`grid grid-cols-3 ${index !== features.length - 1 ? 'border-b border-dark-highlight' : ''}`}
              >
                <div className="p-6 flex items-center">
                  <span className="font-mono text-xs text-text-secondary">{feature.name}</span>
                </div>
                <div className="p-6 flex items-center justify-center border-l border-dark-highlight">
                  {feature.vibemap ? (
                    <div className="size-5 rounded-full bg-spotify-green/20 flex items-center justify-center">
                      <CheckIcon />
                    </div>
                  ) : (
                    <div className="size-5 rounded-full bg-dark-highlight flex items-center justify-center">
                      <CloseIcon />
                    </div>
                  )}
                </div>
                <div className="p-6 flex items-center justify-center border-l border-dark-highlight">
                  {feature.others ? (
                    <div className="size-5 rounded-full bg-dark-highlight flex items-center justify-center text-text-secondary">
                      <CheckIcon />
                    </div>
                  ) : (
                    <div className="size-5 rounded-full bg-dark-highlight flex items-center justify-center text-text-secondary">
                      <CloseIcon />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

// Testimonial Section
const TestimonialSection = () => {
  return (
    <section className="py-24 bg-dark-base">
      <div className="container px-6 max-w-5xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Image Placeholder */}
          <div className="aspect-square rounded-3xl bg-gradient-to-br from-spotify-green/20 to-mood-party/20 flex items-center justify-center">
            <div className="text-8xl">🎧</div>
          </div>

          {/* Quote */}
          <div className="border-t border-dark-highlight pt-10">
            <p className="font-serif text-3xl md:text-4xl text-white leading-snug mb-8">
              "VibeMap completely changed how I discover music. The mood-based recommendations are
              incredibly accurate - it's like having a DJ who truly understands my feelings."
            </p>
            <div className="flex items-center gap-4">
              <div>
                <p className="font-medium text-white">Music Enthusiast</p>
                <p className="font-mono text-xs text-spotify-green">Beta Tester</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// CTA Section
const CTASection = ({ onGetStarted }: { onGetStarted: () => void }) => {
  return (
    <section className="py-24 bg-gradient-to-br from-spotify-green to-spotify-green-dark">
      <div className="container px-6 max-w-4xl mx-auto text-center">
        <h2 className="font-serif text-5xl md:text-6xl text-white mb-6">
          Map Your Mood to Music
        </h2>
        <p className="text-white/80 text-lg mb-10 max-w-2xl mx-auto">
          Start discovering songs that match exactly how you feel. It's free, instant, and powered by ML.
        </p>
        <Button
          variant="primary"
          className="bg-white text-spotify-white hover:bg-gray\-100"
          onClick={onGetStarted}
        >
          Get Started Now
        </Button>
      </div>
    </section>
  );
};

// Getting Started Steps
const GettingStartedSection = () => {
  const steps = [
    {
      number: '01',
      title: 'Choose Your Mood',
      description: 'Select from 8 moods like happy, energetic, or calm.',
    },
    {
      number: '02',
      title: 'Set the Tempo',
      description: 'Pick slow, medium, or fast to match your energy.',
    },
    {
      number: '03',
      title: 'Get Recommendations',
      description: 'Instantly receive AI-curated song suggestions.',
    },
  ];

  return (
    <section className="py-24 bg-dark-elevated">
      <div className="container px-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="font-serif text-5xl md:text-6xl text-white mb-6">Get Started in Seconds</h2>
        </div>

        {/* Steps */}
        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step) => (
            <div key={step.number} className="border-t border-dark-highlight pt-16">
              <span className="font-mono text-7xl text-dark-highlight/30">{step.number}</span>
              <div className="mt-8">
                <h3 className="font-serif text-xl text-white mb-4">{step.title}</h3>
                <p className="text-text-secondary text-sm">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// Main Landing Page Component
const Landing = () => {
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);

  const handleGetStarted = () => {
    navigate('/recommendations');
  };

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Hero animations
      gsap.from('.hero-label', {
        y: 20,
        opacity: 0,
        duration: 0.8,
        ease: 'power3.out',
      });

      gsap.from('.hero-title', {
        y: 40,
        opacity: 0,
        duration: 1,
        delay: 0.2,
        ease: 'power3.out',
      });

      gsap.from('.hero-subtitle', {
        y: 30,
        opacity: 0,
        duration: 1,
        delay: 0.4,
        ease: 'power3.out',
      });

      gsap.from('.hero-buttons', {
        y: 20,
        opacity: 0,
        duration: 0.8,
        delay: 0.6,
        ease: 'power3.out',
      });

      gsap.from('.hero-moods', {
        y: 20,
        opacity: 0,
        duration: 0.8,
        delay: 0.8,
        ease: 'power3.out',
      });

      // Benefits animation
      gsap.from('.benefit-card', {
        scrollTrigger: {
          trigger: '.benefit-card',
          start: 'top 85%',
        },
        y: 40,
        opacity: 0,
        stagger: 0.15,
        duration: 0.8,
        ease: 'power2.out',
      });

      // Mood cards animation
      gsap.from('.mood-card', {
        scrollTrigger: {
          trigger: '.mood-card',
          start: 'top 85%',
        },
        scale: 0.9,
        opacity: 0,
        stagger: 0.1,
        duration: 0.6,
        ease: 'power2.out',
      });

      // Feature items animation
      gsap.from('.feature-item', {
        scrollTrigger: {
          trigger: '.feature-item',
          start: 'top 85%',
        },
        x: -30,
        opacity: 0,
        stagger: 0.15,
        duration: 0.8,
        ease: 'power2.out',
      });
    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className="min-h-screen bg-dark-base">
      <LandingHeader />
      <HeroSection onGetStarted={handleGetStarted} />
      <div id="benefits" className="scroll-mt-20">
        <BenefitsSection />
      </div>
      <div id="moods" className="scroll-mt-20">
        <MoodShowcase />
      </div>
      <div id="how-it-works" className="scroll-mt-20">
        <FeaturesSection onGetStarted={handleGetStarted} />
      </div>
      <ComparisonSection />
      <GettingStartedSection />
      <TestimonialSection />
      <CTASection onGetStarted={handleGetStarted} />
      <LandingFooter />
    </div>
  );
};

export default Landing;
