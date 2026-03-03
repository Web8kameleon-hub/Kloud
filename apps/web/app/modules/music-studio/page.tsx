'use client';

import React, { useState, useRef, useEffect } from 'react';

type Note = 'do' | 're' | 'mi' | 'fa' | 'sol' | 'la' | 'si';
type Duration = 'whole' | 'half' | 'quarter' | 'eighth' | 'sixteenth' | 'thirty-second';
type Octave = 'low' | 'mid' | 'high';
type Waveform = 'sine' | 'square' | 'sawtooth' | 'triangle' | 'bass' | 'organ' | 'piano';
type Genre = 'classical' | 'jazz' | 'electronic' | 'ambient' | 'rock' | 'hip-hop' | 'pop';
type Format = 'wav' | 'mp3';

interface NoteSequence {
  id: string;
  note: Note;
  duration: Duration;
  octave: Octave;
}

interface MusicSettings {
  waveform: Waveform;
  tempo: number;
  genre: Genre;
  format: Format;
  effects: string[];
  polyphony: boolean;
}

const NOTES: Note[] = ['do', 're', 'mi', 'fa', 'sol', 'la', 'si'];
const DURATIONS: Duration[] = ['whole', 'half', 'quarter', 'eighth', 'sixteenth', 'thirty-second'];
const OCTAVES: Octave[] = ['low', 'mid', 'high'];
const WAVEFORMS: Waveform[] = ['sine', 'square', 'sawtooth', 'triangle', 'bass', 'organ', 'piano'];
const GENRES: Genre[] = ['classical', 'jazz', 'electronic', 'ambient', 'rock', 'hip-hop', 'pop'];
const EFFECTS = ['reverb', 'echo', 'chorus', 'vibrato', 'tremolo', 'distortion'];

const DEFAULT_SEQUENCE: NoteSequence[] = [
  { id: '1', note: 'do', duration: 'quarter', octave: 'mid' },
  { id: '2', note: 're', duration: 'quarter', octave: 'mid' },
  { id: '3', note: 'mi', duration: 'quarter', octave: 'mid' },
  { id: '4', note: 'fa', duration: 'quarter', octave: 'mid' },
  { id: '5', note: 'sol', duration: 'quarter', octave: 'mid' },
  { id: '6', note: 'la', duration: 'quarter', octave: 'mid' },
  { id: '7', note: 'si', duration: 'quarter', octave: 'mid' },
];

export default function MusicStudio() {
  const [sequence, setSequence] = useState<NoteSequence[]>(DEFAULT_SEQUENCE);
  const [settings, setSettings] = useState<MusicSettings>({
    waveform: 'sine',
    tempo: 120,
    genre: 'classical',
    format: 'wav',
    effects: [],
    polyphony: false,
  });

  const [isPlaying, setIsPlaying] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedFile, setGeneratedFile] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'sequence' | 'settings' | 'preview'>('sequence');
  const [installPromptEvent, setInstallPromptEvent] = useState<any>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const handler = (event: any) => {
      event.preventDefault();
      setInstallPromptEvent(event);
    };

    window.addEventListener('beforeinstallprompt', handler as EventListener);
    return () => window.removeEventListener('beforeinstallprompt', handler as EventListener);
  }, []);

  const installPwa = async () => {
    if (!installPromptEvent) return;
    installPromptEvent.prompt();
    await installPromptEvent.userChoice;
    setInstallPromptEvent(null);
  };

  const aiGenerateMelody = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('http://127.0.0.1:9999/api/v1/music/ai-generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: 'Krijo një melodi hot hot, ritmike, me motiv lalalalaaaa la/la, stil modern.',
        }),
      });
      if (!response.ok) throw new Error('AI nuk mundi të krijojë melodi');
      const data = await response.json();
      if (data && data.sequence) {
        setSequence(data.sequence);
        setSettings((current) => ({
          ...current,
          waveform: data.waveform || current.waveform,
          genre: data.genre || current.genre,
        }));
        setActiveTab('sequence');
      } else {
        alert('AI nuk ktheu melodi!');
      }
    } catch {
      alert('Gabim nga AI!');
    } finally {
      setIsGenerating(false);
    }
  };

  // Add note to sequence
  const addNote = (note: Note = 'do', duration: Duration = 'quarter', octave: Octave = 'mid') => {
    setSequence([
      ...sequence,
      {
        id: Date.now().toString(),
        note,
        duration,
        octave,
      },
    ]);
  };

  // Remove note from sequence
  const removeNote = (id: string) => {
    setSequence(sequence.filter((n) => n.id !== id));
  };

  // Update note
  const updateNote = (id: string, field: keyof NoteSequence, value: any) => {
    setSequence(
      sequence.map((n) =>
        n.id === id ? { ...n, [field]: value } : n
      )
    );
  };

  // Toggle effect
  const toggleEffect = (effect: string) => {
    setSettings({
      ...settings,
      effects: settings.effects.includes(effect)
        ? settings.effects.filter((e) => e !== effect)
        : [...settings.effects, effect],
    });
  };

  // Generate music
  const generateMusic = async () => {
    if (sequence.length === 0) {
      alert('Shtoni të paktën një notë!');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await fetch('http://127.0.0.1:9999/api/v1/music/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          notes: sequence.map((s) => s.note),
          durations: sequence.map((s) => s.duration),
          octaves: sequence.map((s) => s.octave),
          waveform: settings.waveform,
          tempo_bpm: settings.tempo,
          output_format: settings.format,
          genre: settings.genre,
          effects: settings.effects,
          polyphony: settings.polyphony,
        }),
      });

      if (!response.ok) throw new Error('Failed to generate music');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setGeneratedFile(url);

      if (audioRef.current) {
        audioRef.current.src = url;
      }
    } catch (error) {
      console.error('Error generating music:', error);
      alert('Gabim në gjenerim të muzikës');
    } finally {
      setIsGenerating(false);
    }
  };

  // Download music
  const downloadMusic = () => {
    if (!generatedFile) return;

    const a = document.createElement('a');
    a.href = generatedFile;
    a.download = `clisonix-music.${settings.format}`;
    a.click();
  };

  // Clear sequence
  const clearSequence = () => {
    if (confirm('Fshij të gjithë sekuencën?')) {
      setSequence([]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-slate-900 to-black p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-3xl">🎼</span>
            <h1 className="text-4xl font-bold text-white">🎵 Music Studio</h1>
          </div>
          <p className="text-gray-300">Krijoni muzikë me notë solfezh, efekte dhe zhanre</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 bg-slate-800/50 p-1 rounded-lg w-fit">
          {(['sequence', 'settings', 'preview'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              {tab === 'sequence' && '🎹 Sekuenca'}
              {tab === 'settings' && '⚙️ Cilësimet'}
              {tab === 'preview' && '▶️ Paraparje'}
            </button>
          ))}
        </div>

        <div className="mb-6 flex items-center gap-3">
          <a
            href="/"
            className="px-3 py-2 rounded-md bg-slate-800 text-gray-200 hover:bg-slate-700 text-sm"
          >
            Home Tab
          </a>
          <a
            href="/modules/openmind"
            className="px-3 py-2 rounded-md bg-slate-800 text-gray-200 hover:bg-slate-700 text-sm"
          >
            OpenMind Tab
          </a>
          <span className="px-3 py-2 rounded-md bg-purple-600 text-white text-sm">Music Studio Tab</span>
          {installPromptEvent && (
            <button
              onClick={installPwa}
              className="ml-2 px-3 py-2 rounded-md bg-emerald-600 text-white hover:bg-emerald-700 text-sm"
            >
              Install App (PWA)
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Sequence Tab */}
            {activeTab === 'sequence' && (
              <div className="bg-slate-800/50 border border-purple-500/20 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <span>▶️</span>
                    Sekuenca e Notave
                  </h2>
                  <div className="flex gap-2">
                    <button
                      onClick={() => addNote()}
                      className="px-3 py-1 bg-purple-600 text-white rounded-md hover:bg-purple-700 flex items-center gap-2 text-sm"
                    >
                      <span>➕</span> Shto
                    </button>
                    <button
                      onClick={clearSequence}
                      className="px-3 py-1 bg-red-600/20 text-red-400 rounded-md hover:bg-red-600/40 flex items-center gap-2 text-sm"
                    >
                      <span>🗑️</span> Fshij
                    </button>
                  </div>
                </div>

                {/* Notes Grid */}
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {sequence.length === 0 ? (
                    <p className="text-gray-400 text-center py-8">Asnjë notë. Shtoni të paktën një!</p>
                  ) : (
                    sequence.map((noteItem, idx) => (
                      <div
                        key={noteItem.id}
                        className="bg-slate-700/50 border border-slate-600 rounded-lg p-4 flex items-center gap-3"
                      >
                        <span className="text-gray-400 font-mono font-bold">{idx + 1}</span>

                        {/* Note Select */}
                        <select
                          value={noteItem.note}
                          onChange={(e) => updateNote(noteItem.id, 'note', e.target.value)}
                          className="bg-slate-600 text-white px-2 py-1 rounded border border-slate-500 text-sm"
                        >
                          {NOTES.map((n) => (
                            <option key={n} value={n}>
                              {n.toUpperCase()}
                            </option>
                          ))}
                        </select>

                        {/* Duration Select */}
                        <select
                          value={noteItem.duration}
                          onChange={(e) => updateNote(noteItem.id, 'duration', e.target.value)}
                          className="bg-slate-600 text-white px-2 py-1 rounded border border-slate-500 text-sm"
                        >
                          {DURATIONS.map((d) => (
                            <option key={d} value={d}>
                              {d}
                            </option>
                          ))}
                        </select>

                        {/* Octave Select */}
                        <select
                          value={noteItem.octave}
                          onChange={(e) => updateNote(noteItem.id, 'octave', e.target.value)}
                          className="bg-slate-600 text-white px-2 py-1 rounded border border-slate-500 text-sm"
                        >
                          {OCTAVES.map((o) => (
                            <option key={o} value={o}>
                              {o}
                            </option>
                          ))}
                        </select>

                        {/* Remove Button */}
                        <button
                          onClick={() => removeNote(noteItem.id)}
                          className="ml-auto p-1 hover:bg-red-600/20 rounded text-red-400"
                        >
                          <span>🗑️</span>
                        </button>
                      </div>
                    ))
                  )}
                </div>

                {/* Quick Add Buttons */}
                <div className="mt-6 pt-4 border-t border-slate-600">
                  <p className="text-sm text-gray-400 mb-3">Shto një sekuencë të gatshme:</p>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => setSequence(DEFAULT_SEQUENCE)}
                      className="px-3 py-1 bg-blue-600/20 text-blue-400 rounded text-sm hover:bg-blue-600/40"
                    >
                      Do-Re-Mi (klasike)
                    </button>
                    <button
                      onClick={() =>
                        setSequence([
                          { id: '1', note: 'do', duration: 'quarter', octave: 'low' },
                          { id: '2', note: 'mi', duration: 'quarter', octave: 'low' },
                          { id: '3', note: 'sol', duration: 'quarter', octave: 'low' },
                          { id: '4', note: 'do', duration: 'half', octave: 'mid' },
                        ])
                      }
                      className="px-3 py-1 bg-green-600/20 text-green-400 rounded text-sm hover:bg-green-600/40"
                    >
                      Do-Mi-Sol (akordi)
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Settings Tab */}
            {activeTab === 'settings' && (
              <div className="bg-slate-800/50 border border-purple-500/20 rounded-lg p-6 space-y-6">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <span>⚙️</span>
                  Cilësimet e Gjenerimit
                </h2>

                {/* Waveform */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    <span className="mr-2">⚡</span>
                    Forma e Valës
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {WAVEFORMS.map((w) => (
                      <button
                        key={w}
                        onClick={() => setSettings({ ...settings, waveform: w })}
                        className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                          settings.waveform === w
                            ? 'bg-purple-600 text-white'
                            : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                        }`}
                      >
                        {w}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Genre */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    🎼 Zhanri
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {GENRES.map((g) => (
                      <button
                        key={g}
                        onClick={() => setSettings({ ...settings, genre: g })}
                        className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                          settings.genre === g
                            ? 'bg-purple-600 text-white'
                            : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                        }`}
                      >
                        {g}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Tempo */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    ⏱️ Tempo (BPM): {settings.tempo}
                  </label>
                  <input
                    type="range"
                    min="40"
                    max="200"
                    value={settings.tempo}
                    onChange={(e) =>
                      setSettings({ ...settings, tempo: parseInt(e.target.value) })
                    }
                    className="w-full accent-purple-600"
                  />
                </div>

                {/* Effects */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    ✨ Efekte Zanore
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {EFFECTS.map((effect) => (
                      <button
                        key={effect}
                        onClick={() => toggleEffect(effect)}
                        className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                          settings.effects.includes(effect)
                            ? 'bg-purple-600 text-white'
                            : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                        }`}
                      >
                        {effect}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Format */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    💾 Format Dalës
                  </label>
                  <div className="flex gap-2">
                    {(['wav', 'mp3'] as const).map((fmt) => (
                      <button
                        key={fmt}
                        onClick={() => setSettings({ ...settings, format: fmt })}
                        className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                          settings.format === fmt
                            ? 'bg-purple-600 text-white'
                            : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                        }`}
                      >
                        {fmt.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Polyphony */}
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.polyphony}
                      onChange={(e) =>
                        setSettings({ ...settings, polyphony: e.target.checked })
                      }
                      className="w-4 h-4 accent-purple-600"
                    />
                    <span className="text-sm font-medium text-gray-300">
                      🎵 Polifonija (luaj notat njëkohësisht)
                    </span>
                  </label>
                </div>
              </div>
            )}

            {/* Preview Tab */}
            {activeTab === 'preview' && (
              <div className="bg-slate-800/50 border border-purple-500/20 rounded-lg p-6">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <span>🔊</span>
                  Paraparje dhe Kontroll
                </h2>

                {generatedFile ? (
                  <div className="space-y-4">
                    <audio
                      ref={audioRef}
                      controls
                      className="w-full bg-slate-700 rounded-lg"
                      onPlay={() => setIsPlaying(true)}
                      onPause={() => setIsPlaying(false)}
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          if (audioRef.current?.paused) {
                            audioRef.current?.play();
                            setIsPlaying(true);
                          } else {
                            audioRef.current?.pause();
                            setIsPlaying(false);
                          }
                        }}
                        className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium flex items-center justify-center gap-2"
                      >
                        {isPlaying ? (
                          <>
                            <span>⏸️</span> Ndal
                          </>
                        ) : (
                          <>
                            <span>▶️</span> Luaj
                          </>
                        )}
                      </button>
                      <button
                        onClick={downloadMusic}
                        className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center justify-center gap-2"
                      >
                        <span>⬇️</span> Shkarko
                      </button>
                    </div>
                    <p className="text-sm text-gray-400">
                      Muzika juaj është gati për shkarkim në format {settings.format.toUpperCase()}!
                    </p>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-400 mb-4">Ende asnjë muzikë e gjeneruar</p>
                    <p className="text-sm text-gray-500">
                      Krijoni sekuencën dhe shtypni "Gjeneroj Muzikë" më poshtë
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Sidebar - Generation Controls */}
          <div className="space-y-4">
            {/* Info Card */}
            <div className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 border border-purple-500/20 rounded-lg p-4">
              <h3 className="font-bold text-white mb-2">📊 Statusi</h3>
              <div className="space-y-2 text-sm text-gray-300">
                <p>
                  <span className="text-gray-400">Notat:</span> <span className="font-mono">{sequence.length}</span>
                </p>
                <p>
                  <span className="text-gray-400">Vala:</span> <span className="font-mono">{settings.waveform}</span>
                </p>
                <p>
                  <span className="text-gray-400">Zhanri:</span> <span className="font-mono">{settings.genre}</span>
                </p>
                <p>
                  <span className="text-gray-400">Tempo:</span> <span className="font-mono">{settings.tempo} BPM</span>
                </p>
                <p>
                  <span className="text-gray-400">Efekte:</span>{' '}
                  <span className="font-mono">{settings.effects.length || 'asnjë'}</span>
                </p>
              </div>
            </div>


            {/* AI Generate Button */}
            <button
              onClick={aiGenerateMelody}
              disabled={isGenerating}
              className={`w-full py-3 mb-2 rounded-lg font-bold text-base flex items-center justify-center gap-2 transition-all ${
                isGenerating
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-pink-600 to-yellow-500 text-white hover:from-pink-700 hover:to-yellow-600 shadow-lg hover:shadow-xl'
              }`}
            >
              {isGenerating ? (
                <>
                  <div className="animate-spin">🤖</div>
                  AI po krijon...
                </>
              ) : (
                <>
                  <span>🎤</span>
                  AI Krijo Melodi Hot
                </>
              )}
            </button>

            {/* Generate Button */}
            <button
              onClick={generateMusic}
              disabled={isGenerating || sequence.length === 0}
              className={`w-full py-4 rounded-lg font-bold text-lg flex items-center justify-center gap-2 transition-all ${
                isGenerating || sequence.length === 0
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 shadow-lg hover:shadow-xl'
              }`}
            >
              {isGenerating ? (
                <>
                  <div className="animate-spin">⚙️</div>
                  Po gjeneroj...
                </>
              ) : (
                <>
                  <span>⚡</span>
                  Gjeneroj Muzikë
                </>
              )}
            </button>

            {/* Keyboard Quick Reference */}
            <div className="bg-slate-800/50 border border-slate-600 rounded-lg p-4">
              <h3 className="font-bold text-white mb-3 text-sm">🎹 Notat Solfezh</h3>
              <div className="grid grid-cols-2 gap-1 text-xs text-gray-400">
                {NOTES.map((note) => (
                  <div key={note} className="bg-slate-700/50 px-2 py-1 rounded">
                    <span className="font-mono">{note.toUpperCase()}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Help Card */}
            <div className="bg-slate-800/50 border border-slate-600 rounded-lg p-4 text-xs text-gray-400 space-y-2">
              <p className="font-bold text-white">💡 Këshillë</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Shtoni notat një nga një</li>
                <li>Zgjidhni formën e valës</li>
                <li>Cilësoni efektet zanore</li>
                <li>Shtypni "Gjeneroj"</li>
                <li>Shkarkoni skedarin tuaj</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
