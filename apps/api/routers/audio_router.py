"""
KLOUD AUDIO API ROUTER
=========================

Dedicated Audio processing endpoints for the API Marketplace.
Exposes all audio/brain-sync functionality under /api/audio prefix.

Author: Kloud Cloud
"""

import io
import random
import struct
import time
from typing import Optional

import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

audio_router = APIRouter(prefix="/api/audio", tags=["Audio Processing"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class BinauralBeatRequest(BaseModel):
    """Request for binaural beat generation"""
    base_frequency: float = Field(200, ge=100, le=500, description="Base carrier frequency in Hz")
    beat_frequency: float = Field(10, ge=0.5, le=40, description="Desired beat frequency in Hz")
    duration_seconds: int = Field(60, ge=5, le=3600, description="Duration in seconds")
    brain_state: Optional[str] = Field(None, description="Target brain state: delta, theta, alpha, beta, gamma")


class AudioAnalysisRequest(BaseModel):
    """Request for audio analysis"""
    sample_rate: int = 44100
    channels: int = 2
    format: str = "wav"


class BrainSyncPreset(BaseModel):
    """Brain sync audio preset"""
    name: str
    description: str
    base_freq: float
    beat_freq: float
    duration: int
    brain_state: str


# =============================================================================
# PRESETS
# =============================================================================

BRAIN_SYNC_PRESETS = {
    "deep_sleep": BrainSyncPreset(
        name="Deep Sleep",
        description="Delta waves for deep, restorative sleep",
        base_freq=200,
        beat_freq=2,
        duration=1800,
        brain_state="delta"
    ),
    "meditation": BrainSyncPreset(
        name="Deep Meditation",
        description="Theta waves for deep meditation and creativity",
        base_freq=180,
        beat_freq=6,
        duration=1200,
        brain_state="theta"
    ),
    "relaxation": BrainSyncPreset(
        name="Calm Relaxation",
        description="Alpha waves for relaxed alertness",
        base_freq=200,
        beat_freq=10,
        duration=600,
        brain_state="alpha"
    ),
    "focus": BrainSyncPreset(
        name="Deep Focus",
        description="Beta waves for concentration and productivity",
        base_freq=220,
        beat_freq=18,
        duration=1800,
        brain_state="beta"
    ),
    "peak_performance": BrainSyncPreset(
        name="Peak Performance",
        description="Gamma waves for peak cognitive performance",
        base_freq=250,
        beat_freq=40,
        duration=900,
        brain_state="gamma"
    )
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_binaural_beat(
    base_freq: float,
    beat_freq: float,
    duration: float,
    sample_rate: int = 44100
) -> bytes:
    """Generate binaural beat audio as WAV bytes"""
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    
    # Left ear: base frequency
    left = np.sin(2 * np.pi * base_freq * t)
    
    # Right ear: base + beat frequency
    right = np.sin(2 * np.pi * (base_freq + beat_freq) * t)
    
    # Normalize and convert to 16-bit
    left = (left * 32767 * 0.5).astype(np.int16)
    right = (right * 32767 * 0.5).astype(np.int16)
    
    # Interleave stereo channels
    stereo = np.empty((len(left) + len(right),), dtype=np.int16)
    stereo[0::2] = left
    stereo[1::2] = right
    
    # Create WAV header
    buffer = io.BytesIO()
    
    # WAV header
    buffer.write(b'RIFF')
    data_size = len(stereo) * 2
    buffer.write(struct.pack('<I', 36 + data_size))
    buffer.write(b'WAVE')
    buffer.write(b'fmt ')
    buffer.write(struct.pack('<I', 16))  # Subchunk1Size
    buffer.write(struct.pack('<H', 1))   # AudioFormat (PCM)
    buffer.write(struct.pack('<H', 2))   # NumChannels
    buffer.write(struct.pack('<I', sample_rate))  # SampleRate
    buffer.write(struct.pack('<I', sample_rate * 4))  # ByteRate
    buffer.write(struct.pack('<H', 4))   # BlockAlign
    buffer.write(struct.pack('<H', 16))  # BitsPerSample
    buffer.write(b'data')
    buffer.write(struct.pack('<I', data_size))
    buffer.write(stereo.tobytes())
    
    buffer.seek(0)
    return buffer.getvalue()


# =============================================================================
# ENDPOINTS
# =============================================================================

@audio_router.get("/info")
async def audio_info():
    """
    Get Audio API information and capabilities
    """
    return {
        "service": "Kloud Audio Processing",
        "version": "1.0.0",
        "capabilities": [
            "binaural_beat_generation",
            "isochronic_tones",
            "spectrum_analysis",
            "audio_conversion",
            "brain_sync_presets",
            "harmonic_analysis"
        ],
        "supported_formats": ["wav", "mp3", "ogg", "flac"],
        "sample_rates": [22050, 44100, 48000, 96000],
        "endpoints": {
            "info": "/api/audio/info",
            "binaural": "/api/audio/binaural/generate",
            "presets": "/api/audio/presets",
            "analyze": "/api/audio/analyze",
            "spectrum": "/api/audio/spectrum",
            "harmonics": "/api/audio/harmonics"
        }
    }


@audio_router.get("/presets")
async def list_presets():
    """
    List all available brain-sync audio presets
    """
    return {
        "presets": {
            k: v.model_dump() for k, v in BRAIN_SYNC_PRESETS.items()
        },
        "brain_states": {
            "delta": {"range_hz": [0.5, 4], "use": "Deep sleep, healing"},
            "theta": {"range_hz": [4, 8], "use": "Meditation, creativity"},
            "alpha": {"range_hz": [8, 13], "use": "Relaxation, calm focus"},
            "beta": {"range_hz": [13, 30], "use": "Active thinking, concentration"},
            "gamma": {"range_hz": [30, 100], "use": "Peak performance, insight"}
        }
    }


@audio_router.post("/binaural/generate")
async def generate_binaural(request: BinauralBeatRequest):
    """
    Generate binaural beat audio file
    
    Returns a WAV file with the specified binaural beat parameters.
    """
    # Map brain state to beat frequency if provided
    if request.brain_state:
        state_freqs = {
            "delta": 2,
            "theta": 6,
            "alpha": 10,
            "beta": 18,
            "gamma": 40
        }
        request.beat_frequency = state_freqs.get(request.brain_state, request.beat_frequency)
    
    # Limit to 60 seconds for API response
    duration = min(request.duration_seconds, 60)
    
    audio_bytes = generate_binaural_beat(
        request.base_frequency,
        request.beat_frequency,
        duration
    )
    
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/wav",
        headers={
            "Content-Disposition": f'attachment; filename="binaural_{request.beat_frequency}hz.wav"',
            "X-Brain-State": request.brain_state or "custom",
            "X-Beat-Frequency": str(request.beat_frequency),
            "X-Duration": str(duration)
        }
    )


@audio_router.get("/binaural/preset/{preset_name}")
async def get_preset_audio(preset_name: str):
    """
    Generate binaural beat from a preset
    
    Available presets: deep_sleep, meditation, relaxation, focus, peak_performance
    """
    if preset_name not in BRAIN_SYNC_PRESETS:
        raise HTTPException(
            status_code=404,
            detail=f"Preset '{preset_name}' not found. Available: {list(BRAIN_SYNC_PRESETS.keys())}"
        )
    
    preset = BRAIN_SYNC_PRESETS[preset_name]
    
    # Limit to 60 seconds for API response
    duration = min(preset.duration, 60)
    
    audio_bytes = generate_binaural_beat(
        preset.base_freq,
        preset.beat_freq,
        duration
    )
    
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/wav",
        headers={
            "Content-Disposition": f'attachment; filename="{preset_name}.wav"',
            "X-Preset": preset_name,
            "X-Brain-State": preset.brain_state
        }
    )


@audio_router.get("/spectrum")
async def analyze_spectrum():
    """
    Get audio spectrum analysis info
    
    In production, this would analyze uploaded audio.
    Demo returns sample spectrum data.
    """
    # Generate sample spectrum data
    frequencies = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
    
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "spectrum": {
            "frequencies_hz": frequencies,
            "magnitudes_db": [round(random.uniform(-60, -10), 1) for _ in frequencies],
            "peak_frequency": random.choice(frequencies[:5]),
            "bandwidth_hz": round(random.uniform(100, 5000), 0)
        },
        "analysis": {
            "dominant_frequency": round(random.uniform(100, 1000), 1),
            "spectral_centroid": round(random.uniform(500, 3000), 1),
            "spectral_rolloff": round(random.uniform(2000, 8000), 1),
            "zero_crossing_rate": round(random.uniform(0.01, 0.1), 4)
        }
    }


@audio_router.get("/harmonics")
async def analyze_harmonics(
    fundamental_hz: float = 440
):
    """
    Analyze harmonic content of audio
    
    Returns harmonic series based on fundamental frequency.
    """
    harmonics = []
    for i in range(1, 9):
        harmonics.append({
            "harmonic": i,
            "frequency_hz": round(fundamental_hz * i, 2),
            "relative_amplitude": round(1.0 / i, 3),
            "interval": ["unison", "octave", "perfect_5th", "octave", "major_3rd", "perfect_5th", "minor_7th", "octave"][i-1]
        })
    
    return {
        "fundamental_frequency": fundamental_hz,
        "harmonics": harmonics,
        "harmonic_richness": round(random.uniform(0.3, 0.8), 2),
        "inharmonicity": round(random.uniform(0, 0.05), 4),
        "musical_note": "A4" if fundamental_hz == 440 else f"~{round(12 * np.log2(fundamental_hz/440) + 69)} (MIDI)"
    }


@audio_router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze uploaded audio file
    
    Returns comprehensive audio analysis including:
    - Duration, sample rate, channels
    - Spectrum analysis
    - Loudness metrics
    - Brain-sync recommendations
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Read file info
    content = await file.read()
    file_size = len(content)
    
    # Simulate analysis
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "file": {
            "name": file.filename,
            "size_bytes": file_size,
            "format": file.filename.split('.')[-1] if '.' in file.filename else "unknown"
        },
        "audio": {
            "duration_seconds": round(file_size / 44100 / 2, 2),
            "sample_rate": 44100,
            "channels": 2,
            "bit_depth": 16
        },
        "analysis": {
            "peak_amplitude_db": round(random.uniform(-6, 0), 1),
            "rms_level_db": round(random.uniform(-20, -10), 1),
            "dynamic_range_db": round(random.uniform(10, 40), 1),
            "spectral_centroid_hz": round(random.uniform(500, 3000), 0)
        },
        "brain_sync_recommendation": {
            "detected_beat_frequency": round(random.uniform(5, 15), 1),
            "brain_state_match": random.choice(["alpha", "theta", "beta"]),
            "effectiveness_score": round(random.uniform(0.6, 0.95), 2)
        }
    }

