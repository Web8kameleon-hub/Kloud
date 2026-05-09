'use client';

import { useState } from 'react';
import Link from 'next/link';

/**
 * KLOUD VIRAL REELS CREATOR
 * Professional short-form video generation
 */

const VIDEO_FORMATS = [
  {
    id: 'history',
    name: 'History Reel',
    icon: '📚',
    description: 'Timeline stories, historical events, educational content',
    duration: 90,
    aspectRatio: '9:16',
    badge: 'Most Popular'
  },
  {
    id: 'reel',
    name: 'Instagram Reel',
    icon: '📸',
    description: 'Vertical video optimized for Instagram',
    duration: 60,
    aspectRatio: '9:16'
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: '🎵',
    description: 'Music-driven, trending format',
    duration: 60,
    aspectRatio: '9:16'
  },
  {
    id: 'short',
    name: 'YouTube Short',
    icon: '▶️',
    description: 'Vertical, short-form video',
    duration: 60,
    aspectRatio: '9:16'
  }
];

const EXAMPLE_TOPICS = [
  'Perandoria Romake në 60 sekonda',
  'Napoleon Bonaparte - nga oficeri në perandor',
  'Lufta e Parë Botërore - shkaku dhe pasoja',
  'Revolucioni Francez - çfarë ndryshoi',
  'Perandoria Osmane - 600 vite pushtet',
  'Aleksandri i Madh - fajdeci i botës',
  'Mesopotamia Antike - lindja e qytetërimit',
  'Lufta e Dytë Botërore - në 60 sekonda'
];

export default function CreatePage() {
  const [topic, setTopic] = useState('Revolucioni Francez në 60 sekonda');
  const [selectedFormat, setSelectedFormat] = useState('history');
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [jobId, setJobId] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError('Shkruani temën e videos');
      return;
    }

    setIsGenerating(true);
    setProgress(10);
    setError(null);
    setVideoUrl(null);

    try {
      const response = await fetch('/api/video/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topic.trim(),
          style: selectedFormat === 'history' ? 'documentary' : 'social_media',
          voice: 'narrator',
          add_subtitles: true,
          format: selectedFormat
        })
      });

      if (!response.ok) {
        throw new Error('Video generation failed');
      }

      const data = await response.json();
      setJobId(data.job_id);
      setProgress(30);

      pollJobStatus(data.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Gabim në gjenerimin e videos');
      setIsGenerating(false);
    }
  };

  const pollJobStatus = async (id: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/video/status/${id}`);
        const data = await response.json();

        if (data.status === 'completed') {
          clearInterval(interval);
          setVideoUrl(data.result?.video_url);
          setProgress(100);
          setIsGenerating(false);
        } else if (data.status === 'failed') {
          clearInterval(interval);
          setError('Video generation failed. Try again.');
          setIsGenerating(false);
        } else if (data.status === 'processing') {
          setProgress(Math.min(90, progress + Math.random() * 15));
        }
      } catch (err) {
        clearInterval(interval);
        setError('Status check failed');
        setIsGenerating(false);
      }
    }, 1500);

    setTimeout(() => {
      clearInterval(interval);
      if (isGenerating) {
        setError('Generation timeout');
        setIsGenerating(false);
      }
    }, 300000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <span className="text-2xl">🎬</span>
            <span className="text-sm font-semibold text-slate-300 group-hover:text-white transition-colors">
              KLOUD CREATOR
            </span>
          </Link>
          <nav className="flex gap-6 text-sm">
            <Link href="/gallery" className="text-slate-400 hover:text-slate-200 transition-colors">
              Gallery
            </Link>
            <Link href="/" className="text-slate-400 hover:text-slate-200 transition-colors">
              Home
            </Link>
          </nav>
        </div>
      </header>

      {/* Main */}
      <main className="container mx-auto px-4 py-8 max-w-5xl">
        {!videoUrl ? (
          <>
            {/* Hero */}
            <div className="text-center mb-12">
              <h1 className="text-5xl md:text-6xl font-bold text-white mb-4 leading-tight">
                Create Viral Reels
              </h1>
              <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                AI-generated short-form videos for social media. Professional quality in minutes.
              </p>
            </div>

            {/* Format Selection */}
            <div className="mb-12">
              <label className="block text-white font-semibold mb-6 text-lg">
                Select Format
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {VIDEO_FORMATS.map((format) => (
                  <button
                    key={format.id}
                    onClick={() => setSelectedFormat(format.id)}
                    disabled={isGenerating}
                    className={`relative p-5 rounded-xl border-2 transition-all ${
                      selectedFormat === format.id
                        ? 'border-blue-500 bg-blue-500/15 shadow-lg shadow-blue-500/20'
                        : 'border-slate-700 bg-slate-800/50 hover:border-slate-600 hover:bg-slate-800'
                    } disabled:opacity-50`}
                  >
                    {format.badge && (
                      <div className="absolute -top-2 -right-2 px-2 py-1 bg-blue-600 text-white text-xs rounded-full">
                        {format.badge}
                      </div>
                    )}
                    <div className="text-4xl mb-2">{format.icon}</div>
                    <div className="text-white font-semibold text-sm mb-1">{format.name}</div>
                    <div className="text-slate-400 text-xs leading-relaxed">{format.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Topic Input */}
            <div className="mb-10">
              <label className="block text-white font-semibold mb-4 text-lg">
                Video Topic
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. Revolucioni Francez në 60 sekonda"
                disabled={isGenerating}
                className="w-full px-5 py-4 rounded-xl bg-slate-800 border-2 border-slate-700 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none text-base transition-colors disabled:opacity-50"
              />

              {/* Quick Examples */}
              <div className="mt-5">
                <p className="text-slate-400 text-sm mb-3 font-medium">Quick Examples:</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {EXAMPLE_TOPICS.map((t, idx) => (
                    <button
                      key={idx}
                      onClick={() => setTopic(t)}
                      disabled={isGenerating}
                      className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm transition-colors text-left disabled:opacity-50"
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !topic.trim()}
              className="w-full py-5 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98] shadow-xl shadow-blue-600/20"
            >
              {isGenerating ? (
                <span className="flex items-center justify-center gap-3">
                  <span className="inline-block animate-spin">⏳</span>
                  Generating {progress}%
                </span>
              ) : (
                <span>🎬 Generate Video</span>
              )}
            </button>

            {/* Progress Bar */}
            {isGenerating && (
              <div className="mt-6">
                <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500 rounded-full"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/50 text-red-300 text-sm">
                ❌ {error}
              </div>
            )}
          </>
        ) : (
          /* Success State */
          <div className="space-y-8">
            <div className="text-center">
              <div className="inline-block p-3 bg-green-500/20 border border-green-500/50 rounded-full mb-4">
                <span className="text-3xl">✅</span>
              </div>
              <h2 className="text-3xl font-bold text-white mb-2">Your video is ready!</h2>
              <p className="text-slate-400">Download and share on your favorite platform</p>
            </div>

            {/* Video Preview */}
            <div className="flex justify-center">
              <div className="aspect-[9/16] w-full max-w-sm bg-black rounded-2xl overflow-hidden shadow-2xl border border-slate-700">
                <video src={videoUrl} controls autoPlay muted loop className="w-full h-full" />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4 justify-center flex-wrap">
              <a
                href={videoUrl}
                download
                className="px-8 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-colors"
              >
                ⬇️ Download
              </a>
              <button
                onClick={() => {
                  setVideoUrl(null);
                  setTopic('');
                  setError(null);
                }}
                className="px-8 py-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-semibold transition-colors"
              >
                ➕ Create Another
              </button>
            </div>

            {/* Share Info */}
            <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
              <p className="text-slate-300 text-sm">
                💡 <strong>Pro Tip:</strong> Videos are optimized for TikTok (9:16), Instagram Reels, and YouTube Shorts. Download and upload directly!
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950/50 backdrop-blur-xl mt-20">
        <div className="container mx-auto px-4 py-8 text-center text-slate-500 text-sm">
          <p>Powered by <span className="text-blue-400 font-semibold">Kloud AI</span> • Professional Video Generation</p>
        </div>
      </footer>
    </div>
  );
}

