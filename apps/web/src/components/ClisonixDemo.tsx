'use client';

import { useEffect, useState } from 'react';

export default function KloudDemo() {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  if (!isLoaded) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-neutral-900 via-purple-900 to-neutral-900">
      <div className="container mx-auto px-4 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-white mb-6">Kloud Cloud Demo</h1>
          <p className="text-xl text-purple-200 mb-12">
            Advanced Neural Intelligence Platform
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4">Brain AI</h2>
              <p className="text-purple-200">
                Advanced neural processing and intelligence engine
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4">Signal Processing</h2>
              <p className="text-purple-200">
                Real-time audio and signal analysis
              </p>
            </div>
            
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-4">Analytics</h2>
              <p className="text-purple-200">
                Comprehensive metrics and insights
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

