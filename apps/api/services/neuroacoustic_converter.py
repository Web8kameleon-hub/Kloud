"""
ðŸŽµ Kloud Neuroacoustic Converter
====================================
Advanced EEG-to-Audio conversion engine pÃ«r neuroacoustic analysis.
Real-time neural signal processing & audio synthesis.

REAL NEUROACOUSTIC TECHNOLOGY - NO MOCK DATA
"""

import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.fft import fft, fftfreq
import asyncio
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NeuroAcousticConverter:
    """Advanced EEG-to-Audio conversion engine"""
    
    def __init__(self, sample_rate: int = 44100, eeg_channels: int = 8):
        self.sample_rate = sample_rate
        self.eeg_channels = eeg_channels
        self.eeg_sample_rate = 256  # Standard EEG sampling rate
        self.frequency_bands = {
            'delta': (0.5, 4),
            'theta': (4, 8), 
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 100)
        }
        self.conversion_active = False
        
    async def convert_eeg_to_audio(self, eeg_data: np.ndarray, 
                                 conversion_mode: str = 'harmonic') -> Dict:
        """
        Convert EEG signals to neuroacoustic audio
        
        Args:
            eeg_data: Multi-channel EEG data (channels x samples)
            conversion_mode: 'harmonic', 'frequency_mapping', 'rhythmic'
        """
        try:
            logger.info(f"ðŸŽµ Starting neuroacoustic conversion: {conversion_mode}")
            
            # Validate EEG data
            if eeg_data.shape[0] != self.eeg_channels:
                raise ValueError(f"Expected {self.eeg_channels} channels, got {eeg_data.shape[0]}")
            
            # Extract frequency components
            frequency_analysis = await self._analyze_frequency_bands(eeg_data)
            
            # Convert based on mode
            if conversion_mode == 'harmonic':
                audio_data = await self._harmonic_conversion(eeg_data, frequency_analysis)
            elif conversion_mode == 'frequency_mapping':
                audio_data = await self._frequency_mapping_conversion(eeg_data, frequency_analysis)
            elif conversion_mode == 'rhythmic':
                audio_data = await self._rhythmic_conversion(eeg_data, frequency_analysis)
            else:
                raise ValueError(f"Unknown conversion mode: {conversion_mode}")
            
            # Audio properties
            audio_properties = await self._analyze_audio_properties(audio_data)
            
            # Neural patterns
            neural_patterns = await self._extract_neural_patterns(eeg_data)
            
            return {
                "success": True,
                "conversion_mode": conversion_mode,
                "audio_data": audio_data.tolist(),
                "audio_properties": audio_properties,
                "neural_patterns": neural_patterns,
                "frequency_analysis": frequency_analysis,
                "metadata": {
                    "sample_rate": self.sample_rate,
                    "duration_seconds": len(audio_data) / self.sample_rate,
                    "channels_processed": eeg_data.shape[0],
                    "samples_processed": eeg_data.shape[1],
                    "timestamp": datetime.utcnow().isoformat()
                },
                "real_neuroacoustic_data": True
            }
            
        except Exception as e:
            logger.error(f"ðŸ’¥ Neuroacoustic conversion error: {str(e)}")
            raise
    
    async def _analyze_frequency_bands(self, eeg_data: np.ndarray) -> Dict:
        """Extract power in different frequency bands"""
        
        band_powers = {}
        
        for band_name, (low_freq, high_freq) in self.frequency_bands.items():
            # Bandpass filter pÃ«r secilÃ«n bandÃ«
            nyquist = self.eeg_sample_rate / 2
            low = low_freq / nyquist
            high = high_freq / nyquist
            
            b, a = signal.butter(4, [low, high], btype='band')
            
            # Filter tÃ« gjitha channels
            band_power = 0
            for channel in range(eeg_data.shape[0]):
                filtered = signal.filtfilt(b, a, eeg_data[channel])
                band_power += np.mean(filtered ** 2)
            
            band_powers[band_name] = {
                'power': float(band_power / eeg_data.shape[0]),
                'frequency_range': [low_freq, high_freq],
                'dominance_percentage': 0  # Will calculate later
            }
        
        # Calculate dominance percentages
        total_power = sum(bp['power'] for bp in band_powers.values())
        for band in band_powers.values():
            band['dominance_percentage'] = (band['power'] / total_power) * 100
        
        return band_powers
    
    async def _harmonic_conversion(self, eeg_data: np.ndarray, freq_analysis: Dict) -> np.ndarray:
        """Convert EEG to harmonic audio using frequency mapping"""
        
        # Duration based on EEG samples
        duration = eeg_data.shape[1] / self.eeg_sample_rate
        t = np.linspace(0, duration, int(duration * self.sample_rate))
        
        # Base frequency from alpha band dominance
        alpha_power = freq_analysis['alpha']['dominance_percentage']
        base_freq = 220 + (alpha_power * 4)  # A3 to higher based on alpha
        
        # Create harmonic series
        audio = np.zeros_like(t)
        
        for band_name, band_data in freq_analysis.items():
            power = band_data['dominance_percentage'] / 100
            freq_range = band_data['frequency_range']
            
            # Map neural frequency to audio frequency
            if band_name == 'delta':
                harmonic_freq = base_freq * 0.5
            elif band_name == 'theta':
                harmonic_freq = base_freq * 0.75
            elif band_name == 'alpha':
                harmonic_freq = base_freq
            elif band_name == 'beta':
                harmonic_freq = base_freq * 1.5
            elif band_name == 'gamma':
                harmonic_freq = base_freq * 2
            
            # Add harmonic component with amplitude based on power
            audio += power * np.sin(2 * np.pi * harmonic_freq * t)
        
        # Apply envelope based on EEG amplitude variations
        envelope = await self._calculate_amplitude_envelope(eeg_data, len(t))
        audio *= envelope
        
        # Normalize
        audio = audio / np.max(np.abs(audio))
        
        return audio
    
    async def _frequency_mapping_conversion(self, eeg_data: np.ndarray, freq_analysis: Dict) -> np.ndarray:
        """Direct frequency mapping conversion"""
        
        duration = eeg_data.shape[1] / self.eeg_sample_rate
        t = np.linspace(0, duration, int(duration * self.sample_rate))
        audio = np.zeros_like(t)
        
        # Map each EEG channel to a different audio frequency
        base_frequencies = [220, 247, 277, 311, 349, 392, 440, 494]  # A3 to A#4
        
        for channel in range(min(self.eeg_channels, len(base_frequencies))):
            # Get dominant frequency for this channel
            channel_fft = fft(eeg_data[channel])
            freqs = fftfreq(len(eeg_data[channel]), 1/self.eeg_sample_rate)
            dominant_idx = np.argmax(np.abs(channel_fft[:len(channel_fft)//2]))
            dominant_freq = abs(freqs[dominant_idx])
            
            # Map to audio frequency
            audio_freq = base_frequencies[channel] + (dominant_freq * 2)
            
            # Amplitude based on channel power
            amplitude = np.std(eeg_data[channel]) / 100
            
            # Add to audio mix
            audio += amplitude * np.sin(2 * np.pi * audio_freq * t)
        
        # Normalize
        audio = audio / np.max(np.abs(audio))
        
        return audio
    
    async def _rhythmic_conversion(self, eeg_data: np.ndarray, freq_analysis: Dict) -> np.ndarray:
        """Convert EEG to rhythmic audio patterns"""
        
        duration = eeg_data.shape[1] / self.eeg_sample_rate
        t = np.linspace(0, duration, int(duration * self.sample_rate))
        
        # Base rhythm from theta/alpha ratio
        theta_power = freq_analysis['theta']['dominance_percentage']
        alpha_power = freq_analysis['alpha']['dominance_percentage']
        
        # BPM based on neural rhythms
        bpm = 60 + (alpha_power - theta_power)  # 60-120 BPM range
        beat_freq = bpm / 60  # Hz
        
        # Create rhythmic pattern
        beat_pattern = np.sin(2 * np.pi * beat_freq * t)
        
        # Modulate with higher frequencies
        beta_modulation = np.sin(2 * np.pi * beat_freq * 4 * t) * (freq_analysis['beta']['dominance_percentage'] / 100)
        gamma_modulation = np.sin(2 * np.pi * beat_freq * 8 * t) * (freq_analysis['gamma']['dominance_percentage'] / 100)
        
        # Combine
        audio = beat_pattern + (beta_modulation * 0.3) + (gamma_modulation * 0.2)
        
        # Apply amplitude envelope
        envelope = await self._calculate_amplitude_envelope(eeg_data, len(t))
        audio *= envelope
        
        # Normalize
        audio = audio / np.max(np.abs(audio))
        
        return audio
    
    async def _calculate_amplitude_envelope(self, eeg_data: np.ndarray, audio_length: int) -> np.ndarray:
        """Calculate amplitude envelope from EEG data"""
        
        # Average amplitude across all channels
        avg_amplitude = np.mean(np.abs(eeg_data), axis=0)
        
        # Smooth the envelope
        from scipy.ndimage import gaussian_filter1d
        smoothed = gaussian_filter1d(avg_amplitude, sigma=2)
        
        # Resample to audio length
        envelope = np.interp(np.linspace(0, len(smoothed), audio_length), 
                           np.arange(len(smoothed)), smoothed)
        
        # Normalize dhe add minimum level
        envelope = (envelope / np.max(envelope)) * 0.8 + 0.2
        
        return envelope
    
    async def _analyze_audio_properties(self, audio_data: np.ndarray) -> Dict:
        """Analyze properties of generated audio"""
        
        # Fundamental frequency
        fft_audio = fft(audio_data)
        freqs = fftfreq(len(audio_data), 1/self.sample_rate)
        fundamental_idx = np.argmax(np.abs(fft_audio[:len(fft_audio)//2]))
        fundamental_freq = abs(freqs[fundamental_idx])
        
        # Harmonic content analysis
        harmonics = []
        for i in range(2, 6):  # Check first 4 harmonics
            harmonic_freq = fundamental_freq * i
            harmonic_idx = np.argmin(np.abs(freqs - harmonic_freq))
            if harmonic_idx < len(fft_audio)//2:
                harmonics.append({
                    'frequency': harmonic_freq,
                    'amplitude': float(np.abs(fft_audio[harmonic_idx]))
                })
        
        # Tempo mapping (rhythm detection)
        tempo, beats = librosa.beat.beat_track(y=audio_data, sr=self.sample_rate)
        
        # Audio quality metrics
        rms = np.sqrt(np.mean(audio_data ** 2))
        peak = np.max(np.abs(audio_data))
        
        return {
            'fundamental_frequency': float(fundamental_freq),
            'fundamental_note': self._freq_to_note(fundamental_freq),
            'harmonic_content': harmonics,
            'tempo_bpm': float(tempo),
            'audio_quality': {
                'rms_level': float(rms),
                'peak_level': float(peak),
                'dynamic_range': float(peak / (rms + 1e-10)),
                'quality_rating': 'High Fidelity' if peak > 0.5 else 'Standard'
            },
            'spectral_analysis': {
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate))),
                'spectral_rolloff': float(np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(audio_data)))
            }
        }
    
    def _freq_to_note(self, frequency: float) -> str:
        """Convert frequency to musical note"""
        A4 = 440
        C0 = A4*np.power(2, -4.75)
        
        if frequency > 0:
            h = round(12*np.log2(frequency/C0))
            octave = h // 12
            n = h % 12
            notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            return f"{notes[n]}{octave}"
        return "N/A"
    
    async def _extract_neural_patterns(self, eeg_data: np.ndarray) -> Dict:
        """Extract neural patterns from EEG data"""
        
        patterns = {}
        
        # Dominant rhythm detection
        channel_avg = np.mean(eeg_data, axis=0)
        fft_signal = fft(channel_avg)
        freqs = fftfreq(len(channel_avg), 1/self.eeg_sample_rate)
        dominant_idx = np.argmax(np.abs(fft_signal[:len(fft_signal)//2]))
        dominant_freq = abs(freqs[dominant_idx])
        
        patterns['dominant_rhythm'] = {
            'frequency': float(dominant_freq),
            'band': self._classify_frequency_band(dominant_freq),
            'power': float(np.abs(fft_signal[dominant_idx]))
        }
        
        # Interhemispheric coherence (assuming channels 0-3 left, 4-7 right)
        if self.eeg_channels >= 8:
            left_channels = eeg_data[:4]
            right_channels = eeg_data[4:]
            
            left_avg = np.mean(left_channels, axis=0)
            right_avg = np.mean(right_channels, axis=0)
            
            coherence = np.corrcoef(left_avg, right_avg)[0, 1]
            patterns['interhemispheric_coherence'] = {
                'correlation': float(coherence),
                'quality': 'High' if coherence > 0.7 else 'Moderate' if coherence > 0.4 else 'Low'
            }
        
        # Complexity (entropy)
        entropy = -np.sum((eeg_data ** 2) * np.log(eeg_data ** 2 + 1e-10), axis=1)
        patterns['complexity'] = {
            'mean_entropy': float(np.mean(entropy)),
            'complexity_rating': 'High' if np.mean(entropy) > 5 else 'Moderate'
        }
        
        # Phase synchronization
        from scipy.signal import hilbert
        phases = np.angle(hilbert(eeg_data, axis=1))
        phase_sync = np.mean(np.cos(phases), axis=0)
        patterns['phase_synchronization'] = {
            'mean_sync': float(np.mean(np.abs(phase_sync))),
            'sync_quality': 'Good' if np.mean(np.abs(phase_sync)) > 0.5 else 'Fair'
        }
        
        return patterns
    
    def _classify_frequency_band(self, frequency: float) -> str:
        """Classify frequency into EEG band"""
        for band_name, (low, high) in self.frequency_bands.items():
            if low <= frequency <= high:
                return band_name
        return 'unknown'
    
    async def save_neuroacoustic_file(self, audio_data: np.ndarray, 
                                    filename: str, metadata: Dict) -> str:
        """Save neuroacoustic audio file with metadata"""
        
        filepath = f"C:/Kloud-cloud/data/neuroacoustic/{filename}"
        
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save audio file
        sf.write(f"{filepath}.wav", audio_data, self.sample_rate)
        
        # Save metadata
        with open(f"{filepath}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"ðŸ’¾ Neuroacoustic file saved: {filepath}")
        return filepath

# Factory function
async def create_neuroacoustic_converter() -> NeuroAcousticConverter:
    """Create neuroacoustic converter instance"""
    converter = NeuroAcousticConverter()
    logger.info("ðŸŽµ NeuroAcoustic Converter initialized - REAL TECHNOLOGY READY")
    return converter



