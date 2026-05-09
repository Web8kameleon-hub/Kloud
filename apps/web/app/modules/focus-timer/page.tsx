'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';

/**
 * FOCUS TIMER (Pomodoro) - Kloud Productivity Science Module
 * 
 * Frontend: Beautiful timer, one-tap start, ambient sounds
 * Backend: Focus pattern analysis, optimal work/break ratios, productivity curves
 * 
 * Research Goals:
 * - Individual optimal focus duration
 * - Time-of-day productivity mapping
 * - Task completion vs focus session correlation
 * - Attention span trends over time
 */

interface FocusSession {
  id: string;
  type: 'focus' | 'break';
  duration: number; // minutes
  completed: boolean;
  startedAt: string;
  endedAt?: string;
  task?: string;
  interrupted: boolean;
}

interface FocusStats {
  totalFocusMinutes: number;
  totalSessions: number;
  completionRate: number;
  avgSessionLength: number;
  bestHour: number;
  streak: number;
}

const TIMER_PRESETS = [
  { focus: 25, break: 5, name: 'Pomodoro', emoji: '🍅' },
  { focus: 50, break: 10, name: 'Deep Work', emoji: '🧠' },
  { focus: 15, break: 3, name: 'Sprint', emoji: '⚡' },
  { focus: 90, break: 20, name: 'Flow State', emoji: '🌊' },
];

const AMBIENT_SOUNDS = [
  { id: 'none', name: 'Heshtje', emoji: '🔇' },
  { id: 'rain', name: 'Shi', emoji: '🌧️' },
  { id: 'forest', name: 'Pyll', emoji: '🌲' },
  { id: 'cafe', name: 'Kafene', emoji: '☕' },
  { id: 'waves', name: 'Dallgë', emoji: '🌊' },
  { id: 'fire', name: 'Zjarr', emoji: '🔥' },
];

export default function FocusTimerPage() {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [mode, setMode] = useState<'focus' | 'break'>('focus');
  const [timeLeft, setTimeLeft] = useState(25 * 60); // seconds
  const [selectedPreset, setSelectedPreset] = useState(TIMER_PRESETS[0]);
  const [sessions, setSessions] = useState<FocusSession[]>([]);
  const [stats, setStats] = useState<FocusStats | null>(null);
  const [currentTask, setCurrentTask] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [ambientSound, setAmbientSound] = useState('none');
  const [view, setView] = useState<'timer' | 'stats'>('timer');
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Load saved data
    const stored = localStorage.getItem('kloud_focus_sessions');
    if (stored) {
      const parsed = JSON.parse(stored);
      setSessions(parsed);
      calculateStats(parsed);
    }
    
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const calculateStats = (sessionData: FocusSession[]) => {
    const focusSessions = sessionData.filter(s => s.type === 'focus');
    const completedSessions = focusSessions.filter(s => s.completed);
    
    const totalMinutes = focusSessions.reduce((sum, s) => {
      if (s.completed) return sum + s.duration;
      if (s.endedAt) {
        const elapsed = (new Date(s.endedAt).getTime() - new Date(s.startedAt).getTime()) / 60000;
        return sum + Math.min(elapsed, s.duration);
      }
      return sum;
    }, 0);

    // Best hour analysis
    const hourCounts: Record<number, number> = {};
    completedSessions.forEach(s => {
      const hour = new Date(s.startedAt).getHours();
      hourCounts[hour] = (hourCounts[hour] || 0) + 1;
    });
    const bestHour = Object.entries(hourCounts)
      .sort((a, b) => b[1] - a[1])[0]?.[0] || 9;

    // Streak calculation
    let streak = 0;
    const today = new Date().toDateString();
    for (let i = 0; i < 365; i++) {
      const checkDate = new Date();
      checkDate.setDate(checkDate.getDate() - i);
      const dateStr = checkDate.toDateString();
      const hasSession = focusSessions.some(s => new Date(s.startedAt).toDateString() === dateStr && s.completed);
      if (hasSession) streak++;
      else if (i > 0) break;
    }

    setStats({
      totalFocusMinutes: Math.round(totalMinutes),
      totalSessions: focusSessions.length,
      completionRate: focusSessions.length > 0 ? completedSessions.length / focusSessions.length : 0,
      avgSessionLength: completedSessions.length > 0 
        ? completedSessions.reduce((sum, s) => sum + s.duration, 0) / completedSessions.length 
        : 0,
      bestHour: parseInt(bestHour as string),
      streak
    });
  };

  const startTimer = () => {
    if (isRunning) return;

    const sessionId = Date.now().toString();
    setCurrentSessionId(sessionId);
    
    const newSession: FocusSession = {
      id: sessionId,
      type: mode,
      duration: mode === 'focus' ? selectedPreset.focus : selectedPreset.break,
      completed: false,
      startedAt: new Date().toISOString(),
      task: currentTask || undefined,
      interrupted: false
    };

    const newSessions = [...sessions, newSession];
    setSessions(newSessions);
    localStorage.setItem('kloud_focus_sessions', JSON.stringify(newSessions));

    setIsRunning(true);
    setIsPaused(false);
    setTimeLeft((mode === 'focus' ? selectedPreset.focus : selectedPreset.break) * 60);

    // Send to backend
    logToBackend('start', newSession);
  };

  const logToBackend = async (action: string, session: FocusSession) => {
    try {
      await fetch('/api/behavioral/focus/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action,
          session,
          deviceId: getDeviceId(),
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        })
      });
    } catch (e) {}
  };

  const getDeviceId = () => {
    let id = localStorage.getItem('kloud_device_id');
    if (!id) {
      id = 'dev_' + Math.random().toString(36).substring(2, 15);
      localStorage.setItem('kloud_device_id', id);
    }
    return id;
  };

  const pauseTimer = () => {
    setIsPaused(true);
    if (timerRef.current) clearInterval(timerRef.current);
  };

  const resumeTimer = () => {
    setIsPaused(false);
  };

  const stopTimer = (completed: boolean = false) => {
    setIsRunning(false);
    setIsPaused(false);
    if (timerRef.current) clearInterval(timerRef.current);

    if (currentSessionId) {
      const updatedSessions = sessions.map(s => 
        s.id === currentSessionId 
          ? { ...s, completed, endedAt: new Date().toISOString(), interrupted: !completed }
          : s
      );
      setSessions(updatedSessions);
      localStorage.setItem('kloud_focus_sessions', JSON.stringify(updatedSessions));
      calculateStats(updatedSessions);

      const session = updatedSessions.find(s => s.id === currentSessionId);
      if (session) logToBackend(completed ? 'complete' : 'interrupt', session);
    }

    if (completed) {
      // Switch mode
      if (mode === 'focus') {
        setMode('break');
        setTimeLeft(selectedPreset.break * 60);
      } else {
        setMode('focus');
        setTimeLeft(selectedPreset.focus * 60);
      }
      
      // Notify
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(mode === 'focus' ? '⏰ Koha për pushim!' : '💪 Kthehu në punë!');
      }
    } else {
      setTimeLeft((mode === 'focus' ? selectedPreset.focus : selectedPreset.break) * 60);
    }

    setCurrentSessionId(null);
  };

  // Timer tick
  useEffect(() => {
    if (isRunning && !isPaused) {
      timerRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            stopTimer(true);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isRunning, isPaused]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgress = () => {
    const total = (mode === 'focus' ? selectedPreset.focus : selectedPreset.break) * 60;
    return ((total - timeLeft) / total) * 100;
  };

  const formatHour = (hour: number) => {
    return `${hour.toString().padStart(2, '0')}:00`;
  };

  const todaySessions = sessions.filter(s => 
    new Date(s.startedAt).toDateString() === new Date().toDateString() && 
    s.type === 'focus' && 
    s.completed
  );

  return (
    <div className={`min-h-screen transition-colors duration-500 ${
      mode === 'focus' 
        ? 'bg-gradient-to-br from-slate-900 via-red-900/30 to-slate-900' 
        : 'bg-gradient-to-br from-slate-900 via-green-900/30 to-slate-900'
    }`}>
      {/* Header */}
      <header className="sticky top-0 z-50 bg-black/20 backdrop-blur-lg border-b border-white/10">
        <div className="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-white/60 hover:text-white">
            ← Kthehu
          </Link>
          <h1 className="text-xl font-bold text-white">⏱️ Focus Timer</h1>
          <button 
            onClick={() => setShowSettings(true)}
            className="text-white/60 hover:text-white text-xl"
          >
            ⚙️
          </button>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-lg mx-auto px-4 pt-4">
        <div className="flex bg-white/10 rounded-2xl p-1">
          <button
            onClick={() => setView('timer')}
            className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all ${
              view === 'timer' ? 'bg-white text-slate-900' : 'text-white/70 hover:text-white'
            }`}
          >
            ⏱️ Timer
          </button>
          <button
            onClick={() => setView('stats')}
            className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all ${
              view === 'stats' ? 'bg-white text-slate-900' : 'text-white/70 hover:text-white'
            }`}
          >
            📊 Stats
          </button>
        </div>
      </div>

      <main className="max-w-lg mx-auto px-4 py-6">
        {/* Settings Modal */}
        {showSettings && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-slate-800 rounded-3xl p-6 w-full max-w-sm">
              <h3 className="text-xl font-bold text-white mb-4">⚙️ Cilësimet</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="text-white/60 text-sm">Preset</label>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    {TIMER_PRESETS.map(preset => (
                      <button
                        key={preset.name}
                        onClick={() => {
                          setSelectedPreset(preset);
                          if (!isRunning) {
                            setTimeLeft(preset.focus * 60);
                          }
                        }}
                        className={`p-3 rounded-xl text-left ${
                          selectedPreset.name === preset.name 
                            ? 'bg-red-500 text-white' 
                            : 'bg-white/10 text-white/70'
                        }`}
                      >
                        <span className="text-xl">{preset.emoji}</span>
                        <p className="font-medium">{preset.name}</p>
                        <p className="text-xs opacity-70">{preset.focus}/{preset.break} min</p>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-white/60 text-sm">Tingull ambienti</label>
                  <div className="grid grid-cols-3 gap-2 mt-2">
                    {AMBIENT_SOUNDS.map(sound => (
                      <button
                        key={sound.id}
                        onClick={() => setAmbientSound(sound.id)}
                        className={`p-2 rounded-xl text-center ${
                          ambientSound === sound.id 
                            ? 'bg-violet-500 text-white' 
                            : 'bg-white/10 text-white/70'
                        }`}
                      >
                        <span className="text-xl">{sound.emoji}</span>
                        <p className="text-xs mt-1">{sound.name}</p>
                      </button>
                    ))}
                  </div>
                </div>

                <button
                  onClick={() => setShowSettings(false)}
                  className="w-full py-3 bg-white/10 rounded-xl text-white mt-4"
                >
                  Mbyll
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TIMER VIEW */}
        {view === 'timer' && (
          <div className="space-y-6">
            {/* Mode Indicator */}
            <div className="text-center">
              <span className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${
                mode === 'focus' 
                  ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                  : 'bg-green-500/20 text-green-400 border border-green-500/30'
              }`}>
                {mode === 'focus' ? '🎯 Fokus' : '☕ Pushim'}
              </span>
            </div>

            {/* Timer Circle */}
            <div className="flex justify-center py-8">
              <div className="relative w-64 h-64">
                {/* Background circle */}
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="128" cy="128" r="120"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="128" cy="128" r="120"
                    stroke={mode === 'focus' ? '#ef4444' : '#22c55e'}
                    strokeWidth="8"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={`${getProgress() * 7.54} 754`}
                    className="transition-all duration-1000"
                  />
                </svg>

                {/* Timer Display */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-6xl font-bold text-white font-mono">
                    {formatTime(timeLeft)}
                  </span>
                  <span className="text-white/60 mt-2">
                    {selectedPreset.emoji} {selectedPreset.name}
                  </span>
                </div>
              </div>
            </div>

            {/* Task Input */}
            {!isRunning && mode === 'focus' && (
              <div>
                <input
                  type="text"
                  value={currentTask}
                  onChange={(e) => setCurrentTask(e.target.value)}
                  placeholder="Çfarë do të punosh? (opsionale)"
                  className="w-full bg-white/10 border border-white/20 rounded-2xl p-4 text-white placeholder-white/40 focus:outline-none focus:border-red-500 text-center"
                />
              </div>
            )}

            {/* Control Buttons */}
            <div className="flex justify-center gap-4">
              {!isRunning ? (
                <button
                  onClick={startTimer}
                  className={`w-20 h-20 rounded-full flex items-center justify-center text-3xl shadow-lg transition-all transform hover:scale-105 ${
                    mode === 'focus' 
                      ? 'bg-gradient-to-br from-red-500 to-red-600 shadow-red-500/30' 
                      : 'bg-gradient-to-br from-green-500 to-green-600 shadow-green-500/30'
                  }`}
                >
                  ▶️
                </button>
              ) : (
                <>
                  {isPaused ? (
                    <button
                      onClick={resumeTimer}
                      className="w-16 h-16 bg-yellow-500 rounded-full flex items-center justify-center text-2xl shadow-lg shadow-yellow-500/30"
                    >
                      ▶️
                    </button>
                  ) : (
                    <button
                      onClick={pauseTimer}
                      className="w-16 h-16 bg-yellow-500 rounded-full flex items-center justify-center text-2xl shadow-lg shadow-yellow-500/30"
                    >
                      ⏸️
                    </button>
                  )}
                  <button
                    onClick={() => stopTimer(false)}
                    className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center text-2xl"
                  >
                    ⏹️
                  </button>
                </>
              )}
            </div>

            {/* Today's Progress */}
            <div className="bg-white/10 rounded-2xl p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🍅</span>
                  <div>
                    <p className="text-white font-medium">Sesione sot</p>
                    <p className="text-white/60 text-sm">
                      {todaySessions.reduce((sum, s) => sum + s.duration, 0)} minuta fokus
                    </p>
                  </div>
                </div>
                <div className="flex gap-1">
                  {[...Array(Math.min(todaySessions.length, 8))].map((_, i) => (
                    <div key={i} className="w-3 h-3 bg-red-500 rounded-full"></div>
                  ))}
                  {todaySessions.length > 8 && (
                    <span className="text-white/60 text-xs ml-1">+{todaySessions.length - 8}</span>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Tips */}
            {!isRunning && (
              <div className="bg-white/5 rounded-2xl p-4 text-center">
                <p className="text-white/60 text-sm">
                  💡 Tip: Hiq të gjitha shpërqendrimet përpara se të fillosh
                </p>
              </div>
            )}
          </div>
        )}

        {/* STATS VIEW */}
        {view === 'stats' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-white">📊 Statistikat e fokusit</h2>

            {!stats || stats.totalSessions === 0 ? (
              <div className="text-center py-12 bg-white/5 rounded-2xl">
                <p className="text-6xl mb-4">⏱️</p>
                <p className="text-white/60">Fillo sesionin e parë</p>
              </div>
            ) : (
              <>
                {/* Main Stats */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-gradient-to-br from-red-500/20 to-orange-500/20 border border-red-500/30 rounded-2xl p-4 text-center">
                    <p className="text-3xl">⏱️</p>
                    <p className="text-2xl font-bold text-white">{stats.totalFocusMinutes}</p>
                    <p className="text-xs text-white/60">minuta totale</p>
                  </div>
                  <div className="bg-gradient-to-br from-green-500/20 to-blue-800/20 border border-green-500/30 rounded-2xl p-4 text-center">
                    <p className="text-3xl">🔥</p>
                    <p className="text-2xl font-bold text-white">{stats.streak}</p>
                    <p className="text-xs text-white/60">ditë streak</p>
                  </div>
                  <div className="bg-gradient-to-br from-violet-500/20 to-violet-500/20 border border-violet-500/30 rounded-2xl p-4 text-center">
                    <p className="text-3xl">🍅</p>
                    <p className="text-2xl font-bold text-white">{stats.totalSessions}</p>
                    <p className="text-xs text-white/60">sesione</p>
                  </div>
                  <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-2xl p-4 text-center">
                    <p className="text-3xl">✅</p>
                    <p className="text-2xl font-bold text-white">{Math.round(stats.completionRate * 100)}%</p>
                    <p className="text-xs text-white/60">përfunduar</p>
                  </div>
                </div>

                {/* Best Hour */}
                <div className="bg-white/10 rounded-2xl p-6">
                  <div className="flex items-center gap-4">
                    <span className="text-4xl">⭐</span>
                    <div>
                      <p className="text-white/60 text-sm">Ora jote më produktive</p>
                      <p className="text-2xl font-bold text-white">{formatHour(stats.bestHour)}</p>
                      <p className="text-white/60 text-sm">Provo të planifikosh punë të rëndësishme këtu</p>
                    </div>
                  </div>
                </div>

                {/* Recent Sessions */}
                <div className="bg-white/10 rounded-2xl p-4">
                  <p className="text-white font-medium mb-3">Sesionet e fundit</p>
                  <div className="space-y-2">
                    {sessions
                      .filter(s => s.type === 'focus')
                      .slice(-5)
                      .reverse()
                      .map(session => (
                        <div key={session.id} className="flex items-center justify-between py-2 border-b border-white/10 last:border-0">
                          <div className="flex items-center gap-3">
                            <span className={session.completed ? 'text-green-400' : 'text-red-400'}>
                              {session.completed ? '✅' : '❌'}
                            </span>
                            <div>
                              <p className="text-white text-sm">{session.task || 'Fokus'}</p>
                              <p className="text-white/50 text-xs">
                                {new Date(session.startedAt).toLocaleDateString('sq-AL', {
                                  day: 'numeric',
                                  month: 'short',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </p>
                            </div>
                          </div>
                          <span className="text-white/60 text-sm">{session.duration} min</span>
                        </div>
                      ))}
                  </div>
                </div>

                {/* AI Insight */}
                <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-2xl p-6">
                  <div className="flex items-start gap-3">
                    <span className="text-3xl">🤖</span>
                    <div>
                      <p className="text-white font-bold">Insight nga AI</p>
                      <p className="text-white/80 text-sm mt-2">
                        {stats.completionRate >= 0.8
                          ? `Shkëlqyeshëm! Ke ${Math.round(stats.completionRate * 100)}% përfundim. Ora ${formatHour(stats.bestHour)} është optimale për ty.`
                          : stats.completionRate >= 0.5
                          ? 'Provo sesione më të shkurtra. Fokusi optimal varion nga personi.'
                          : 'Shumë sesione të ndërprera. Fillo me 15 minuta dhe rrit gradualisht.'}
                      </p>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </main>

      <div className="h-20"></div>
    </div>
  );
}








