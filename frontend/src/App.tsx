import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Landing from '@/pages/Landing';
import Recommendations from '@/pages/Recommendations';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import './App.css';

gsap.registerPlugin(ScrollTrigger);

function AppContent() {
  const appRef = useRef<HTMLDivElement>(null);
  const location = useLocation();
  const isLandingPage = location.pathname === '/';

  useEffect(() => {
    if (appRef.current) {
      gsap.fromTo(appRef.current, { opacity: 0 }, {
        opacity: 1,
        duration: 0.5,
        ease: 'power2.out',
      });
    }
  }, []);

  return (
    <div ref={appRef} className="min-h-screen bg-dark-base text-text-primary flex flex-col">
      {!isLandingPage && <Header />}
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/recommendations" element={<Recommendations />} />
        </Routes>
      </main>
      {!isLandingPage && <Footer />}
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
