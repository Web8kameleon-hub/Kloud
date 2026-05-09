'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

/**
 * MOOD JOURNAL - Kloud Behavioral Science Module
 * 
 * Frontend: Simple emoji picker, one-tap logging
 * Backend: Sentiment analysis, temporal patterns, correlation engine
 * 
 * Research Goals:
 * - Circadian mood patterns
 * - Weather ↔ Mood correlation  
 * - Activity ↔ Emotional state mapping
 * - Predictive mood modeling
 */

interface MoodEntry {
  id: string;
  mood: number; // 1-5 scale
  emoji: string;
  note: string;
  timestamp: string;
  timeOfDay: 'morning' | 'afternoon' | 'evening' | 'night';
  factors: string[];
}

interface MoodStats {
  avgMood: number;
  totalEntries: number;
  streak: number;
  bestTimeOfDay: string;
  topFactors: string[];
  trend: 'improving' | 'stable' | 'declining';
}

const MOODS = [
  { value: 1, emoji: '😢', label: 'Shumë keq', color: 'from-red-500 to-red-600' },
  { value: 2, emoji: '😔', label: 'Keq', color: 'from-orange-500 to-orange-600' },
  { value: 3, emoji: '😐', label: 'Normale', color: 'from-yellow-500 to-yellow-600' },
  { value: 4, emoji: '😊', label: 'Mirë', color: 'from-green-500 to-green-600' },
  { value: 5, emoji: '🤩', label: 'Shkëlqyeshëm', color: 'from-blue-800 to-violet-500' },
];

const FACTORS = [
  { id: 'sleep', emoji: '😴', label: 'Gjumi' },
  { id: 'exercise', emoji: '🏃', label: 'Stërvitje' },
  { id: 'social', emoji: '👥', label: 'Shoqëri' },
  { id: 'work', emoji: '💼', label: 'Punë' },
  { id: 'food', emoji: '🍽️', label: 'Ushqim' },
  { id: 'weather', emoji: '🌤️', label: 'Moti' },
  { id: 'stress', emoji: '😰', label: 'Stres' },
  { id: 'family', emoji: '👨‍👩‍👧', label: 'Familje' },
];

export default function MoodJournalPage() {
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const [selectedFactors, setSelectedFactors] = useState<string[]>([]);
  const [note, setNote] = useState('');
  const [entries, setEntries] = useState<MoodEntry[]>([]);
  const [stats, setStats] = useState<MoodStats | null>(null);
  const [saving, setSaving] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [view, setView] = useState<'log' | 'history' | 'insights'>('log');

  // Load entries from localStorage + API
  useEffect(() => {
    const stored = localStorage.getItem('kloud_mood_entries');
    if (stored) {
      const parsed = JSON.parse(stored);
      setEntries(parsed);
      calculateStats(parsed);
    }
    // Sync with backend
    syncWithBackend();
  }, []);

  const syncWithBackend = async () => {
    try {
      const response = await fetch('/api/behavioral/mood/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entries: entries,
          deviceId: getDeviceId(),
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        })
      });
      if (response.ok) {
        const data = await response.json();
        if (data.stats) setStats(data.stats);
      }
    } catch (e) {
      // Offline mode - continue with local data
    }
  };

  const getDeviceId = () => {
    let id = localStorage.getItem('kloud_device_id');
    if (!id) {
      id = 'dev_' + Math.random().toString(36).substring(2, 15);
      localStorage.setItem('kloud_device_id', id);
    }
    return id;
  };

  const getTimeOfDay = (): 'morning' | 'afternoon' | 'evening' | 'night' => {
    const hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 17) return 'afternoon';
    if (hour >= 17 && hour < 21) return 'evening';
    return 'night';
  };

  const calculateStats = (data: MoodEntry[]) => {
    if (data.length === 0) {
      setStats(null);
      return;
    }

    const avgMood = data.reduce((sum, e) => sum + e.mood, 0) / data.length;
    
    // Calculate streak
    let streak = 0;
    const today = new Date().toDateString();
    const sortedDates = [...new Set(data.map(e => new Date(e.timestamp).toDateString()))].sort().reverse();
    
    for (let i = 0; i < sortedDates.length; i++) {
      const expected = new Date();
      expected.setDate(expected.getDate() - i);
      if (sortedDates[i] === expected.toDateString()) {
        streak++;
      } else break;
    }

    // Best time of day
    const timeGroups = data.reduce((acc, e) => {
      acc[e.timeOfDay] = acc[e.timeOfDay] || [];
      acc[e.timeOfDay].push(e.mood);
      return acc;
    }, {} as Record<string, number[]>);
    
    let bestTime = 'morning';
    let bestAvg = 0;
    Object.entries(timeGroups).forEach(([time, moods]) => {
      const avg = moods.reduce((a, b) => a + b, 0) / moods.length;
      if (avg > bestAvg) {
        bestAvg = avg;
        bestTime = time;
      }
    });

    // Top factors
    const factorCounts = data.flatMap(e => e.factors).reduce((acc, f) => {
      acc[f] = (acc[f] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const topFactors = Object.entries(factorCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([f]) => f);

    // Trend (last 7 days vs previous 7)
    const now = Date.now();
    const week = 7 * 24 * 60 * 60 * 1000;
    const recent = data.filter(e => now - new Date(e.timestamp).getTime() < week);
    const previous = data.filter(e => {
      const diff = now - new Date(e.timestamp).getTime();
      return diff >= week && diff < week * 2;
    });
    
    const recentAvg = recent.length ? recent.reduce((s, e) => s + e.mood, 0) / recent.length : 3;
    const prevAvg = previous.length ? previous.reduce((s, e) => s + e.mood, 0) / previous.length : 3;
    
    let trend: 'improving' | 'stable' | 'declining' = 'stable';
    if (recentAvg - prevAvg > 0.3) trend = 'improving';
    else if (prevAvg - recentAvg > 0.3) trend = 'declining';

    setStats({
      avgMood,
      totalEntries: data.length,
      streak,
      bestTimeOfDay: bestTime,
      topFactors,
      trend
    });
  };

  const handleSave = async () => {
    if (selectedMood === null) return;

    setSaving(true);
    const mood = MOODS.find(m => m.value === selectedMood)!;
    
    const entry: MoodEntry = {
      id: Date.now().toString(),
      mood: selectedMood,
      emoji: mood.emoji,
      note,
      timestamp: new Date().toISOString(),
      timeOfDay: getTimeOfDay(),
      factors: selectedFactors
    };

    const newEntries = [entry, ...entries];
    setEntries(newEntries);
    localStorage.setItem('kloud_mood_entries', JSON.stringify(newEntries));
    calculateStats(newEntries);

    // Send to backend for analysis
    try {
      await fetch('/api/behavioral/mood/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entry,
          deviceId: getDeviceId(),
          userAgent: navigator.userAgent,
          screenSize: `${window.innerWidth}x${window.innerHeight}`,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        })
      });
    } catch (e) {
      // Queued for later sync
    }

    setSaving(false);
    setShowSuccess(true);
    setSelectedMood(null);
    setSelectedFactors([]);
    setNote('');
    
    setTimeout(() => setShowSuccess(false), 2000);
  };

  const toggleFactor = (factorId: string) => {
    setSelectedFactors(prev => 
      prev.includes(factorId) 
        ? prev.filter(f => f !== factorId)
        : [...prev, factorId]
    );
  };

  const formatTime = (timeOfDay: string) => {
    const labels: Record<string, string> = {
      morning: '🌅 Mëngjes',
      afternoon: '☀️ Pasdite',
      evening: '🌆 Mbrëmje',
      night: '🌙 Natë'
    };
    return labels[timeOfDay] || timeOfDay;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-black/20 backdrop-blur-lg border-b border-white/10">
        <div className="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-white/60 hover:text-white">
            ← Kthehu
          </Link>
          <h1 className="text-xl font-bold text-white">😊 Mood Journal</h1>
          <div className="w-16"></div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-lg mx-auto px-4 pt-4">
        <div className="flex bg-white/10 rounded-2xl p-1">
          {[
            { id: 'log', label: '✏️ Log', icon: '' },
            { id: 'history', label: '📅 Historia', icon: '' },
            { id: 'insights', label: '📊 Insights', icon: '' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setView(tab.id as 'log' | 'history' | 'insights')}
              className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all ${
                view === tab.id 
                  ? 'bg-white text-purple-900' 
                  : 'text-white/70 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <main className="max-w-lg mx-auto px-4 py-6">
        {/* Success Animation */}
        {showSuccess && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-gradient-to-br from-green-500 to-blue-900 rounded-3xl p-8 text-center animate-bounce">
              <div className="text-6xl mb-4">✅</div>
              <p className="text-xl font-bold text-white">U ruajt!</p>
            </div>
          </div>
        )}

        {/* LOG VIEW */}
        {view === 'log' && (
          <div className="space-y-6">
            {/* Current Time */}
            <div className="text-center py-4">
              <p className="text-white/60 text-sm">
                {formatTime(getTimeOfDay())} • {new Date().toLocaleDateString('sq-AL', { weekday: 'long', day: 'numeric', month: 'long' })}
              </p>
              <h2 className="text-2xl font-bold text-white mt-2">Si ndihesh tani?</h2>
            </div>

            {/* Mood Selector - BIG BUTTONS */}
            <div className="grid grid-cols-5 gap-2">
              {MOODS.map(mood => (
                <button
                  key={mood.value}
                  onClick={() => setSelectedMood(mood.value)}
                  className={`aspect-square rounded-2xl flex flex-col items-center justify-center transition-all transform ${
                    selectedMood === mood.value
                      ? `bg-gradient-to-br ${mood.color} scale-110 shadow-lg shadow-white/20`
                      : 'bg-white/10 hover:bg-white/20 hover:scale-105'
                  }`}
                >
                  <span className="text-4xl">{mood.emoji}</span>
                  <span className={`text-xs mt-1 ${selectedMood === mood.value ? 'text-white' : 'text-white/60'}`}>
                    {mood.label}
                  </span>
                </button>
              ))}
            </div>

            {/* Factors */}
            {selectedMood && (
              <div className="space-y-3 animate-fadeIn">
                <p className="text-white/70 text-sm text-center">Çfarë ndikoi? (opsionale)</p>
                <div className="grid grid-cols-4 gap-2">
                  {FACTORS.map(factor => (
                    <button
                      key={factor.id}
                      onClick={() => toggleFactor(factor.id)}
                      className={`p-3 rounded-xl flex flex-col items-center gap-1 transition-all ${
                        selectedFactors.includes(factor.id)
                          ? 'bg-purple-500 text-white'
                          : 'bg-white/10 text-white/70 hover:bg-white/20'
                      }`}
                    >
                      <span className="text-2xl">{factor.emoji}</span>
                      <span className="text-xs">{factor.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Note */}
            {selectedMood && (
              <div className="animate-fadeIn">
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="Shënim i shkurtër... (opsionale)"
                  className="w-full bg-white/10 border border-white/20 rounded-2xl p-4 text-white placeholder-white/40 focus:outline-none focus:border-purple-500 resize-none"
                  rows={3}
                />
              </div>
            )}

            {/* Save Button */}
            {selectedMood && (
              <button
                onClick={handleSave}
                disabled={saving}
                className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl text-white font-bold text-lg shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transition-all disabled:opacity-50"
              >
                {saving ? '⏳ Duke ruajtur...' : '💾 Ruaj'}
              </button>
            )}

            {/* Quick Stats */}
            {stats && (
              <div className="grid grid-cols-3 gap-3 pt-4">
                <div className="bg-white/10 rounded-2xl p-4 text-center">
                  <p className="text-3xl">🔥</p>
                  <p className="text-2xl font-bold text-white">{stats.streak}</p>
                  <p className="text-xs text-white/60">ditë streak</p>
                </div>
                <div className="bg-white/10 rounded-2xl p-4 text-center">
                  <p className="text-3xl">{MOODS[Math.round(stats.avgMood) - 1]?.emoji || '😐'}</p>
                  <p className="text-2xl font-bold text-white">{stats.avgMood.toFixed(1)}</p>
                  <p className="text-xs text-white/60">mesatare</p>
                </div>
                <div className="bg-white/10 rounded-2xl p-4 text-center">
                  <p className="text-3xl">📝</p>
                  <p className="text-2xl font-bold text-white">{stats.totalEntries}</p>
                  <p className="text-xs text-white/60">regjistrime</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* HISTORY VIEW */}
        {view === 'history' && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-white">📅 Historia jote</h2>
            
            {entries.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-6xl mb-4">📝</p>
                <p className="text-white/60">Nuk ke asnjë regjistrim ende</p>
                <button
                  onClick={() => setView('log')}
                  className="mt-4 px-6 py-2 bg-purple-500 rounded-full text-white"
                >
                  Fillo tani
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {entries.slice(0, 20).map(entry => (
                  <div key={entry.id} className="bg-white/10 rounded-2xl p-4">
                    <div className="flex items-center gap-4">
                      <span className="text-4xl">{entry.emoji}</span>
                      <div className="flex-1">
                        <p className="text-white font-medium">
                          {formatTime(entry.timeOfDay)}
                        </p>
                        <p className="text-white/60 text-sm">
                          {new Date(entry.timestamp).toLocaleDateString('sq-AL', {
                            day: 'numeric',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                        {entry.note && (
                          <p className="text-white/80 text-sm mt-1 italic">&quot;{entry.note}&quot;</p>
                        )}
                      </div>
                    </div>
                    {entry.factors.length > 0 && (
                      <div className="flex gap-2 mt-3 flex-wrap">
                        {entry.factors.map(f => {
                          const factor = FACTORS.find(x => x.id === f);
                          return factor ? (
                            <span key={f} className="px-2 py-1 bg-white/10 rounded-full text-xs text-white/70">
                              {factor.emoji} {factor.label}
                            </span>
                          ) : null;
                        })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* INSIGHTS VIEW */}
        {view === 'insights' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-white">📊 Insights nga AI</h2>
            
            {!stats || stats.totalEntries < 5 ? (
              <div className="text-center py-12 bg-white/5 rounded-2xl">
                <p className="text-6xl mb-4">🔮</p>
                <p className="text-white/60">Duhen të paktën 5 regjistrime për insights</p>
                <p className="text-white/40 text-sm mt-2">Ke {stats?.totalEntries || 0}/5</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Trend Card */}
                <div className={`p-6 rounded-2xl ${
                  stats.trend === 'improving' ? 'bg-gradient-to-br from-green-500/20 to-blue-800/20 border border-green-500/30' :
                  stats.trend === 'declining' ? 'bg-gradient-to-br from-red-500/20 to-orange-500/20 border border-red-500/30' :
                  'bg-gradient-to-br from-violet-500/20 to-violet-500/20 border border-violet-500/30'
                }`}>
                  <div className="flex items-center gap-4">
                    <span className="text-5xl">
                      {stats.trend === 'improving' ? '📈' : stats.trend === 'declining' ? '📉' : '➡️'}
                    </span>
                    <div>
                      <p className="text-white font-bold text-lg">
                        {stats.trend === 'improving' ? 'Duke u përmirësuar!' : 
                         stats.trend === 'declining' ? 'Trend në rënie' : 'I qëndrueshëm'}
                      </p>
                      <p className="text-white/60 text-sm">
                        Krahasuar me javën e kaluar
                      </p>
                    </div>
                  </div>
                </div>

                {/* Best Time */}
                <div className="bg-white/10 rounded-2xl p-6">
                  <p className="text-white/60 text-sm">Koha jote më e mirë</p>
                  <p className="text-2xl font-bold text-white mt-1">
                    {formatTime(stats.bestTimeOfDay)}
                  </p>
                  <p className="text-white/60 text-sm mt-2">
                    Ndihesh më mirë në këtë kohë të ditës
                  </p>
                </div>

                {/* Top Factors */}
                {stats.topFactors.length > 0 && (
                  <div className="bg-white/10 rounded-2xl p-6">
                    <p className="text-white/60 text-sm mb-3">Faktorët më të shpeshtë</p>
                    <div className="flex gap-3">
                      {stats.topFactors.map(f => {
                        const factor = FACTORS.find(x => x.id === f);
                        return factor ? (
                          <div key={f} className="flex-1 text-center bg-white/10 rounded-xl p-3">
                            <span className="text-3xl">{factor.emoji}</span>
                            <p className="text-white text-sm mt-1">{factor.label}</p>
                          </div>
                        ) : null;
                      })}
                    </div>
                  </div>
                )}

                {/* AI Recommendation */}
                <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-2xl p-6">
                  <div className="flex items-start gap-3">
                    <span className="text-3xl">🤖</span>
                    <div>
                      <p className="text-white font-bold">Rekomandim AI</p>
                      <p className="text-white/80 text-sm mt-2">
                        Bazuar në të dhënat e tua, {stats.trend === 'improving' 
                          ? 'vazhdo kështu! Streak-u yt po ndikon pozitivisht.'
                          : stats.trend === 'declining'
                          ? 'provo të fokusohesh më shumë tek gjumi dhe stërvitja.'
                          : 'je në rrugë të mirë. Provo të shtosh pak më shumë aktivitet social.'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Bottom Padding for mobile */}
      <div className="h-20"></div>
    </div>
  );
}








