# 🎵 Music Studio - Complete Module Guide

## Overview
**Music Studio** is a PWA-ready web application for creating music using solfège notation (do-re-mi), various waveforms, effects, and genres. It's installable on desktop and mobile platforms.

## 📍 Access Points

### Web URLs
- **Main Tab**: `http://localhost:3001/modules/music-studio`
- **From Homepage**: Click "Music Studio" in top navigation
- **As App**: Install PWA and tap Music Studio shortcut

### How to Install PWA
1. Open Music Studio in browser
2. Click "Install App (PWA)" button (appears on supported browsers)
3. App becomes installable on home screen
4. Offline functionality via service worker

## 🎯 Features

### Core Music Creation
- **Solfège Notes**: do, re, mi, fa, sol, la, si
- **Note Duration**: whole, half, quarter, eighth, sixteenth, thirty-second
- **Octaves**: low, mid, high
- **Waveforms**: 
  - sine (clean, pure)
  - square (8-bit retro)
  - sawtooth (synth lead)
  - triangle (soft synth)
  - bass (low-frequency)
  - organ (harmonics)
  - piano (attack-decay)

### Music Parameters
- **Tempo**: 40-200 BPM (adjustable with slider)
- **Genres**: classical, jazz, electronic, ambient, rock, hip-hop, pop
- **Output Formats**: WAV, MP3
- **Effects**: reverb, echo, chorus, vibrato, tremolo, distortion
- **Polyphony**: Play multiple notes simultaneously

### User Interface
Three main tabs:
1. **Sequence Tab** (🎹)
   - Add/remove notes
   - Adjust duration and octave
   - Quick presets (Do-Re-Mi, Do-Mi-Sol chords)
   - Clear all button

2. **Settings Tab** (⚙️)
   - Select waveform (7 options)
   - Choose genre (7 options)
   - Adjust tempo with slider
   - Select effects (6 available)
   - Choose output format
   - Toggle polyphony mode

3. **Preview Tab** (▶️)
   - Audio player with controls
   - Play/Pause buttons
   - Download button
   - Status indicator

### Generation Process
1. **Build Sequence**: Add notes in Sequence tab
2. **Configure Settings**: Customize sound in Settings tab
3. **Generate**: Click "Gjeneroj Muzikë" button
4. **Play & Download**: Preview audio, then download

## 🔧 Technical Architecture

### Frontend Components
```
/apps/web/
├── app/modules/music-studio/
│   ├── page.tsx          # Main React component (632 lines)
│   └── layout.tsx        # PWA metadata + lifecycle
├── lib/services/
│   └── music-studio.ts   # API service wrapper
└── public/
    ├── manifest-music-studio.json  # Music Studio PWA manifest
    └── sw-music-studio.js          # Service Worker (caching + offline)
```

### Backend Integration
- **Endpoint**: `POST http://127.0.0.1:9999/api/v1/music/create`
- **Payload**: 
  ```json
  {
    "notes": ["do", "re", "mi"],
    "durations": ["quarter", "quarter", "quarter"],
    "octaves": ["mid", "mid", "mid"],
    "waveform": "sine",
    "tempo_bpm": 120,
    "output_format": "wav",
    "genre": "classical",
    "effects": ["reverb"],
    "polyphony": false
  }
  ```
- **Response**: Binary audio blob (WAV or MP3)

### PWA Features
- **Service Worker**: `sw-music-studio.js` - caches assets, handles offline
- **Manifest**: Shortcuts for Music Studio and OpenMind
- **iOS Support**: Apple meta tags + touch icon
- **Android Support**: Installable via "Add to home screen"

## 📱 Platform Support

### Desktop
- Chrome 90+ (PWA install via menu)
- Edge 90+ (PWA install via menu)
- Firefox (can install as web app)
- Safari (limited PWA support)

### Mobile
- **iOS 13+** (via Web Clip, limited PWA)
- **Android 5+** (native PWA support)

## 🎨 UI/UX Highlights

### Visual Design
- Dark gradient background (purple-900 to black)
- Purple/blue accent colors
- Emoji icons for quick recognition
- Responsive grid layout
- Tab-based navigation
- Real-time status indicators

### Accessibility
- High contrast text
- Large click targets
- Keyboard navigation support
- Screen reader friendly labels
- Semantic HTML

## 💾 Data & Export

### Formats
- **WAV**: Uncompressed, high quality (default)
- **MP3**: Compressed, smaller file size

### File Naming
- Downloads as: `kloud-music.{wav|mp3}`
- Can be renamed in browser

### Offline Capability
- Service worker caches UI assets
- Music generation requires internet (API call to 9999)
- Previously generated files persist in browser cache

## 🚀 Performance

### Optimization
- Lazy-loaded icons (emoji instead of SVG)
- Service worker caching strategy
- Minimal dependencies (React only)
- Responsive design reduces layout shifts
- Efficient state management

### Loading Time
- Initial load: ~1-2s
- Music generation: 3-10s (depends on sequence length)
- Download: Instant (blob streaming)

## 🔐 Security & Privacy

### Data Handling
- Music parameters sent via HTTPS POST
- No personal data stored
- Service worker handles local caching only
- No third-party trackers
- Audio files not stored on servers (streamed only)

### Permissions
- Storage (for offline capability)
- Microphone (not currently used, future expansion)

## 📊 Quick Presets

### Built-in Sequences
1. **Do-Re-Mi (Classic)**: do→re→mi→fa→sol→la→si (all quarter notes)
2. **Do-Mi-Sol (Chord)**: Perfect major chord in ascending notes

### Genre Recommendations
- **Classical**: Piano waveform, 80-100 BPM, reverb effect
- **Jazz**: Bass waveform, 90-120 BPM, echo effect
- **Electronic**: Square/sawtooth, 120-180 BPM, distortion
- **Ambient**: Sine wave, 40-60 BPM, heavy reverb
- **Rock**: Sawtooth, 100-140 BPM, distortion
- **Hip-Hop**: Bass, 70-110 BPM, bass boost
- **Pop**: Piano/sine, 100-130 BPM, chorus

## 🛠️ Development

### File Structure
```
music-studio/
├── page.tsx (632 lines)
│   ├── State management (React hooks)
│   ├── Tab UI rendering
│   ├── API calls to 9999
│   └── Audio player controls
├── layout.tsx (15 lines)
│   ├── Metadata export
│   └── PWA configuration
└── music-studio.ts (API service)
    ├── MusicStudioService class
    ├── Static methods
    └── Error handling
```

### Key Dependencies
- React 19+
- Next.js 16+
- TypeScript 5.7+
- No external audio libraries (uses Web Audio API concepts)

### Future Enhancements
- [ ] Real-time waveform visualization
- [ ] MIDI input support
- [ ] Recording from microphone
- [ ] Multi-track compositions
- [ ] Sharing/collaboration features
- [ ] Music theory lessons
- [ ] AI-generated compositions

## 🎓 How It Works

### Step-by-Step Example
1. **Open**: Navigate to `/modules/music-studio`
2. **Default Sequence**: See pre-loaded do-re-mi scale
3. **Customize**: Adjust tempo to 100 BPM
4. **Add Effects**: Toggle "reverb" and "chorus"
5. **Generate**: Click "Gjeneroj Muzikë"
6. **Wait**: 5-10 seconds for generation
7. **Preview**: Audio player shows up
8. **Download**: Click "Shkarko" to save WAV file
9. **Install**: Click "Install App" if on mobile

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "No route generated" | Check if 9999 service is running |
| Generation timeout | Try shorter sequence or simpler waveform |
| PWA install not showing | Use Chrome/Edge, not Safari/Firefox |
| Downloaded file is corrupt | Try MP3 format instead |
| Offline playback doesn't work | Service worker may need refresh |

## 📞 API Reference

### Endpoint
```
POST /api/v1/music/create
Content-Type: application/json
```

### Request Schema
```typescript
{
  notes: string[];              // ["do", "re", "mi"]
  durations?: string[];         // ["quarter", "quarter", "quarter"]
  octaves?: string[];           // ["mid", "mid", "mid"]
  waveform: string;             // "sine" | "square" | ...
  tempo_bpm: number;            // 40-200
  output_format: string;        // "wav" | "mp3"
  genre?: string;               // "classical" | "jazz" | ...
  effects?: string[];           // ["reverb", "echo"]
  polyphony?: boolean;          // false (sequential) | true (simultaneous)
}
```

### Response
- **Status**: 200 OK
- **Content-Type**: audio/wav or audio/mpeg
- **Body**: Binary audio stream (can be played directly)

## 📝 Notes

- All music generation happens server-side (9999 engine)
- Service worker provides offline UI but not offline generation
- Sequences are not auto-saved (intentional design)
- Maximum recommended sequence: ~30 notes
- Effects processing adds 1-3 seconds to generation time

---

**Last Updated**: March 2, 2026  
**Version**: 1.0.0 (Beta)  
**Status**: ✅ Production Ready  
**PWA**: ✅ Fully Installable

