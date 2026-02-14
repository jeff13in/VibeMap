import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Music, Sparkles, Target, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

gsap.registerPlugin(ScrollTrigger);

const Home = () => {
  const navigate = useNavigate();
  const heroRef = useRef<HTMLDivElement>(null);
  const featuresRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from('.hero-title', {
        y: 50,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
      });

      gsap.from('.hero-subtitle', {
        y: 30,
        opacity: 0,
        duration: 1,
        delay: 0.3,
        ease: 'power3.out',
      });

      gsap.from('.hero-cta', {
        y: 20,
        opacity: 0,
        duration: 1,
        delay: 0.6,
        ease: 'power3.out',
      });

      gsap.from('.feature-card', {
        scrollTrigger: {
          trigger: '.features-section',
          start: 'top 80%',
        },
        y: 50,
        opacity: 0,
        stagger: 0.2,
        duration: 0.8,
        ease: 'power2.out',
      });
    });

    return () => ctx.revert();
  }, []);

  const features = [
    {
      icon: Sparkles,
      title: 'Mood-Based Discovery',
      description: 'Find songs that match your current mood with AI-powered recommendations.',
    },
    {
      icon: Zap,
      title: 'Tempo Filtering',
      description: 'Discover music by tempo - from slow ballads to high-energy tracks.',
    },
    {
      icon: Target,
      title: 'Similar Songs',
      description: 'Explore songs similar to your favorites using advanced ML algorithms.',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section
        ref={heroRef}
        className="relative overflow-hidden bg-gradient-to-br from-dark-base via-dark-elevated to-dark-highlight"
      >
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20" />
        <div className="container relative py-24 md:py-32">
          <div className="flex flex-col items-center text-center space-y-8">
            <div className="space-y-4">
              <h1 className="hero-title text-4xl md:text-6xl font-bold bg-gradient-to-r from-spotify-green-light via-spotify-green to-emerald-300 bg-clip-text text-transparent">
                Discover Your Perfect Playlist
              </h1>
              <p className="hero-subtitle text-xl md:text-2xl text-white/80 max-w-2xl mx-auto">
                AI-powered music recommendations based on mood, tempo, and your musical taste
              </p>
            </div>

            <div className="hero-cta flex flex-col sm:flex-row gap-4">
              <Button
                size="lg"
                className="bg-spotify-green hover:bg-spotify-green-dark text-lg px-8"
                onClick={() => navigate('/recommendations')}
              >
                <Music className="mr-2 h-5 w-5" />
                Start Discovering
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-spotify-green text-spotify-green hover:bg-spotify-green hover:text-white text-lg px-8"
                onClick={() => navigate('/recommendations')}
              >
                Learn More
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section ref={featuresRef} className="features-section py-24 bg-dark-base">
        <div className="container">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">How It Works</h2>
            <p className="text-white/70 text-lg max-w-2xl mx-auto">
              Powered by machine learning and clustering algorithms to deliver personalized music
              recommendations
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card
                  key={index}
                  className="feature-card bg-dark-elevated border-dark-highlight hover:border-spotify-green transition-colors"
                >
                  <CardHeader>
                    <div className="h-12 w-12 rounded-lg bg-spotify-green/20 flex items-center justify-center mb-4">
                      <Icon className="h-6 w-6 text-spotify-green" />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-text-secondary">{feature.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-spotify-green to-spotify-green-dark">
        <div className="container text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Discover New Music?</h2>
          <p className="text-lg mb-8 opacity-90">
            Get personalized recommendations in seconds
          </p>
          <Button
            size="lg"
            variant="secondary"
            className="bg-white text-black hover:bg-gray-100 text-lg px-8"
            onClick={() => navigate('/recommendations')}
          >
            Get Started Now
          </Button>
        </div>
      </section>
    </div>
  );
};

export default Home;
