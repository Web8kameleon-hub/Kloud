"""
Kloud Audio Synthesizer
Convert brain wave patterns into real-time audio synthesis with real audio output
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import math
from datetime import datetime
import logging
# Optional audio dependencies with fallbacks
try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    sd = None

import threading
import queue
import time

logger = logging.getLogger(__name__)


class AudioSynthesizer:
    """Convert EEG brain waves to audio synthesis with real-time audio output"""
    
    def __init__(self, sample_rate: int = 44100, real_audio: bool = True):
        self.sample_rate = sample_rate
        self.duration_buffer = 1.0  # 1 second audio buffer
        self.buffer_size = int(sample_rate * self.duration_buffer)
        self.real_audio = real_audio and SOUNDDEVICE_AVAILABLE
        
        # Audio streaming setup
        self.audio_queue = queue.Queue(maxsize=10)
        self.is_playing = False
        
        if not SOUNDDEVICE_AVAILABLE:
            logger.warning("[WARN] sounddevice not available - audio synthesis will work without real audio output")
        self.audio_thread = None
        
        # Musical scale frequencies (C major)
        self.musical_scale = {
            "C": 261.63,
            "D": 293.66,
            "E": 329.63,
            "F": 349.23,
            "G": 392.00,
            "A": 440.00,
            "B": 493.88
        }
        
        # Brain wave to frequency mapping
        self.brainwave_mapping = {
            "delta": {"base_freq": 60, "octave": 1},    # Deep bass
            "theta": {"base_freq": 120, "octave": 2},   # Low frequencies
            "alpha": {"base_freq": 240, "octave": 3},   # Mid frequencies
            "beta": {"base_freq": 480, "octave": 4},    # Higher frequencies
            "gamma": {"base_freq": 960, "octave": 5}    # High frequencies
        }
        
        # Initialize audio device if real audio is enabled
        if self.real_audio:
            try:
                self._initialize_audio_device()
                logger.info(f"ðŸ”Š Real Audio Synthesizer initialized with {sample_rate}Hz sample rate")
            except Exception as e:
                logger.warning(f"âš ï¸ Failed to initialize audio device: {e}, falling back to simulation mode")
                self.real_audio = False
        else:
            logger.info(f"ðŸŽµ Audio Synthesizer initialized in simulation mode with {sample_rate}Hz sample rate")
    
    def _initialize_audio_device(self):
        """Initialize audio device for real-time playback"""
        try:
            # Check available audio devices
            devices = sd.query_devices()
            logger.info(f"Available audio devices: {len(devices)}")
            
            # Get default output device
            default_device = sd.default.device[1]  # Output device
            logger.info(f"Using default output device: {default_device}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize audio device: {e}")
    
    def _audio_callback(self, outdata, frames, time, status):
        """Audio callback function for real-time streaming"""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        try:
            # Get audio data from queue (non-blocking)
            audio_chunk = self.audio_queue.get_nowait()
            
            # Ensure correct shape
            if len(audio_chunk.shape) == 1:
                audio_chunk = audio_chunk.reshape(-1, 1)  # Mono
            
            # Copy to output buffer
            outdata[:] = audio_chunk[:frames]
            
        except queue.Empty:
            # No audio data available, output silence
            outdata.fill(0)
    
    def start_audio_stream(self):
        """Start real-time audio streaming"""
        if not self.real_audio:
            logger.info("ðŸŽµ Audio streaming in simulation mode")
            return
        
        try:
            self.is_playing = True
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,  # Mono
                callback=self._audio_callback,
                blocksize=1024
            )
            self.stream.start()
            logger.info("ðŸ”Š Real-time audio streaming started")
            
        except Exception as e:
            logger.error(f"âŒ Failed to start audio stream: {e}")
            self.real_audio = False
    
    def stop_audio_stream(self):
        """Stop real-time audio streaming"""
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop()
            self.stream.close()
            self.is_playing = False
            logger.info("â¹ï¸ Audio streaming stopped")
    
    def play_audio_array(self, audio_data: np.ndarray):
        """Play audio data either through real device or simulation"""
        if self.real_audio and hasattr(self, 'stream') and self.stream.active:
            try:
                # Add to queue for real-time playback
                if not self.audio_queue.full():
                    self.audio_queue.put_nowait(audio_data)
                logger.debug(f"ðŸ”Š Playing {len(audio_data)} audio samples")
            except Exception as e:
                logger.error(f"âŒ Failed to queue audio data: {e}")
        else:
            # Simulation mode - just log
            duration = len(audio_data) / self.sample_rate
            logger.info(f"ðŸŽµ Simulated audio playback: {duration:.2f}s, {len(audio_data)} samples")
    
    def generate_sine_wave(self, frequency: float, duration: float, amplitude: float = 0.5) -> np.ndarray:
        """Generate a sine wave with given parameters"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        wave = amplitude * np.sin(2 * np.pi * frequency * t)
        return wave
    
    def generate_brain_tone(self, band_powers: Dict[str, float], duration: float = 1.0) -> np.ndarray:
        """Generate audio tone based on brain wave band powers"""
        if not band_powers:
            # Return silence
            return np.zeros(int(duration * self.sample_rate))
        
        # Normalize band powers
        total_power = sum(band_powers.values()) + 1e-6
        normalized_powers = {band: power/total_power for band, power in band_powers.items()}
        
        # Generate composite waveform
        composite_wave = np.zeros(int(duration * self.sample_rate))
        
        for band, power in normalized_powers.items():
            if power > 0.01:  # Only include significant bands
                mapping = self.brainwave_mapping.get(band, {"base_freq": 220, "octave": 3})
                frequency = mapping["base_freq"] * mapping["octave"]
                amplitude = min(power * 2.0, 0.8)  # Scale amplitude
                
                wave = self.generate_sine_wave(frequency, duration, amplitude)
                composite_wave += wave
        
        # Normalize to prevent clipping
        max_amplitude = np.max(np.abs(composite_wave))
        if max_amplitude > 1.0:
            composite_wave = composite_wave / max_amplitude * 0.9
        
        return composite_wave
    
    def generate_musical_sequence(self, cognitive_state: str, confidence: float) -> np.ndarray:
        """Generate musical sequence based on cognitive state"""
        note_duration = 0.25  # Quarter note
        
        # Map cognitive states to musical patterns
        musical_patterns = {
            "relaxed": ["C", "E", "G", "C"],
            "focused": ["C", "D", "E", "F", "G"],
            "meditative": ["A", "C", "E", "A"],
            "stressed": ["G", "F", "E", "D", "C"],
            "drowsy": ["C", "G", "C", "G"]
        }
        
        pattern = musical_patterns.get(cognitive_state, ["C", "E", "G"])
        sequence = np.array([])
        
        for note in pattern:
            frequency = self.musical_scale[note]
            amplitude = confidence * 0.6  # Scale by confidence
            wave = self.generate_sine_wave(frequency, note_duration, amplitude)
            sequence = np.concatenate([sequence, wave])
        
        return sequence
    
    def apply_envelope(self, audio: np.ndarray, attack: float = 0.1, decay: float = 0.1, 
                      sustain: float = 0.7, release: float = 0.2) -> np.ndarray:
        """Apply ADSR envelope to audio signal"""
        length = len(audio)
        envelope = np.ones(length)
        
        # Attack
        attack_samples = int(attack * length)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        decay_samples = int(decay * length)
        if decay_samples > 0:
            start_idx = attack_samples
            end_idx = start_idx + decay_samples
            envelope[start_idx:end_idx] = np.linspace(1, sustain, decay_samples)
        
        # Sustain (already set)
        sustain_start = attack_samples + decay_samples
        sustain_end = length - int(release * length)
        envelope[sustain_start:sustain_end] = sustain
        
        # Release
        release_samples = int(release * length)
        if release_samples > 0:
            envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)
        
        return audio * envelope
    
    def add_harmonics(self, base_audio: np.ndarray, harmonics: List[float] = [0.5, 0.25, 0.125]) -> np.ndarray:
        """Add harmonic content to base audio"""
        if len(base_audio) == 0:
            return base_audio
        
        enhanced_audio = base_audio.copy()
        
        # Add each harmonic
        for i, amplitude in enumerate(harmonics):
            harmonic_order = i + 2  # 2nd, 3rd, 4th harmonics
            
            # Create time array
            t = np.arange(len(base_audio)) / self.sample_rate
            
            # Estimate fundamental frequency (simplified)
            fft_data = np.fft.fft(base_audio)
            freqs = np.fft.fftfreq(len(base_audio), 1/self.sample_rate)
            fundamental_idx = np.argmax(np.abs(fft_data[1:len(fft_data)//2])) + 1
            fundamental_freq = abs(freqs[fundamental_idx])
            
            if fundamental_freq > 0:
                harmonic_freq = fundamental_freq * harmonic_order
                harmonic_wave = amplitude * np.sin(2 * np.pi * harmonic_freq * t)
                enhanced_audio += harmonic_wave
        
        # Normalize
        max_amplitude = np.max(np.abs(enhanced_audio))
        if max_amplitude > 1.0:
            enhanced_audio = enhanced_audio / max_amplitude * 0.9
        
        return enhanced_audio
    
    def synthesize_from_brain_data(self, brain_analysis: Dict) -> Dict[str, np.ndarray]:
        """Generate multiple audio streams from brain analysis data"""
        if brain_analysis.get("status") != "active":
            return {"silence": np.zeros(self.buffer_size)}
        
        audio_streams = {}
        
        # 1. Brain wave tone synthesis
        cognitive_state = brain_analysis.get("cognitive_state", {})
        band_powers = cognitive_state.get("band_powers", {})
        
        if band_powers:
            brain_tone = self.generate_brain_tone(band_powers, self.duration_buffer)
            brain_tone = self.apply_envelope(brain_tone)
            audio_streams["brain_waves"] = brain_tone
        
        # 2. Musical interpretation
        state = cognitive_state.get("state", "unknown")
        confidence = cognitive_state.get("confidence", 0.0)
        
        if state != "unknown":
            musical_seq = self.generate_musical_sequence(state, confidence)
            if len(musical_seq) < self.buffer_size:
                # Repeat sequence to fill buffer
                repeats = int(np.ceil(self.buffer_size / len(musical_seq)))
                musical_seq = np.tile(musical_seq, repeats)[:self.buffer_size]
            audio_streams["musical"] = musical_seq
        
        # 3. Hemisphere balance (stereo)
        brain_symmetry = brain_analysis.get("brain_symmetry", {})
        if brain_symmetry.get("symmetry_index") is not None:
            symmetry = brain_symmetry["symmetry_index"]
            
            # Create stereo balance based on hemisphere dominance
            base_tone = self.generate_sine_wave(220, self.duration_buffer, 0.3)
            left_channel = base_tone * (1.0 - symmetry)
            right_channel = base_tone * symmetry
            
            # Combine to stereo
            stereo_audio = np.column_stack([left_channel, right_channel])
            audio_streams["hemisphere_balance"] = stereo_audio
        
        return audio_streams
    
    def synthesize_and_play_realtime(self, brain_analysis: Dict) -> Dict:
        """Real-time synthesis and playback from brain data"""
        try:
            # Generate audio streams
            audio_streams = self.synthesize_from_brain_data(brain_analysis)
            
            if not audio_streams:
                return {"status": "no_audio", "message": "No audio generated"}
            
            # Mix all streams for playback
            mixed_audio = np.zeros(self.buffer_size)
            active_streams = []
            
            for stream_name, audio_data in audio_streams.items():
                if len(audio_data.shape) == 1:  # Mono audio
                    mixed_audio += audio_data[:self.buffer_size]
                    active_streams.append(stream_name)
                elif audio_data.shape[1] == 2:  # Stereo - convert to mono for mixing
                    mono_audio = np.mean(audio_data, axis=1)
                    mixed_audio += mono_audio[:self.buffer_size]
                    active_streams.append(f"{stream_name}_stereo")
            
            # Normalize mixed audio
            if np.max(np.abs(mixed_audio)) > 0:
                mixed_audio = mixed_audio / np.max(np.abs(mixed_audio)) * 0.8
            
            # Play the mixed audio
            self.play_audio_array(mixed_audio)
            
            return {
                "status": "playing",
                "active_streams": active_streams,
                "audio_duration": len(mixed_audio) / self.sample_rate,
                "synthesis_timestamp": datetime.now().isoformat(),
                "real_audio": self.real_audio
            }
            
        except Exception as e:
            logger.error(f"âŒ Error in real-time synthesis: {e}")
            return {"status": "error", "message": str(e)}
    
    def start_continuous_synthesis(self, brain_data_callback, update_interval: float = 0.5):
        """Start continuous synthesis loop with brain data callback"""
        if not callable(brain_data_callback):
            raise ValueError("brain_data_callback must be callable")
        
        self.start_audio_stream()
        
        def synthesis_loop():
            logger.info("ðŸŽµ Starting continuous brain-to-audio synthesis")
            
            while self.is_playing:
                try:
                    # Get fresh brain data
                    brain_data = brain_data_callback()
                    
                    if brain_data:
                        # Synthesize and play
                        result = self.synthesize_and_play_realtime(brain_data)
                        if result["status"] == "playing":
                            logger.debug(f"ðŸ”Š Playing: {result['active_streams']}")
                    
                    # Wait for next update
                    time.sleep(update_interval)
                    
                except Exception as e:
                    logger.error(f"âŒ Error in synthesis loop: {e}")
                    time.sleep(1.0)  # Error recovery delay
            
            logger.info("â¹ï¸ Continuous synthesis stopped")
        
        # Start synthesis in background thread
        self.audio_thread = threading.Thread(target=synthesis_loop, daemon=True)
        self.audio_thread.start()
        
        return {
            "status": "started",
            "update_interval": update_interval,
            "real_audio": self.real_audio
        }
    
    def stop_continuous_synthesis(self):
        """Stop continuous synthesis and audio stream"""
        self.is_playing = False
        self.stop_audio_stream()
        
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2.0)
        
        return {"status": "stopped"}
    
    def get_synthesis_status(self) -> Dict:
        """Get current audio synthesis status"""
        return {
            "synthesizer_status": "active",
            "sample_rate": self.sample_rate,
            "buffer_duration": self.duration_buffer,
            "real_audio_enabled": self.real_audio,
            "is_playing": self.is_playing,
            "queue_size": self.audio_queue.qsize() if hasattr(self, 'audio_queue') else 0,
            "available_modes": ["brain_waves", "musical", "hemisphere_balance"],
            "frequency_mappings": self.brainwave_mapping,
            "timestamp": datetime.now().isoformat()
        }



