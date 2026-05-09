'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

/**
 * DAILY HABITS TRACKER - Kloud Behavioral Science Module
 * 
 * Frontend: One-tap habit checking, visual streaks, gamification
 * Backend: Habit formation analysis, adherence patterns, optimal scheduling
 * 
 * Research Goals:
 * - Habit formation curves (21-day myth vs reality)
 * - Time-of-day completion patterns
 * - Habit stacking effectiveness
 * - Motivation decay analysis
 */

interface Habit {
  id: string;
  name: string;
  emoji: string;
  frequency: 'daily' | 'weekly';
  targetPerDay: number;
  color: string;
  createdAt: string;
}

interface HabitLog {
  habitId: string;
  date: string; // YYYY-MM-DD
  completed: number;
  timestamp: string;
}

interface HabitStats {
  habitId: string;
  currentStreak: number;
  longestStreak: number;
  completionRate: number;
  totalCompletions: number;
}

const DEFAULT_HABITS: Habit[] = [
  { id: 'water', name: 'Pi ujë', emoji: '💧', frequency: 'daily', targetPerDay: 8, color: 'from-violet-400 to-violet-500', createdAt: '' },
  { id: 'sleep', name: '8 orë gjumë', emoji: '😴', frequency: 'daily', targetPerDay: 1, color: 'from-blue-600 to-purple-500', createdAt: '' },
  { id: 'exercise', name: 'Stërvitje', emoji: '🏃', frequency: 'daily', targetPerDay: 1, color: 'from-green-400 to-blue-800', createdAt: '' },
  { id: 'meditate', name: 'Meditim', emoji: '🧘', frequency: 'daily', targetPerDay: 1, color: 'from-purple-400 to-pink-500', createdAt: '' },
  { id: 'read', name: 'Lexim', emoji: '📚', frequency: 'daily', targetPerDay: 1, color: 'from-amber-400 to-orange-500', createdAt: '' },
  { id: 'walk', name: '10k hapa', emoji: '👟', frequency: 'daily', targetPerDay: 1, color: 'from-blue-700 to-green-500', createdAt: '' },
];

export default function DailyHabitsPage() {
  const [habits, setHabits] = useState<Habit[]>(DEFAULT_HABITS);
  const [logs, setLogs] = useState<HabitLog[]>([]);
  const [stats, setStats] = useState<Map<string, HabitStats>>(new Map());
  const [view, setView] = useState<'today' | 'week' | 'stats'>('today');
  const [showAddHabit, setShowAddHabit] = useState(false);
  const [newHabitName, setNewHabitName] = useState('');
  const [newHabitEmoji, setNewHabitEmoji] = useState('✨');

  const today = new Date().toISOString().split('T')[0];

  useEffect(() => {
    // Load from localStorage
    const storedHabits = localStorage.getItem('kloud_habits');
    const storedLogs = localStorage.getItem('kloud_habit_logs');
    
    if (storedHabits) setHabits(JSON.parse(storedHabits));
    if (storedLogs) {
      const parsed = JSON.parse(storedLogs);
      setLogs(parsed);
      calculateStats(parsed);
    }

    syncWithBackend();
  }, []);

  const syncWithBackend = async () => {
    try {
      await fetch('/api/behavioral/habits/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          habits,
          logs,
          deviceId: getDeviceId(),
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        })
      });
    } catch (e) {
      // Offline mode
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

  const calculateStats = (logData: HabitLog[]) => {
    const newStats = new Map<string, HabitStats>();
    
    habits.forEach(habit => {
      const habitLogs = logData.filter(l => l.habitId === habit.id);
      const dates = [...new Set(habitLogs.map(l => l.date))].sort().reverse();
      
      // Calculate streak
      let streak = 0;
      for (let i = 0; i < 365; i++) {
        const checkDate = new Date();
        checkDate.setDate(checkDate.getDate() - i);
        const dateStr = checkDate.toISOString().split('T')[0];
        const dayLog = habitLogs.find(l => l.date === dateStr);
        if (dayLog && dayLog.completed >= habit.targetPerDay) {
          streak++;
        } else if (i > 0) break; // Allow today to be incomplete
      }

      // Longest streak
      let longest = 0;
      let currentRun = 0;
      dates.forEach((date, i) => {
        const log = habitLogs.find(l => l.date === date);
        if (log && log.completed >= habit.targetPerDay) {
          currentRun++;
          longest = Math.max(longest, currentRun);
        } else {
          currentRun = 0;
        }
      });

      // Completion rate (last 30 days)
      const last30 = [];
      for (let i = 0; i < 30; i++) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dateStr = d.toISOString().split('T')[0];
        const log = habitLogs.find(l => l.date === dateStr);
        if (log && log.completed >= habit.targetPerDay) {
          last30.push(1);
        } else {
          last30.push(0);
        }
      }
      const rate = last30.reduce((a, b) => a + b, 0) / 30;

      newStats.set(habit.id, {
        habitId: habit.id,
        currentStreak: streak,
        longestStreak: longest,
        completionRate: rate,
        totalCompletions: habitLogs.reduce((sum, l) => sum + l.completed, 0)
      });
    });

    setStats(newStats);
  };

  const toggleHabit = async (habitId: string) => {
    const habit = habits.find(h => h.id === habitId);
    if (!habit) return;

    const existingLog = logs.find(l => l.habitId === habitId && l.date === today);
    let newLogs: HabitLog[];

    if (existingLog) {
      // Increment or reset
      const newCompleted = existingLog.completed >= habit.targetPerDay ? 0 : existingLog.completed + 1;
      newLogs = logs.map(l => 
        l.habitId === habitId && l.date === today 
          ? { ...l, completed: newCompleted, timestamp: new Date().toISOString() }
          : l
      );
    } else {
      // New log
      newLogs = [...logs, {
        habitId,
        date: today,
        completed: 1,
        timestamp: new Date().toISOString()
      }];
    }

    setLogs(newLogs);
    localStorage.setItem('kloud_habit_logs', JSON.stringify(newLogs));
    calculateStats(newLogs);

    // Send to backend
    try {
      await fetch('/api/behavioral/habits/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          habitId,
          date: today,
          action: existingLog ? 'increment' : 'start',
          deviceId: getDeviceId(),
          timestamp: new Date().toISOString()
        })
      });
    } catch (e) {}
  };

  const getLogForToday = (habitId: string): number => {
    const log = logs.find(l => l.habitId === habitId && l.date === today);
    return log?.completed || 0;
  };

  const getTotalProgress = (): number => {
    const total = habits.reduce((sum, h) => sum + h.targetPerDay, 0);
    const completed = habits.reduce((sum, h) => sum + Math.min(getLogForToday(h.id), h.targetPerDay), 0);
    return total > 0 ? (completed / total) * 100 : 0;
  };

  const addCustomHabit = () => {
    if (!newHabitName.trim()) return;
    
    const newHabit: Habit = {
      id: 'custom_' + Date.now(),
      name: newHabitName,
      emoji: newHabitEmoji,
      frequency: 'daily',
      targetPerDay: 1,
      color: 'from-gray-400 to-gray-500',
      createdAt: new Date().toISOString()
    };

    const newHabits = [...habits, newHabit];
    setHabits(newHabits);
    localStorage.setItem('kloud_habits', JSON.stringify(newHabits));
    setNewHabitName('');
    setShowAddHabit(false);
  };

  const getLast7Days = () => {
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      days.push({
        date: d.toISOString().split('T')[0],
        day: d.toLocaleDateString('sq-AL', { weekday: 'short' }),
        isToday: i === 0
      });
    }
    return days;
  };

  const EMOJI_OPTIONS = ['✨', '🎯', '💪', '🧠', '❤️', '🌟', '🔥', '💎', '🚀', '🌈', '☕', '🍎'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-black/20 backdrop-blur-lg border-b border-white/10">
        <div className="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-white/60 hover:text-white">
            ← Kthehu
          </Link>
          <h1 className="text-xl font-bold text-white">🎯 Daily Habits</h1>
          <button 
            onClick={() => setShowAddHabit(true)}
            className="w-8 h-8 bg-blue-800 rounded-full flex items-center justify-center text-white font-bold"
          >
            +
          </button>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-lg mx-auto px-4 pt-4">
        <div className="flex bg-white/10 rounded-2xl p-1">
          {[
            { id: 'today', label: '📅 Sot' },
            { id: 'week', label: '📊 Java' },
            { id: 'stats', label: '🏆 Stats' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setView(tab.id as 'today' | 'week' | 'stats')}
              className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all ${
                view === tab.id 
                  ? 'bg-white text-emerald-900' 
                  : 'text-white/70 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <main className="max-w-lg mx-auto px-4 py-6">
        {/* Add Habit Modal */}
        {showAddHabit && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-slate-800 rounded-3xl p-6 w-full max-w-sm">
              <h3 className="text-xl font-bold text-white mb-4">➕ Habit i ri</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="text-white/60 text-sm">Emoji</label>
                  <div className="grid grid-cols-6 gap-2 mt-2">
                    {EMOJI_OPTIONS.map(e => (
                      <button
                        key={e}
                        onClick={() => setNewHabitEmoji(e)}
                        className={`p-2 rounded-xl text-2xl ${newHabitEmoji === e ? 'bg-blue-800' : 'bg-white/10'}`}
                      >
                        {e}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-white/60 text-sm">Emri</label>
                  <input
                    type="text"
                    value={newHabitName}
                    onChange={(e) => setNewHabitName(e.target.value)}
                    placeholder="p.sh. Vitamina"
                    className="w-full mt-2 bg-white/10 border border-white/20 rounded-xl p-3 text-white placeholder-white/40 focus:outline-none focus:border-blue-800"
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => setShowAddHabit(false)}
                    className="flex-1 py-3 bg-white/10 rounded-xl text-white"
                  >
                    Anulo
                  </button>
                  <button
                    onClick={addCustomHabit}
                    className="flex-1 py-3 bg-blue-800 rounded-xl text-white font-bold"
                  >
                    Shto
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TODAY VIEW */}
        {view === 'today' && (
          <div className="space-y-6">
            {/* Progress Ring */}
            <div className="flex justify-center py-4">
              <div className="relative w-32 h-32">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="64" cy="64" r="56"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="12"
                    fill="none"
                  />
                  <circle
                    cx="64" cy="64" r="56"
                    stroke="url(#progressGradient)"
                    strokeWidth="12"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={`${getTotalProgress() * 3.52} 352`}
                  />
                  <defs>
                    <linearGradient id="progressGradient">
                      <stop offset="0%" stopColor="#10b981" />
                      <stop offset="100%" stopColor="#06b6d4" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold text-white">{Math.round(getTotalProgress())}%</span>
                  <span className="text-white/60 text-xs">kompletuar</span>
                </div>
              </div>
            </div>

            {/* Date */}
            <p className="text-center text-white/60">
              {new Date().toLocaleDateString('sq-AL', { weekday: 'long', day: 'numeric', month: 'long' })}
            </p>

            {/* Habits Grid */}
            <div className="grid grid-cols-2 gap-3">
              {habits.map(habit => {
                const completed = getLogForToday(habit.id);
                const isComplete = completed >= habit.targetPerDay;
                const stat = stats.get(habit.id);
                
                return (
                  <button
                    key={habit.id}
                    onClick={() => toggleHabit(habit.id)}
                    className={`p-4 rounded-2xl transition-all transform active:scale-95 ${
                      isComplete 
                        ? `bg-gradient-to-br ${habit.color} shadow-lg` 
                        : 'bg-white/10 hover:bg-white/15'
                    }`}
                  >
                    <div className="flex flex-col items-center gap-2">
                      <span className="text-4xl">{habit.emoji}</span>
                      <span className={`font-medium ${isComplete ? 'text-white' : 'text-white/80'}`}>
                        {habit.name}
                      </span>
                      
                      {habit.targetPerDay > 1 ? (
                        <div className="flex gap-1">
                          {Array.from({ length: habit.targetPerDay }).map((_, i) => (
                            <div
                              key={i}
                              className={`w-2 h-2 rounded-full ${
                                i < completed ? 'bg-white' : 'bg-white/30'
                              }`}
                            />
                          ))}
                        </div>
                      ) : (
                        <span className={`text-xs ${isComplete ? 'text-white/80' : 'text-white/50'}`}>
                          {isComplete ? '✓ Bërë!' : 'Tap për të shënuar'}
                        </span>
                      )}

                      {stat && stat.currentStreak > 0 && (
                        <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">
                          🔥 {stat.currentStreak} ditë
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* WEEK VIEW */}
        {view === 'week' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-white">📊 Java jote</h2>
            
            {/* Week Grid */}
            <div className="bg-white/10 rounded-2xl p-4">
              <div className="grid grid-cols-8 gap-1 text-center text-xs text-white/60 mb-2">
                <div></div>
                {getLast7Days().map(d => (
                  <div key={d.date} className={d.isToday ? 'text-blue-700 font-bold' : ''}>
                    {d.day}
                  </div>
                ))}
              </div>

              {habits.map(habit => (
                <div key={habit.id} className="grid grid-cols-8 gap-1 items-center py-2 border-t border-white/10">
                  <span className="text-xl">{habit.emoji}</span>
                  {getLast7Days().map(d => {
                    const log = logs.find(l => l.habitId === habit.id && l.date === d.date);
                    const isComplete = log && log.completed >= habit.targetPerDay;
                    return (
                      <div 
                        key={d.date}
                        className={`w-6 h-6 mx-auto rounded-full ${
                          isComplete 
                            ? 'bg-blue-800' 
                            : log?.completed 
                            ? 'bg-yellow-500/50'
                            : 'bg-white/10'
                        }`}
                      >
                        {isComplete && <span className="flex items-center justify-center h-full text-xs">✓</span>}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>

            {/* Week Summary */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white/10 rounded-2xl p-4 text-center">
                <p className="text-3xl">🎯</p>
                <p className="text-2xl font-bold text-white">
                  {habits.reduce((sum, h) => {
                    const weekLogs = logs.filter(l => l.habitId === h.id && getLast7Days().some(d => d.date === l.date));
                    return sum + weekLogs.filter(l => l.completed >= h.targetPerDay).length;
                  }, 0)}
                </p>
                <p className="text-xs text-white/60">kompletuar këtë javë</p>
              </div>
              <div className="bg-white/10 rounded-2xl p-4 text-center">
                <p className="text-3xl">📈</p>
                <p className="text-2xl font-bold text-white">
                  {Math.round(
                    (habits.reduce((sum, h) => {
                      const weekLogs = logs.filter(l => l.habitId === h.id && getLast7Days().some(d => d.date === l.date));
                      return sum + weekLogs.filter(l => l.completed >= h.targetPerDay).length;
                    }, 0) / (habits.length * 7)) * 100
                  )}%
                </p>
                <p className="text-xs text-white/60">sukses i javës</p>
              </div>
            </div>
          </div>
        )}

        {/* STATS VIEW */}
        {view === 'stats' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-white">🏆 Statistikat</h2>

            {/* Overall Stats */}
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-500/30 rounded-2xl p-4 text-center">
                <p className="text-3xl">🔥</p>
                <p className="text-2xl font-bold text-white">
                  {Math.max(...Array.from(stats.values()).map(s => s.currentStreak), 0)}
                </p>
                <p className="text-xs text-white/60">best streak</p>
              </div>
              <div className="bg-gradient-to-br from-blue-800/20 to-green-500/20 border border-blue-800/30 rounded-2xl p-4 text-center">
                <p className="text-3xl">✅</p>
                <p className="text-2xl font-bold text-white">
                  {Array.from(stats.values()).reduce((sum, s) => sum + s.totalCompletions, 0)}
                </p>
                <p className="text-xs text-white/60">total</p>
              </div>
              <div className="bg-gradient-to-br from-violet-500/20 to-violet-500/20 border border-violet-500/30 rounded-2xl p-4 text-center">
                <p className="text-3xl">📊</p>
                <p className="text-2xl font-bold text-white">
                  {Math.round(
                    Array.from(stats.values()).reduce((sum, s) => sum + s.completionRate, 0) / 
                    Math.max(stats.size, 1) * 100
                  )}%
                </p>
                <p className="text-xs text-white/60">mesatare</p>
              </div>
            </div>

            {/* Per-Habit Stats */}
            <div className="space-y-3">
              {habits.map(habit => {
                const stat = stats.get(habit.id);
                if (!stat) return null;

                return (
                  <div key={habit.id} className="bg-white/10 rounded-2xl p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-3xl">{habit.emoji}</span>
                      <div className="flex-1">
                        <p className="text-white font-medium">{habit.name}</p>
                        <p className="text-white/60 text-sm">
                          {stat.currentStreak > 0 ? `🔥 ${stat.currentStreak} ditë streak` : 'Fillo sot!'}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-white">{Math.round(stat.completionRate * 100)}%</p>
                        <p className="text-xs text-white/60">30 ditë</p>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                      <div 
                        className={`h-full bg-gradient-to-r ${habit.color} transition-all`}
                        style={{ width: `${stat.completionRate * 100}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* AI Insight */}
            <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-2xl p-6">
              <div className="flex items-start gap-3">
                <span className="text-3xl">🤖</span>
                <div>
                  <p className="text-white font-bold">Insight nga AI</p>
                  <p className="text-white/80 text-sm mt-2">
                    {Array.from(stats.values()).some(s => s.currentStreak >= 7)
                      ? 'Bravo! Ke të paktën një habit me streak 7+ ditë. Kjo tregon disiplinë të lartë.'
                      : Array.from(stats.values()).some(s => s.currentStreak >= 3)
                      ? 'Po ecën mirë! Vazhdo kështu për të arritur streakun 7-ditor.'
                      : 'Fillo me 1 habit të vetëm dhe fokusohu të krijosh streak. Konsistenca > Sasia.'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <div className="h-20"></div>
    </div>
  );
}








