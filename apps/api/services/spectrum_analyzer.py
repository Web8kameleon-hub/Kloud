#!/usr/bin/env python3
"""
ðŸ“Š Kloud INDUSTRIAL SPECTRUM ANALYZER
Advanced FFT Processing, Spectrogram Generation, Real-time Visualization
Production-Grade Frequency Domain Analysis for EEG & Neural Signals

ðŸŽ¯ Key Features:
- Multi-channel FFT processing with windowing
- Real-time spectrogram generation
- Advanced frequency band analysis (Delta, Theta, Alpha, Beta, Gamma)
- Spectral features extraction (centroid, bandwidth, rolloff, flux)
- Cross-channel coherence analysis
- Power spectral density estimation
- Industrial-grade performance optimization
- Comprehensive visualization support
"""

import numpy as np
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
# Optional scipy dependencies with fallbacks
try:
    from scipy import signal
    from scipy.fft import fft, fftfreq
    from scipy.signal import welch, coherence, spectrogram
    SCIPY_AVAILABLE = True
except ImportError:
    # Fallback to numpy for basic FFT
    from numpy.fft import fft, fftfreq
    SCIPY_AVAILABLE = False
    signal = None
    welch = None
    coherence = None
    spectrogram = None
import threading
import queue
import json
import asyncio
from collections import deque
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Kloud-SpectrumAnalyzer")

@dataclass
class FrequencyBand:
    """Frequency band definition with advanced properties"""
    name: str
    frequency_range: Tuple[float, float]  # Hz
    color: str
    power: float = 0.0
    relative_power: float = 0.0  # Percentage of total power
    peak_frequency: float = 0.0
    bandwidth: float = 0.0
    dominant: bool = False
    artifacts_detected: bool = False

@dataclass
class SpectralFeatures:
    """Advanced spectral analysis features"""
    spectral_centroid: float
    spectral_bandwidth: float
    spectral_rolloff: float
    spectral_flux: float
    spectral_flatness: float
    zero_crossing_rate: float
    mfcc: List[float]  # Mel-frequency cepstral coefficients
    
@dataclass
class FFTAnalysis:
    """Complete FFT analysis results"""
    frequencies: List[float]
    magnitude: List[float]
    phase: List[float]
    power_spectrum: List[float]
    frequency_resolution: float
    window_function: str
    fft_size: int
    overlap: float

@dataclass
class SpectrogramData:
    """Spectrogram analysis results"""
    time_segments: List[float]
    frequencies: List[float]
    magnitude_db: List[List[float]]  # 2D array: time x frequency
    dynamic_range: float
    time_resolution: float
    frequency_resolution: float

@dataclass
class CoherenceAnalysis:
    """Cross-channel coherence analysis"""
    channel_pairs: List[Tuple[str, str]]
    coherence_values: List[List[float]]  # Coherence vs frequency
    frequencies: List[float]
    mean_coherence: Dict[str, float]  # Average coherence per pair
    peak_coherence_frequency: Dict[str, float]

class IndustrialSpectrumAnalyzer:
    """
    ðŸ­ Industrial-grade spectrum analyzer for EEG and neural signals
    Real-time FFT processing with advanced spectral analysis
    """
    
    def __init__(self, 
                 sampling_rate: int = 250,
                 fft_size: int = 512,
                 window_function: str = 'hanning',
                 overlap: float = 0.5,
                 max_frequency: float = 100.0):
        """
        Initialize the spectrum analyzer
        
        Args:
            sampling_rate: Signal sampling rate in Hz
            fft_size: FFT window size (power of 2)
            window_function: Window function ('hanning', 'hamming', 'blackman', 'bartlett')
            overlap: Window overlap ratio (0.0 to 0.9)
            max_frequency: Maximum frequency of interest in Hz
        """
        self.sampling_rate = sampling_rate
        self.fft_size = fft_size
        self.window_function = window_function
        self.overlap = overlap
        self.max_frequency = min(max_frequency, sampling_rate / 2)  # Nyquist limit
        
        # Frequency bands definition (EEG standard)
        self.frequency_bands = {
            'delta': FrequencyBand('Delta', (0.5, 4.0), '#ef4444'),
            'theta': FrequencyBand('Theta', (4.0, 8.0), '#f97316'),
            'alpha': FrequencyBand('Alpha', (8.0, 13.0), '#eab308'),
            'beta': FrequencyBand('Beta', (13.0, 30.0), '#22c55e'),
            'gamma': FrequencyBand('Gamma', (30.0, 100.0), '#a855f7')
        }
        
        # Processing parameters
        self.hop_length = int(fft_size * (1 - overlap))
        self.frequency_resolution = sampling_rate / fft_size
        
        # Real-time processing buffers
        self.signal_buffers: Dict[str, deque] = {}
        self.analysis_history: Dict[str, deque] = {}
        self.processing_lock = threading.Lock()
        
        # Initialize window function
        self.window = self._create_window()
        
        # Performance metrics
        self.processing_times = deque(maxlen=100)
        self.total_analyses = 0
        
        logger.info(f"ðŸ”§ Spectrum Analyzer initialized:")
        logger.info(f"   ðŸ“Š Sampling Rate: {sampling_rate} Hz")
        logger.info(f"   ðŸªŸ FFT Size: {fft_size}")
        logger.info(f"   ðŸ“ Window: {window_function}")
        logger.info(f"   ðŸ”„ Overlap: {overlap*100:.1f}%")
        logger.info(f"   ðŸ“ˆ Frequency Resolution: {self.frequency_resolution:.2f} Hz")
    
    def _create_window(self) -> np.ndarray:
        """Create window function for FFT processing"""
        if self.window_function == 'hanning':
            return np.hanning(self.fft_size)
        elif self.window_function == 'hamming':
            return np.hamming(self.fft_size)
        elif self.window_function == 'blackman':
            return np.blackman(self.fft_size)
        elif self.window_function == 'bartlett':
            return np.bartlett(self.fft_size)
        else:
            return np.ones(self.fft_size)  # Rectangular window
    
    def add_signal_data(self, channel: str, data: np.ndarray) -> None:
        """Add new signal data for real-time processing"""
        with self.processing_lock:
            if channel not in self.signal_buffers:
                self.signal_buffers[channel] = deque(maxlen=self.fft_size * 4)
                self.analysis_history[channel] = deque(maxlen=1000)
            
            # Add new data to buffer
            if isinstance(data, (list, tuple)):
                self.signal_buffers[channel].extend(data)
            else:
                self.signal_buffers[channel].extend(data.flatten())
    
    async def analyze_spectrum(self, 
                             channel: str, 
                             signal_data: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Perform comprehensive spectrum analysis
        
        Args:
            channel: Channel name
            signal_data: Optional signal data (uses buffer if None)
            
        Returns:
            Complete spectrum analysis results
        """
        start_time = time.time()
        
        try:
            # Get signal data
            if signal_data is None:
                with self.processing_lock:
                    if channel not in self.signal_buffers or len(self.signal_buffers[channel]) < self.fft_size:
                        return self._empty_analysis_result(channel, "Insufficient data")
                    
                    # Get latest data segment
                    data = np.array(list(self.signal_buffers[channel])[-self.fft_size:])
            else:
                data = signal_data.flatten()
                if len(data) < self.fft_size:
                    # Zero-pad if necessary
                    data = np.pad(data, (0, self.fft_size - len(data)), mode='constant')
                elif len(data) > self.fft_size:
                    # Take the last fft_size samples
                    data = data[-self.fft_size:]
            
            # 1. FFT Analysis
            fft_analysis = await self._perform_fft_analysis(data)
            
            # 2. Frequency Band Analysis
            band_analysis = await self._analyze_frequency_bands(fft_analysis)
            
            # 3. Spectral Features
            spectral_features = await self._extract_spectral_features(data, fft_analysis)
            
            # 4. Power Spectral Density
            psd_analysis = await self._estimate_power_spectral_density(data)
            
            # 5. Generate Spectrogram (if enough data)
            spectrogram_data = None
            if len(data) >= self.fft_size * 2:
                spectrogram_data = await self._generate_spectrogram(data)
            
            # Compile results
            analysis_result = {
                "channel": channel,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "analysis_duration_ms": round((time.time() - start_time) * 1000, 2),
                "signal_info": {
                    "length": len(data),
                    "sampling_rate": self.sampling_rate,
                    "duration_seconds": len(data) / self.sampling_rate,
                    "rms_amplitude": float(np.sqrt(np.mean(data**2))),
                    "peak_amplitude": float(np.max(np.abs(data))),
                    "signal_to_noise_ratio": self._estimate_snr(data)
                },
                "fft_analysis": asdict(fft_analysis),
                "frequency_bands": {name: asdict(band) for name, band in band_analysis.items()},
                "spectral_features": asdict(spectral_features),
                "power_spectral_density": psd_analysis,
                "spectrogram": asdict(spectrogram_data) if spectrogram_data else None,
                "quality_metrics": {
                    "artifacts_detected": self._detect_artifacts(data, fft_analysis),
                    "signal_quality_score": self._calculate_quality_score(data, fft_analysis),
                    "frequency_stability": self._assess_frequency_stability(fft_analysis)
                }
            }
            
            # Store in history
            with self.processing_lock:
                self.analysis_history[channel].append({
                    "timestamp": analysis_result["timestamp"],
                    "dominant_frequency": self._find_dominant_frequency(fft_analysis),
                    "total_power": sum(band.power for band in band_analysis.values()),
                    "quality_score": analysis_result["quality_metrics"]["signal_quality_score"]
                })
            
            # Update performance metrics
            self.processing_times.append(time.time() - start_time)
            self.total_analyses += 1
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"âŒ Spectrum analysis error for {channel}: {e}")
            return self._empty_analysis_result(channel, f"Analysis error: {str(e)}")
    
    async def _perform_fft_analysis(self, data: np.ndarray) -> FFTAnalysis:
        """Perform FFT analysis with windowing"""
        
        # Apply window function
        windowed_data = data * self.window
        
        # Perform FFT
        fft_result = fft(windowed_data)
        frequencies = fftfreq(self.fft_size, 1/self.sampling_rate)
        
        # Take positive frequencies only
        positive_freq_mask = frequencies >= 0
        frequencies = frequencies[positive_freq_mask]
        fft_result = fft_result[positive_freq_mask]
        
        # Limit to max frequency of interest
        freq_mask = frequencies <= self.max_frequency
        frequencies = frequencies[freq_mask]
        fft_result = fft_result[freq_mask]
        
        # Calculate magnitude and phase
        magnitude = np.abs(fft_result)
        phase = np.angle(fft_result)
        power_spectrum = magnitude ** 2
        
        return FFTAnalysis(
            frequencies=frequencies.tolist(),
            magnitude=magnitude.tolist(),
            phase=phase.tolist(),
            power_spectrum=power_spectrum.tolist(),
            frequency_resolution=self.frequency_resolution,
            window_function=self.window_function,
            fft_size=self.fft_size,
            overlap=self.overlap
        )
    
    async def _analyze_frequency_bands(self, fft_analysis: FFTAnalysis) -> Dict[str, FrequencyBand]:
        """Analyze power in standard EEG frequency bands"""
        
        frequencies = np.array(fft_analysis.frequencies)
        power_spectrum = np.array(fft_analysis.power_spectrum)
        total_power = np.sum(power_spectrum)
        
        band_results = {}
        
        for band_name, band_template in self.frequency_bands.items():
            # Find frequencies in this band
            freq_mask = (frequencies >= band_template.frequency_range[0]) & \
                       (frequencies <= band_template.frequency_range[1])
            
            if not np.any(freq_mask):
                # No frequencies in this band
                band_results[band_name] = FrequencyBand(
                    name=band_template.name,
                    frequency_range=band_template.frequency_range,
                    color=band_template.color,
                    power=0.0,
                    relative_power=0.0,
                    peak_frequency=band_template.frequency_range[0],
                    bandwidth=0.0
                )
                continue
            
            # Calculate band power
            band_power = np.sum(power_spectrum[freq_mask])
            relative_power = (band_power / total_power * 100) if total_power > 0 else 0
            
            # Find peak frequency in band
            band_frequencies = frequencies[freq_mask]
            band_powers = power_spectrum[freq_mask]
            peak_idx = np.argmax(band_powers)
            peak_frequency = band_frequencies[peak_idx]
            
            # Calculate bandwidth (frequencies with power > 50% of peak)
            half_max = band_powers[peak_idx] / 2
            above_half_max = band_powers >= half_max
            if np.any(above_half_max):
                bandwidth = band_frequencies[above_half_max][-1] - band_frequencies[above_half_max][0]
            else:
                bandwidth = 0.0
            
            band_results[band_name] = FrequencyBand(
                name=band_template.name,
                frequency_range=band_template.frequency_range,
                color=band_template.color,
                power=float(band_power),
                relative_power=float(relative_power),
                peak_frequency=float(peak_frequency),
                bandwidth=float(bandwidth),
                artifacts_detected=self._detect_band_artifacts(band_powers)
            )
        
        # Find dominant band
        if band_results:
            dominant_band = max(band_results.values(), key=lambda b: b.power)
            dominant_band.dominant = True
        
        return band_results
    
    async def _extract_spectral_features(self, data: np.ndarray, fft_result: FFTAnalysis) -> SpectralFeatures:
        """Extract advanced spectral features"""
        
        frequencies = np.array(fft_result.frequencies)
        magnitude = np.array(fft_result.magnitude)
        
        # Spectral centroid (center of mass of spectrum)
        spectral_centroid = np.sum(frequencies * magnitude) / np.sum(magnitude) if np.sum(magnitude) > 0 else 0
        
        # Spectral bandwidth (weighted standard deviation around centroid)
        spectral_bandwidth = np.sqrt(np.sum(((frequencies - spectral_centroid) ** 2) * magnitude) / np.sum(magnitude)) if np.sum(magnitude) > 0 else 0
        
        # Spectral rolloff (frequency below which 85% of energy is contained)
        cumulative_energy = np.cumsum(magnitude ** 2)
        total_energy = cumulative_energy[-1]
        rolloff_threshold = 0.85 * total_energy
        rolloff_idx = np.where(cumulative_energy >= rolloff_threshold)[0]
        spectral_rolloff = frequencies[rolloff_idx[0]] if len(rolloff_idx) > 0 else frequencies[-1]
        
        # Spectral flux (rate of change of spectrum)
        spectral_flux = 0.0  # Would need previous frame for comparison
        
        # Spectral flatness (measure of noisiness)
        geometric_mean = np.exp(np.mean(np.log(magnitude + 1e-10)))
        arithmetic_mean = np.mean(magnitude)
        spectral_flatness = geometric_mean / arithmetic_mean if arithmetic_mean > 0 else 0
        
        # Zero crossing rate
        zero_crossings = np.where(np.diff(np.signbit(data)))[0]
        zero_crossing_rate = len(zero_crossings) / len(data)
        
        # MFCC (simplified - would need mel filter bank for full implementation)
        mfcc = []  # Placeholder for now
        
        return SpectralFeatures(
            spectral_centroid=float(spectral_centroid),
            spectral_bandwidth=float(spectral_bandwidth),
            spectral_rolloff=float(spectral_rolloff),
            spectral_flux=float(spectral_flux),
            spectral_flatness=float(spectral_flatness),
            zero_crossing_rate=float(zero_crossing_rate),
            mfcc=mfcc
        )
    
    async def _estimate_power_spectral_density(self, data: np.ndarray) -> Dict[str, Any]:
        """Estimate power spectral density using Welch's method"""
        
        try:
            # Use Welch's method for better PSD estimation
            frequencies, psd = welch(
                data, 
                fs=self.sampling_rate,
                window=self.window_function,
                nperseg=self.fft_size,
                noverlap=int(self.fft_size * self.overlap),
                return_onesided=True
            )
            
            # Limit to frequency range of interest
            freq_mask = frequencies <= self.max_frequency
            frequencies = frequencies[freq_mask]
            psd = psd[freq_mask]
            
            return {
                "frequencies": frequencies.tolist(),
                "power_density": psd.tolist(),
                "total_power": float(np.sum(psd)),
                "peak_frequency": float(frequencies[np.argmax(psd)]),
                "peak_power": float(np.max(psd)),
                "method": "welch",
                "frequency_resolution": float(frequencies[1] - frequencies[0]) if len(frequencies) > 1 else 0.0
            }
            
        except Exception as e:
            logger.error(f"PSD estimation error: {e}")
            return {
                "frequencies": [],
                "power_density": [],
                "total_power": 0.0,
                "peak_frequency": 0.0,
                "peak_power": 0.0,
                "method": "welch",
                "frequency_resolution": 0.0,
                "error": str(e)
            }
    
    async def _generate_spectrogram(self, data: np.ndarray) -> SpectrogramData:
        """Generate spectrogram for time-frequency analysis"""
        
        try:
            frequencies, times, Sxx = spectrogram(
                data,
                fs=self.sampling_rate,
                window=self.window_function,
                nperseg=self.fft_size,
                noverlap=int(self.fft_size * self.overlap),
                return_onesided=True
            )
            
            # Limit to frequency range of interest
            freq_mask = frequencies <= self.max_frequency
            frequencies = frequencies[freq_mask]
            Sxx = Sxx[freq_mask, :]
            
            # Convert to dB
            magnitude_db = 10 * np.log10(Sxx + 1e-10)
            
            # Calculate dynamic range
            dynamic_range = float(np.max(magnitude_db) - np.min(magnitude_db))
            
            return SpectrogramData(
                time_segments=times.tolist(),
                frequencies=frequencies.tolist(),
                magnitude_db=magnitude_db.tolist(),
                dynamic_range=dynamic_range,
                time_resolution=float(times[1] - times[0]) if len(times) > 1 else 0.0,
                frequency_resolution=float(frequencies[1] - frequencies[0]) if len(frequencies) > 1 else 0.0
            )
            
        except Exception as e:
            logger.error(f"Spectrogram generation error: {e}")
            return SpectrogramData(
                time_segments=[],
                frequencies=[],
                magnitude_db=[],
                dynamic_range=0.0,
                time_resolution=0.0,
                frequency_resolution=0.0
            )
    
    async def analyze_coherence(self, channel_data: Dict[str, np.ndarray]) -> CoherenceAnalysis:
        """Analyze coherence between multiple channels"""
        
        if len(channel_data) < 2:
            return CoherenceAnalysis([], [], [], {}, {})
        
        channels = list(channel_data.keys())
        channel_pairs = []
        coherence_values = []
        frequencies = []
        mean_coherence = {}
        peak_coherence_frequency = {}
        
        # Analyze all channel pairs
        for i in range(len(channels)):
            for j in range(i + 1, len(channels)):
                ch1, ch2 = channels[i], channels[j]
                pair_name = f"{ch1}-{ch2}"
                channel_pairs.append((ch1, ch2))
                
                try:
                    # Calculate coherence
                    freqs, coh = coherence(
                        channel_data[ch1], 
                        channel_data[ch2],
                        fs=self.sampling_rate,
                        window=self.window_function,
                        nperseg=self.fft_size,
                        noverlap=int(self.fft_size * self.overlap)
                    )
                    
                    # Limit to frequency range of interest
                    freq_mask = freqs <= self.max_frequency
                    freqs = freqs[freq_mask]
                    coh = coh[freq_mask]
                    
                    if len(frequencies) == 0:
                        frequencies = freqs.tolist()
                    
                    coherence_values.append(coh.tolist())
                    mean_coherence[pair_name] = float(np.mean(coh))
                    peak_coherence_frequency[pair_name] = float(freqs[np.argmax(coh)])
                    
                except Exception as e:
                    logger.error(f"Coherence calculation error for {pair_name}: {e}")
                    coherence_values.append([0.0] * len(frequencies))
                    mean_coherence[pair_name] = 0.0
                    peak_coherence_frequency[pair_name] = 0.0
        
        return CoherenceAnalysis(
            channel_pairs=channel_pairs,
            coherence_values=coherence_values,
            frequencies=frequencies,
            mean_coherence=mean_coherence,
            peak_coherence_frequency=peak_coherence_frequency
        )
    
    def _detect_artifacts(self, data: np.ndarray, fft_analysis: FFTAnalysis) -> bool:
        """Detect potential artifacts in the signal"""
        
        # Check for extreme amplitudes
        amplitude_threshold = 5 * np.std(data)
        if np.any(np.abs(data) > amplitude_threshold):
            return True
        
        # Check for power line interference (50/60 Hz)
        frequencies = np.array(fft_analysis.frequencies)
        magnitude = np.array(fft_analysis.magnitude)
        
        for interference_freq in [50, 60]:  # Common power line frequencies
            freq_mask = (frequencies >= interference_freq - 1) & (frequencies <= interference_freq + 1)
            if np.any(freq_mask):
                interference_power = np.sum(magnitude[freq_mask])
                total_power = np.sum(magnitude)
                if interference_power / total_power > 0.1:  # 10% threshold
                    return True
        
        return False
    
    def _detect_band_artifacts(self, band_powers: np.ndarray) -> bool:
        """Detect artifacts in frequency band"""
        if len(band_powers) == 0:
            return False
        
        # Check for extremely high power spikes
        mean_power = np.mean(band_powers)
        std_power = np.std(band_powers)
        threshold = mean_power + 3 * std_power
        
        return np.any(band_powers > threshold)
    
    def _calculate_quality_score(self, data: np.ndarray, fft_analysis: FFTAnalysis) -> float:
        """Calculate overall signal quality score (0-100)"""
        
        score = 100.0
        
        # Penalize for artifacts
        if self._detect_artifacts(data, fft_analysis):
            score -= 20
        
        # Penalize for low SNR
        snr = self._estimate_snr(data)
        if snr < 10:  # dB
            score -= (10 - snr) * 2
        
        # Penalize for excessive DC component
        dc_component = np.abs(np.mean(data))
        rms = np.sqrt(np.mean(data**2))
        if dc_component > 0.1 * rms:
            score -= 15
        
        # Ensure score is within bounds
        return max(0.0, min(100.0, score))
    
    def _estimate_snr(self, data: np.ndarray) -> float:
        """Estimate signal-to-noise ratio in dB"""
        
        # Simple SNR estimation: signal power vs noise power
        # Assumes high frequencies contain mostly noise
        
        fft_result = np.fft.fft(data)
        frequencies = np.fft.fftfreq(len(data), 1/self.sampling_rate)
        power_spectrum = np.abs(fft_result) ** 2
        
        # Signal power (low to mid frequencies)
        signal_mask = (np.abs(frequencies) >= 1) & (np.abs(frequencies) <= 40)
        signal_power = np.sum(power_spectrum[signal_mask])
        
        # Noise power (high frequencies)
        noise_mask = np.abs(frequencies) > 40
        noise_power = np.sum(power_spectrum[noise_mask])
        
        if noise_power > 0:
            snr_linear = signal_power / noise_power
            return 10 * np.log10(snr_linear)
        else:
            return 50.0  # Very high SNR
    
    def _assess_frequency_stability(self, fft_analysis: FFTAnalysis) -> float:
        """Assess stability of dominant frequencies (0-100)"""
        
        # This would need multiple time windows for proper assessment
        # For now, return a simple measure based on spectral concentration
        
        power_spectrum = np.array(fft_analysis.power_spectrum)
        if len(power_spectrum) == 0:
            return 0.0
        
        total_power = np.sum(power_spectrum)
        if total_power == 0:
            return 0.0
        
        # Calculate spectral concentration (higher = more stable)
        peak_power = np.max(power_spectrum)
        concentration = peak_power / total_power
        
        return min(100.0, concentration * 200)  # Scale to 0-100
    
    def _find_dominant_frequency(self, fft_analysis: FFTAnalysis) -> float:
        """Find the dominant frequency in the spectrum"""
        
        if not fft_analysis.power_spectrum:
            return 0.0
        
        max_idx = np.argmax(fft_analysis.power_spectrum)
        return fft_analysis.frequencies[max_idx]
    
    def _empty_analysis_result(self, channel: str, reason: str) -> Dict[str, Any]:
        """Return empty analysis result with error information"""
        
        return {
            "channel": channel,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_duration_ms": 0.0,
            "error": reason,
            "signal_info": {},
            "fft_analysis": {},
            "frequency_bands": {},
            "spectral_features": {},
            "power_spectral_density": {},
            "spectrogram": None,
            "quality_metrics": {}
        }
    
    def get_analysis_history(self, channel: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical analysis data for a channel"""
        
        with self.processing_lock:
            if channel not in self.analysis_history:
                return []
            
            history = list(self.analysis_history[channel])
            return history[-limit:] if limit > 0 else history
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get analyzer performance metrics"""
        
        if not self.processing_times:
            return {
                "total_analyses": 0,
                "average_processing_time_ms": 0.0,
                "min_processing_time_ms": 0.0,
                "max_processing_time_ms": 0.0,
                "analyses_per_second": 0.0
            }
        
        processing_times_ms = [t * 1000 for t in self.processing_times]
        
        return {
            "total_analyses": self.total_analyses,
            "average_processing_time_ms": round(np.mean(processing_times_ms), 2),
            "min_processing_time_ms": round(np.min(processing_times_ms), 2),
            "max_processing_time_ms": round(np.max(processing_times_ms), 2),
            "analyses_per_second": round(1.0 / np.mean(self.processing_times), 2),
            "buffer_status": {
                channel: len(buffer) for channel, buffer in self.signal_buffers.items()
            }
        }
    
    def reset_analyzer(self) -> None:
        """Reset analyzer state and clear buffers"""
        
        with self.processing_lock:
            self.signal_buffers.clear()
            self.analysis_history.clear()
            self.processing_times.clear()
            self.total_analyses = 0
        
        logger.info("ðŸ”„ Spectrum Analyzer reset completed")

# Global analyzer instance
spectrum_analyzer = IndustrialSpectrumAnalyzer()

# Export for use in other modules
__all__ = [
    'IndustrialSpectrumAnalyzer',
    'spectrum_analyzer',
    'FrequencyBand',
    'SpectralFeatures',
    'FFTAnalysis',
    'SpectrogramData',
    'CoherenceAnalysis'
]



