"""
Kloud Industrial EEG Processor
Advanced real-time processing of EEG signals with industrial-grade algorithms
Business: Ledjan Ahmati - WEB8euroweb GmbH

Industrial Features:
- Advanced signal processing with adaptive filtering
- Real-time artifact detection and removal
- Independent Component Analysis (ICA) for noise reduction
- Spectral analysis with advanced windowing techniques
- Machine learning-based signal classification
- Multi-threading for real-time performance
- Comprehensive quality metrics and validation
"""

import asyncio
import logging
import time
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Union, Callable, Any
import uuid

import numpy as np
import scipy.signal as signal
from scipy.fft import fft, fftfreq, fftshift
from scipy.stats import zscore, kurtosis, skew

# Optional advanced dependencies
try:
    from sklearn.decomposition import FastICA
    from sklearn.preprocessing import StandardScaler
    ICA_AVAILABLE = True
except ImportError:
    ICA_AVAILABLE = False
    FastICA = StandardScaler = None

try:
    import scipy.signal.windows as windows
    ADVANCED_WINDOWS_AVAILABLE = True
except ImportError:
    ADVANCED_WINDOWS_AVAILABLE = False
    windows = None

logger = logging.getLogger(__name__)


class IndustrialEEGProcessor:
    """Industrial-grade real-time EEG signal processing and analysis"""
    
    def __init__(self, sampling_rate: int = 256, max_channels: int = 64):
        self.sampling_rate = sampling_rate
        self.max_channels = max_channels
        self.processor_id = f"EEG_{uuid.uuid4().hex[:8]}"
        
        # Standard EEG channel layout (10-20 system)
        self.standard_channels = [
            "Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2", 
            "F7", "F8", "T3", "T4", "T5", "T6", "Fz", "Cz", "Pz", "A1", "A2"
        ]
        
        # Extended channel support for high-density EEG
        self.extended_channels = [
            "AF3", "AF4", "F1", "F2", "F5", "F6", "FC1", "FC2", "FC5", "FC6",
            "C1", "C2", "C5", "C6", "CP1", "CP2", "CP5", "CP6", "P1", "P2",
            "P5", "P6", "PO3", "PO4", "PO7", "PO8"
        ]
        
        self.available_channels = self.standard_channels + self.extended_channels
        self.active_channels = set()
        
        # Advanced buffering system with thread-safe operations
        self.buffer_duration = 10.0  # 10 seconds industrial buffer
        self.buffer_size = int(sampling_rate * self.buffer_duration)
        self.signal_buffers = {}
        self.quality_buffers = {}
        self.timestamp_buffers = {}
        
        # Industrial frequency band definitions with sub-bands
        self.frequency_bands = {
            "delta": {
                "range": (0.5, 4.0),
                "sub_bands": {
                    "slow_delta": (0.5, 1.0),
                    "fast_delta": (1.0, 4.0)
                }
            },
            "theta": {
                "range": (4.0, 8.0),
                "sub_bands": {
                    "slow_theta": (4.0, 6.0),
                    "fast_theta": (6.0, 8.0)
                }
            },
            "alpha": {
                "range": (8.0, 13.0),
                "sub_bands": {
                    "slow_alpha": (8.0, 10.0),
                    "fast_alpha": (10.0, 13.0)
                }
            },
            "beta": {
                "range": (13.0, 30.0),
                "sub_bands": {
                    "low_beta": (13.0, 20.0),
                    "high_beta": (20.0, 30.0)
                }
            },
            "gamma": {
                "range": (30.0, 100.0),
                "sub_bands": {
                    "low_gamma": (30.0, 50.0),
                    "high_gamma": (50.0, 100.0)
                }
            }
        }
        
        # Advanced processing parameters
        self.filter_order = 6  # Higher order for better frequency response
        self.notch_frequencies = [50.0, 60.0]  # Power line interference
        self.artifact_thresholds = {
            "amplitude_threshold": 150.0,  # Î¼V
            "gradient_threshold": 50.0,    # Î¼V/sample
            "variance_threshold": 100.0,   # Î¼VÂ²
            "kurtosis_threshold": 5.0,     # Dimensionless
            "frequency_ratio_threshold": 0.3  # Power ratio
        }
        
        # ICA for artifact removal
        self.ica_model = None
        self.ica_trained = False
        self.ica_buffer_required = int(sampling_rate * 60)  # 1 minute for ICA training
        
        # Performance monitoring
        self.processing_stats = {
            "samples_processed": 0,
            "artifacts_detected": 0,
            "filters_applied": 0,
            "ica_components_removed": 0,
            "processing_time_ms": deque(maxlen=1000),
            "last_update": datetime.now(timezone.utc)
        }
        
        # Thread safety
        self.processing_lock = threading.RLock()
        self.is_processing = False
        
        logger.info(f"Industrial EEG Processor [{self.processor_id}] initialized: "
                   f"{sampling_rate}Hz, {max_channels} channels, "
                   f"ICA={ICA_AVAILABLE}, Advanced Windows={ADVANCED_WINDOWS_AVAILABLE}")
    
    def register_channel(self, channel: str) -> bool:
        """Register a new EEG channel for processing"""
        if len(self.active_channels) >= self.max_channels:
            logger.warning(f"Maximum channels ({self.max_channels}) reached")
            return False
            
        if channel not in self.available_channels:
            logger.warning(f"Unknown channel: {channel}")
            return False
        
        with self.processing_lock:
            self.active_channels.add(channel)
            self.signal_buffers[channel] = deque(maxlen=self.buffer_size)
            self.quality_buffers[channel] = deque(maxlen=100)  # Quality metrics
            self.timestamp_buffers[channel] = deque(maxlen=self.buffer_size)
            
        logger.info(f"Channel {channel} registered. Active channels: {len(self.active_channels)}")
        return True
    
    def unregister_channel(self, channel: str) -> bool:
        """Unregister an EEG channel"""
        with self.processing_lock:
            if channel in self.active_channels:
                self.active_channels.remove(channel)
                del self.signal_buffers[channel]
                del self.quality_buffers[channel]
                del self.timestamp_buffers[channel]
                logger.info(f"Channel {channel} unregistered")
                return True
        return False
    
    def add_sample(self, channel: str, sample: float, timestamp: Optional[float] = None) -> bool:
        """Add a new EEG sample with industrial-grade validation"""
        if channel not in self.active_channels:
            logger.warning(f"Attempt to add sample to unregistered channel: {channel}")
            return False
        
        if timestamp is None:
            timestamp = time.time()
            
        # Validate sample value
        if not isinstance(sample, (int, float)) or not np.isfinite(sample):
            logger.warning(f"Invalid sample value for {channel}: {sample}")
            return False
        
        # Check for reasonable EEG amplitude range (-500 to +500 Î¼V)
        if abs(sample) > 500.0:
            logger.warning(f"Sample amplitude out of range for {channel}: {sample}Î¼V")
            # Don't reject, but flag for artifact detection
        
        with self.processing_lock:
            self.signal_buffers[channel].append(float(sample))
            self.timestamp_buffers[channel].append(timestamp)
            self.processing_stats["samples_processed"] += 1
            
            # Real-time quality assessment
            if len(self.signal_buffers[channel]) >= 10:
                recent_samples = list(self.signal_buffers[channel])[-10:]
                quality_score = self._calculate_signal_quality(recent_samples)
                self.quality_buffers[channel].append(quality_score)
        
        return True
    
    def add_multi_channel_sample(self, samples: Dict[str, float], timestamp: Optional[float] = None) -> Dict[str, bool]:
        """Add samples from multiple channels with synchronized timestamps"""
        if timestamp is None:
            timestamp = time.time()
            
        results = {}
        for channel, sample in samples.items():
            results[channel] = self.add_sample(channel, sample, timestamp)
            
        return results
    
    def add_sample_batch(self, channel: str, samples: List[float], 
                        timestamps: Optional[List[float]] = None) -> int:
        """Add multiple samples at once for better performance"""
        if channel not in self.active_channels:
            return 0
            
        if timestamps is None:
            base_time = time.time()
            timestamps = [base_time + (i / self.sampling_rate) for i in range(len(samples))]
        elif len(timestamps) != len(samples):
            logger.error("Timestamp count must match sample count")
            return 0
        
        successful_adds = 0
        for sample, timestamp in zip(samples, timestamps):
            if self.add_sample(channel, sample, timestamp):
                successful_adds += 1
                
        return successful_adds
    
    def get_channel_data(self, channel: str, duration_seconds: float = 2.0, 
                        apply_filters: bool = True) -> Dict[str, Union[np.ndarray, List[float]]]:
        """Get recent data from specific channel with metadata"""
        if channel not in self.active_channels:
            return {
                "data": np.array([]),
                "timestamps": [],
                "quality_scores": [],
                "sample_count": 0,
                "duration": 0.0
            }
        
        num_samples = int(duration_seconds * self.sampling_rate)
        
        with self.processing_lock:
            # Get raw data
            raw_data = list(self.signal_buffers[channel])[-num_samples:]
            timestamps = list(self.timestamp_buffers[channel])[-num_samples:]
            quality_scores = list(self.quality_buffers[channel])[-min(len(self.quality_buffers[channel]), num_samples//10):]
        
        if not raw_data:
            return {
                "data": np.array([]),
                "timestamps": [],
                "quality_scores": [],
                "sample_count": 0,
                "duration": 0.0
            }
        
        data_array = np.array(raw_data)
        
        # Apply industrial-grade filtering if requested
        if apply_filters and len(data_array) > self.filter_order * 3:
            data_array = self.apply_industrial_filters(data_array)
        
        actual_duration = (timestamps[-1] - timestamps[0]) if len(timestamps) > 1 else 0.0
        
        return {
            "data": data_array,
            "timestamps": timestamps,
            "quality_scores": quality_scores,
            "sample_count": len(raw_data),
            "duration": actual_duration,
            "sampling_rate": self.sampling_rate,
            "channel": channel
        }
    
    def get_multi_channel_data(self, channels: List[str], duration_seconds: float = 2.0,
                              synchronized: bool = True) -> Dict[str, Dict]:
        """Get synchronized data from multiple channels"""
        results = {}
        
        for channel in channels:
            if channel in self.active_channels:
                results[channel] = self.get_channel_data(channel, duration_seconds)
        
        if synchronized and len(results) > 1:
            # Synchronize timestamps across channels
            results = self._synchronize_channel_data(results)
        
        return results
    
    def apply_industrial_filters(self, data: np.ndarray, filter_config: Optional[Dict] = None) -> np.ndarray:
        """Apply comprehensive industrial-grade filtering pipeline"""
        if len(data) < self.filter_order * 3:
            return data
        
        start_time = time.time()
        
        try:
            # Default filter configuration
            if filter_config is None:
                filter_config = {
                    "bandpass": {"low": 0.5, "high": 50.0},
                    "notch": self.notch_frequencies,
                    "smoothing": True,
                    "detrend": True
                }
            
            filtered_data = data.copy()
            
            # 1. Remove DC offset and linear trends
            if filter_config.get("detrend", True):
                filtered_data = signal.detrend(filtered_data, type='linear')
            
            # 2. Apply bandpass filter
            if "bandpass" in filter_config:
                bp_config = filter_config["bandpass"]
                filtered_data = self._apply_bandpass_filter(
                    filtered_data, 
                    bp_config.get("low", 0.5), 
                    bp_config.get("high", 50.0)
                )
            
            # 3. Apply notch filters for power line interference
            if "notch" in filter_config:
                for notch_freq in filter_config["notch"]:
                    filtered_data = self._apply_notch_filter(filtered_data, notch_freq)
            
            # 4. Apply smoothing filter if requested
            if filter_config.get("smoothing", False):
                window_size = min(5, len(filtered_data) // 10)
                if window_size >= 3:
                    filtered_data = signal.savgol_filter(filtered_data, window_size, 2)
            
            # Update performance stats
            processing_time = (time.time() - start_time) * 1000
            self.processing_stats["processing_time_ms"].append(processing_time)
            self.processing_stats["filters_applied"] += 1
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Industrial filtering failed: {e}")
            return data
    
    def _apply_bandpass_filter(self, data: np.ndarray, low_freq: float, high_freq: float) -> np.ndarray:
        """Apply bandpass filter with improved stability"""
        nyquist = self.sampling_rate / 2
        low = max(0.01, low_freq / nyquist)  # Prevent numerical issues
        high = min(0.99, high_freq / nyquist)
        
        if low >= high:
            logger.warning(f"Invalid filter frequencies: {low_freq}-{high_freq} Hz")
            return data
        
        # Use higher order filter for better frequency response
        sos = signal.butter(self.filter_order, [low, high], btype='band', output='sos')
        filtered_data = signal.sosfiltfilt(sos, data)
        
        return filtered_data
    
    def _apply_notch_filter(self, data: np.ndarray, notch_freq: float, Q: float = 30.0) -> np.ndarray:
        """Apply notch filter for power line interference removal"""
        nyquist = self.sampling_rate / 2
        
        if notch_freq >= nyquist:
            return data
            
        # Design notch filter
        w0 = notch_freq / nyquist
        b, a = signal.iirnotch(w0, Q)
        
        # Apply filter
        filtered_data = signal.filtfilt(b, a, data)
        
        return filtered_data
    
    def _calculate_signal_quality(self, samples: List[float]) -> float:
        """Calculate signal quality score (0-1, higher is better)"""
        if len(samples) < 3:
            return 0.0
        
        samples_array = np.array(samples)
        
        # Quality metrics
        quality_factors = []
        
        # 1. Amplitude stability (penalize excessive variation)
        amplitude_stability = 1.0 / (1.0 + np.std(samples_array) / 50.0)
        quality_factors.append(amplitude_stability)
        
        # 2. Gradient continuity (penalize sharp transitions)
        if len(samples) > 1:
            gradients = np.diff(samples_array)
            gradient_stability = 1.0 / (1.0 + np.std(gradients) / 20.0)
            quality_factors.append(gradient_stability)
        
        # 3. Finite value check
        finite_ratio = np.sum(np.isfinite(samples_array)) / len(samples_array)
        quality_factors.append(finite_ratio)
        
        # 4. Reasonable amplitude range
        max_amplitude = np.max(np.abs(samples_array))
        amplitude_reasonableness = 1.0 if max_amplitude < 200.0 else max(0.1, 200.0 / max_amplitude)
        quality_factors.append(amplitude_reasonableness)
        
        # Combined quality score
        quality_score = np.mean(quality_factors)
        
        return float(np.clip(quality_score, 0.0, 1.0))
    
    def _synchronize_channel_data(self, channel_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """Synchronize timestamps across multiple channels"""
        if len(channel_data) < 2:
            return channel_data
        
        # Find common time range
        start_times = []
        end_times = []
        
        for data in channel_data.values():
            if data["timestamps"]:
                start_times.append(data["timestamps"][0])
                end_times.append(data["timestamps"][-1])
        
        if not start_times:
            return channel_data
        
        common_start = max(start_times)
        common_end = min(end_times)
        
        if common_start >= common_end:
            logger.warning("No overlapping time range for synchronization")
            return channel_data
        
        # Trim data to common time range
        synchronized_data = {}
        
        for channel, data in channel_data.items():
            timestamps = np.array(data["timestamps"])
            signal_data = data["data"]
            
            # Find indices within common time range
            valid_indices = (timestamps >= common_start) & (timestamps <= common_end)
            
            if np.any(valid_indices):
                synchronized_data[channel] = {
                    **data,
                    "data": signal_data[valid_indices] if len(signal_data) == len(timestamps) else signal_data,
                    "timestamps": timestamps[valid_indices].tolist(),
                    "synchronized": True,
                    "sync_duration": common_end - common_start
                }
            else:
                synchronized_data[channel] = data
        
        return synchronized_data
    
    def extract_advanced_frequency_analysis(self, data: np.ndarray, 
                                           window_type: str = "hanning") -> Dict[str, Any]:
        """Extract comprehensive frequency domain features"""
        if len(data) < self.sampling_rate // 2:
            return self._empty_frequency_analysis()
        
        try:
            # Apply windowing for better spectral analysis
            if ADVANCED_WINDOWS_AVAILABLE and hasattr(windows, window_type):
                window = getattr(windows, window_type)(len(data))
                windowed_data = data * window
            else:
                windowed_data = data * np.hanning(len(data))
            
            # Compute power spectral density
            freqs, psd = signal.welch(
                windowed_data, 
                fs=self.sampling_rate,
                nperseg=min(len(data), self.sampling_rate * 2),
                noverlap=None,
                window=window_type if ADVANCED_WINDOWS_AVAILABLE else 'hann'
            )
            
            # Extract band powers and sub-band analysis
            band_analysis = {}
            total_power = np.sum(psd)
            
            for band_name, band_info in self.frequency_bands.items():
                low_freq, high_freq = band_info["range"]
                
                # Main band power
                band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                band_power = np.sum(psd[band_mask])
                relative_power = band_power / total_power if total_power > 0 else 0
                
                # Peak frequency in band
                if np.sum(band_mask) > 0:
                    band_freqs = freqs[band_mask]
                    band_psd = psd[band_mask]
                    peak_idx = np.argmax(band_psd)
                    peak_frequency = band_freqs[peak_idx]
                    peak_power = band_psd[peak_idx]
                else:
                    peak_frequency = (low_freq + high_freq) / 2
                    peak_power = 0.0
                
                # Sub-band analysis
                sub_band_powers = {}
                for sub_name, (sub_low, sub_high) in band_info["sub_bands"].items():
                    sub_mask = (freqs >= sub_low) & (freqs <= sub_high)
                    sub_power = np.sum(psd[sub_mask])
                    sub_band_powers[sub_name] = {
                        "power": float(sub_power),
                        "relative_power": float(sub_power / band_power) if band_power > 0 else 0.0
                    }
                
                band_analysis[band_name] = {
                    "power": float(band_power),
                    "relative_power": float(relative_power),
                    "peak_frequency": float(peak_frequency),
                    "peak_power": float(peak_power),
                    "frequency_range": [low_freq, high_freq],
                    "sub_bands": sub_band_powers
                }
            
            # Advanced spectral features
            spectral_features = self._calculate_spectral_features(freqs, psd)
            
            # Frequency ratios (commonly used in EEG analysis)
            frequency_ratios = {
                "theta_alpha": band_analysis["theta"]["power"] / max(band_analysis["alpha"]["power"], 1e-10),
                "alpha_beta": band_analysis["alpha"]["power"] / max(band_analysis["beta"]["power"], 1e-10),
                "theta_beta": band_analysis["theta"]["power"] / max(band_analysis["beta"]["power"], 1e-10),
                "low_high": (band_analysis["delta"]["power"] + band_analysis["theta"]["power"]) / 
                           max(band_analysis["beta"]["power"] + band_analysis["gamma"]["power"], 1e-10)
            }
            
            return {
                "band_powers": band_analysis,
                "spectral_features": spectral_features,
                "frequency_ratios": frequency_ratios,
                "total_power": float(total_power),
                "dominant_frequency": float(freqs[np.argmax(psd)]),
                "spectral_edge_frequency": self._calculate_spectral_edge(freqs, psd),
                "frequency_resolution": float(freqs[1] - freqs[0]),
                "analysis_parameters": {
                    "window_type": window_type,
                    "data_length": len(data),
                    "sampling_rate": self.sampling_rate
                }
            }
            
        except Exception as e:
            logger.error(f"Frequency analysis failed: {e}")
            return self._empty_frequency_analysis()
    
    def _calculate_spectral_features(self, freqs: np.ndarray, psd: np.ndarray) -> Dict[str, float]:
        """Calculate advanced spectral features"""
        features = {}
        
        # Spectral centroid (center of mass of spectrum)
        features["spectral_centroid"] = float(np.sum(freqs * psd) / np.sum(psd))
        
        # Spectral spread (bandwidth)
        centroid = features["spectral_centroid"]
        features["spectral_spread"] = float(np.sqrt(np.sum(((freqs - centroid) ** 2) * psd) / np.sum(psd)))
        
        # Spectral skewness
        features["spectral_skewness"] = float(skew(psd))
        
        # Spectral kurtosis
        features["spectral_kurtosis"] = float(kurtosis(psd))
        
        # Spectral entropy
        normalized_psd = psd / np.sum(psd)
        features["spectral_entropy"] = float(-np.sum(normalized_psd * np.log2(normalized_psd + 1e-12)))
        
        # Spectral flux (change in spectrum)
        if len(psd) > 1:
            spectral_diff = np.diff(psd)
            features["spectral_flux"] = float(np.sum(spectral_diff ** 2))
        else:
            features["spectral_flux"] = 0.0
        
        return features
    
    def _calculate_spectral_edge(self, freqs: np.ndarray, psd: np.ndarray, 
                                percentage: float = 0.95) -> float:
        """Calculate spectral edge frequency (frequency below which X% of power lies)"""
        cumulative_power = np.cumsum(psd)
        total_power = cumulative_power[-1]
        
        if total_power == 0:
            return 0.0
        
        normalized_cumulative = cumulative_power / total_power
        edge_idx = np.argmax(normalized_cumulative >= percentage)
        
        return float(freqs[edge_idx])
    
    def _empty_frequency_analysis(self) -> Dict[str, Any]:
        """Return empty frequency analysis structure"""
        empty_bands = {}
        for band_name, band_info in self.frequency_bands.items():
            empty_sub_bands = {}
            for sub_name in band_info["sub_bands"].keys():
                empty_sub_bands[sub_name] = {"power": 0.0, "relative_power": 0.0}
            
            empty_bands[band_name] = {
                "power": 0.0,
                "relative_power": 0.0,
                "peak_frequency": (band_info["range"][0] + band_info["range"][1]) / 2,
                "peak_power": 0.0,
                "frequency_range": list(band_info["range"]),
                "sub_bands": empty_sub_bands
            }
        
        return {
            "band_powers": empty_bands,
            "spectral_features": {
                "spectral_centroid": 0.0,
                "spectral_spread": 0.0,
                "spectral_skewness": 0.0,
                "spectral_kurtosis": 0.0,
                "spectral_entropy": 0.0,
                "spectral_flux": 0.0
            },
            "frequency_ratios": {
                "theta_alpha": 0.0,
                "alpha_beta": 0.0,
                "theta_beta": 0.0,
                "low_high": 0.0
            },
            "total_power": 0.0,
            "dominant_frequency": 0.0,
            "spectral_edge_frequency": 0.0,
            "frequency_resolution": 0.0,
            "analysis_parameters": {
                "window_type": "none",
                "data_length": 0,
                "sampling_rate": self.sampling_rate
            }
        }
    
    def detect_advanced_artifacts(self, data: np.ndarray, channel: str = "unknown") -> Dict[str, Any]:
        """Advanced artifact detection using multiple algorithms"""
        if len(data) == 0:
            return self._empty_artifact_report()
        
        artifacts = {
            "high_amplitude": False,
            "flat_line": False,
            "high_frequency_noise": False,
            "eye_blink": False,
            "muscle_artifact": False,
            "electrode_pop": False,
            "drift": False,
            "saturation": False
        }
        
        artifact_scores = {}
        artifact_details = {}
        
        try:
            # 1. Amplitude-based artifacts
            max_amplitude = np.max(np.abs(data))
            amplitude_threshold = self.artifact_thresholds["amplitude_threshold"]
            
            if max_amplitude > amplitude_threshold:
                artifacts["high_amplitude"] = True
                artifact_scores["high_amplitude"] = float(max_amplitude / amplitude_threshold)
                artifact_details["high_amplitude"] = {
                    "max_amplitude": float(max_amplitude),
                    "threshold": amplitude_threshold,
                    "samples_above_threshold": int(np.sum(np.abs(data) > amplitude_threshold))
                }
            
            # 2. Flat line detection (electrode disconnection)
            data_std = np.std(data)
            if data_std < 1.0:
                artifacts["flat_line"] = True
                artifact_scores["flat_line"] = float(1.0 / max(data_std, 0.001))
                artifact_details["flat_line"] = {
                    "std_deviation": float(data_std),
                    "threshold": 1.0
                }
            
            # 3. High frequency noise (EMG, electrical interference)
            if len(data) > self.filter_order * 3:
                high_freq_filtered = self._apply_bandpass_filter(data, 50.0, 100.0)
                noise_std = np.std(high_freq_filtered)
                
                if noise_std > 10.0:
                    artifacts["high_frequency_noise"] = True
                    artifact_scores["high_frequency_noise"] = float(noise_std / 10.0)
                    artifact_details["high_frequency_noise"] = {
                        "noise_std": float(noise_std),
                        "threshold": 10.0,
                        "frequency_range": [50.0, 100.0]
                    }
            
            # 4. Eye blink detection (low frequency, high amplitude)
            if len(data) > self.sampling_rate:
                low_freq_filtered = self._apply_bandpass_filter(data, 0.5, 4.0)
                blink_candidates = np.abs(low_freq_filtered) > 50.0
                
                if np.sum(blink_candidates) > len(data) * 0.01:  # More than 1% of samples
                    artifacts["eye_blink"] = True
                    artifact_scores["eye_blink"] = float(np.sum(blink_candidates) / len(data))
                    artifact_details["eye_blink"] = {
                        "affected_samples": int(np.sum(blink_candidates)),
                        "percentage": float(np.sum(blink_candidates) / len(data) * 100),
                        "threshold": 50.0
                    }
            
            # 5. Muscle artifact detection (high frequency, sustained)
            if len(data) > self.sampling_rate:
                emg_filtered = self._apply_bandpass_filter(data, 20.0, 45.0)
                emg_power = np.mean(emg_filtered ** 2)
                
                if emg_power > 100.0:
                    artifacts["muscle_artifact"] = True
                    artifact_scores["muscle_artifact"] = float(emg_power / 100.0)
                    artifact_details["muscle_artifact"] = {
                        "emg_power": float(emg_power),
                        "threshold": 100.0,
                        "frequency_range": [20.0, 45.0]
                    }
            
            # 6. Electrode pop detection (sudden amplitude changes)
            if len(data) > 1:
                gradients = np.abs(np.diff(data))
                max_gradient = np.max(gradients)
                gradient_threshold = self.artifact_thresholds["gradient_threshold"]
                
                if max_gradient > gradient_threshold:
                    artifacts["electrode_pop"] = True
                    artifact_scores["electrode_pop"] = float(max_gradient / gradient_threshold)
                    artifact_details["electrode_pop"] = {
                        "max_gradient": float(max_gradient),
                        "threshold": gradient_threshold,
                        "sharp_transitions": int(np.sum(gradients > gradient_threshold))
                    }
            
            # 7. Drift detection (low frequency trend)
            if len(data) > self.sampling_rate * 2:
                detrended = signal.detrend(data, type='linear')
                trend_strength = np.std(data) / max(np.std(detrended), 0.001)
                
                if trend_strength > 2.0:
                    artifacts["drift"] = True
                    artifact_scores["drift"] = float(trend_strength / 2.0)
                    artifact_details["drift"] = {
                        "trend_strength": float(trend_strength),
                        "threshold": 2.0
                    }
            
            # 8. Saturation detection (clipping)
            amplitude_range = np.max(data) - np.min(data)
            unique_values = len(np.unique(data))
            
            if amplitude_range > 400.0 and unique_values < len(data) * 0.8:
                artifacts["saturation"] = True
                artifact_scores["saturation"] = float(amplitude_range / 400.0)
                artifact_details["saturation"] = {
                    "amplitude_range": float(amplitude_range),
                    "unique_values": unique_values,
                    "total_samples": len(data)
                }
            
            # Calculate overall artifact severity
            artifact_count = sum(artifacts.values())
            max_score = max(artifact_scores.values()) if artifact_scores else 0.0
            
            # Update processing stats
            if artifact_count > 0:
                self.processing_stats["artifacts_detected"] += artifact_count
            
            return {
                "artifacts_detected": artifacts,
                "artifact_scores": artifact_scores,
                "artifact_details": artifact_details,
                "summary": {
                    "total_artifacts": artifact_count,
                    "max_severity_score": float(max_score),
                    "overall_quality": "poor" if artifact_count > 3 else "fair" if artifact_count > 1 else "good",
                    "channel": channel,
                    "data_length": len(data),
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Artifact detection failed for channel {channel}: {e}")
            return self._empty_artifact_report()
    
    def apply_ica_artifact_removal(self, multi_channel_data: Dict[str, np.ndarray], 
                                  n_components: Optional[int] = None) -> Dict[str, Any]:
        """Apply Independent Component Analysis for artifact removal"""
        if not ICA_AVAILABLE:
            logger.warning("ICA not available - sklearn not installed")
            return {
                "success": False,
                "message": "ICA functionality requires scikit-learn",
                "cleaned_data": multi_channel_data
            }
        
        if len(multi_channel_data) < 2:
            logger.warning("ICA requires at least 2 channels")
            return {
                "success": False, 
                "message": "ICA requires at least 2 channels",
                "cleaned_data": multi_channel_data
            }
        
        try:
            # Prepare data matrix (channels x samples)
            channel_names = list(multi_channel_data.keys())
            min_length = min(len(data) for data in multi_channel_data.values())
            
            if min_length < self.ica_buffer_required:
                logger.warning(f"Insufficient data for ICA: {min_length} < {self.ica_buffer_required}")
                return {
                    "success": False,
                    "message": f"Need at least {self.ica_buffer_required} samples for ICA",
                    "cleaned_data": multi_channel_data
                }
            
            # Create data matrix
            data_matrix = np.array([
                multi_channel_data[channel][:min_length] 
                for channel in channel_names
            ])
            
            # Standardize data
            scaler = StandardScaler()
            standardized_data = scaler.fit_transform(data_matrix.T).T
            
            # Apply ICA
            if n_components is None:
                n_components = min(len(channel_names), data_matrix.shape[1] // 100)
            
            ica = FastICA(n_components=n_components, random_state=42, max_iter=1000)
            ica_components = ica.fit_transform(standardized_data.T).T
            
            # Identify artifact components (simple heuristic)
            artifact_components = []
            
            for i, component in enumerate(ica_components):
                # High amplitude components likely artifacts
                if np.std(component) > 2.0:
                    artifact_components.append(i)
                
                # High frequency components likely muscle artifacts
                if len(component) > self.sampling_rate:
                    freq_analysis = self.extract_advanced_frequency_analysis(component)
                    if freq_analysis["spectral_features"]["spectral_centroid"] > 25.0:
                        artifact_components.append(i)
            
            # Remove artifact components
            cleaned_components = ica_components.copy()
            for artifact_idx in artifact_components:
                cleaned_components[artifact_idx] = 0
            
            # Reconstruct cleaned data
            cleaned_standardized = ica.inverse_transform(cleaned_components.T).T
            cleaned_data_matrix = scaler.inverse_transform(cleaned_standardized.T).T
            
            # Convert back to channel dictionary
            cleaned_data = {}
            for i, channel in enumerate(channel_names):
                cleaned_data[channel] = cleaned_data_matrix[i]
            
            # Update processing stats
            self.processing_stats["ica_components_removed"] += len(artifact_components)
            
            return {
                "success": True,
                "cleaned_data": cleaned_data,
                "ica_info": {
                    "n_components": n_components,
                    "artifact_components_removed": artifact_components,
                    "channels_processed": channel_names,
                    "data_length": min_length,
                    "processing_timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"ICA artifact removal failed: {e}")
            return {
                "success": False,
                "message": f"ICA processing error: {str(e)}",
                "cleaned_data": multi_channel_data
            }
    
    def _empty_artifact_report(self) -> Dict[str, Any]:
        """Return empty artifact detection report"""
        return {
            "artifacts_detected": {
                "high_amplitude": False,
                "flat_line": False,
                "high_frequency_noise": False,
                "eye_blink": False,
                "muscle_artifact": False,
                "electrode_pop": False,
                "drift": False,
                "saturation": False
            },
            "artifact_scores": {},
            "artifact_details": {},
            "summary": {
                "total_artifacts": 0,
                "max_severity_score": 0.0,
                "overall_quality": "unknown",
                "channel": "unknown",
                "data_length": 0,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    
    def get_comprehensive_channel_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all active EEG channels"""
        status = {
            "channels": {},
            "summary": {},
            "processor": {}
        }
        
        total_quality_scores = []
        total_artifacts = 0
        
        for channel in self.active_channels:
            channel_data_info = self.get_channel_data(channel, 4.0, apply_filters=False)
            data = channel_data_info["data"]
            
            if len(data) > 0:
                # Frequency analysis
                freq_analysis = self.extract_advanced_frequency_analysis(data)
                
                # Artifact detection
                artifact_analysis = self.detect_advanced_artifacts(data, channel)
                
                # Signal quality assessment
                quality_scores = channel_data_info.get("quality_scores", [])
                avg_quality = np.mean(quality_scores) if quality_scores else 0.0
                total_quality_scores.append(avg_quality)
                
                # Count artifacts
                channel_artifacts = sum(artifact_analysis["artifacts_detected"].values())
                total_artifacts += channel_artifacts
                
                status["channels"][channel] = {
                    "signal_info": {
                        "samples_available": len(self.signal_buffers[channel]),
                        "buffer_duration": channel_data_info["duration"],
                        "sampling_rate": self.sampling_rate,
                        "amplitude_range": [float(np.min(data)), float(np.max(data))],
                        "signal_std": float(np.std(data)),
                        "signal_mean": float(np.mean(data))
                    },
                    "quality_assessment": {
                        "overall_score": float(avg_quality),
                        "quality_rating": self._rate_signal_quality(avg_quality, channel_artifacts),
                        "recent_quality_trend": self._calculate_quality_trend(quality_scores)
                    },
                    "frequency_analysis": freq_analysis,
                    "artifact_analysis": artifact_analysis,
                    "timestamps": {
                        "first_sample": channel_data_info["timestamps"][0] if channel_data_info["timestamps"] else None,
                        "last_sample": channel_data_info["timestamps"][-1] if channel_data_info["timestamps"] else None,
                        "last_update": datetime.now(timezone.utc).isoformat()
                    }
                }
            else:
                status["channels"][channel] = {
                    "signal_info": {
                        "samples_available": 0,
                        "buffer_duration": 0.0,
                        "sampling_rate": self.sampling_rate,
                        "amplitude_range": [0.0, 0.0],
                        "signal_std": 0.0,
                        "signal_mean": 0.0
                    },
                    "quality_assessment": {
                        "overall_score": 0.0,
                        "quality_rating": "no_data",
                        "recent_quality_trend": "unknown"
                    },
                    "frequency_analysis": self._empty_frequency_analysis(),
                    "artifact_analysis": self._empty_artifact_report(),
                    "timestamps": {
                        "first_sample": None,
                        "last_sample": None,
                        "last_update": datetime.now(timezone.utc).isoformat()
                    }
                }
        
        # Summary statistics
        status["summary"] = {
            "total_active_channels": len(self.active_channels),
            "average_quality_score": float(np.mean(total_quality_scores)) if total_quality_scores else 0.0,
            "total_artifacts_detected": total_artifacts,
            "overall_system_quality": self._assess_overall_quality(total_quality_scores, total_artifacts),
            "data_collection_rate": self._calculate_data_rate(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Processor status
        status["processor"] = self.get_industrial_metrics()
        
        return status
    
    def get_industrial_metrics(self) -> Dict[str, Any]:
        """Get comprehensive industrial-grade processing metrics"""
        with self.processing_lock:
            # Calculate performance metrics
            avg_processing_time = (
                np.mean(list(self.processing_stats["processing_time_ms"])) 
                if self.processing_stats["processing_time_ms"] 
                else 0.0
            )
            
            total_samples = sum(len(buffer) for buffer in self.signal_buffers.values())
            max_buffer_fill = (
                max(len(buffer) / self.buffer_size for buffer in self.signal_buffers.values()) 
                if self.signal_buffers else 0.0
            )
            
            return {
                "processor_id": self.processor_id,
                "status": "active" if self.active_channels else "idle",
                "configuration": {
                    "sampling_rate": self.sampling_rate,
                    "max_channels": self.max_channels,
                    "buffer_duration": self.buffer_duration,
                    "filter_order": self.filter_order,
                    "ica_available": ICA_AVAILABLE,
                    "advanced_windows_available": ADVANCED_WINDOWS_AVAILABLE
                },
                "channel_management": {
                    "total_channels_available": len(self.available_channels),
                    "active_channels": len(self.active_channels),
                    "active_channel_list": list(self.active_channels),
                    "channel_utilization": len(self.active_channels) / self.max_channels
                },
                "buffer_status": {
                    "total_samples_buffered": total_samples,
                    "max_buffer_fill_percentage": float(max_buffer_fill * 100),
                    "buffer_memory_usage_mb": self._estimate_buffer_memory_usage()
                },
                "performance_metrics": {
                    "samples_processed": self.processing_stats["samples_processed"],
                    "average_processing_time_ms": float(avg_processing_time),
                    "filters_applied": self.processing_stats["filters_applied"],
                    "artifacts_detected": self.processing_stats["artifacts_detected"],
                    "ica_components_removed": self.processing_stats["ica_components_removed"],
                    "processing_efficiency": self._calculate_processing_efficiency()
                },
                "system_health": {
                    "memory_efficiency": self._assess_memory_efficiency(),
                    "processing_stability": self._assess_processing_stability(),
                    "data_integrity": self._assess_data_integrity(),
                    "overall_health_score": self._calculate_overall_health_score()
                },
                "timestamps": {
                    "processor_start": self.processing_stats["last_update"].isoformat(),
                    "last_update": datetime.now(timezone.utc).isoformat(),
                    "uptime_seconds": (datetime.now(timezone.utc) - self.processing_stats["last_update"]).total_seconds()
                }
            }
    
    def _rate_signal_quality(self, quality_score: float, artifact_count: int) -> str:
        """Rate signal quality based on score and artifacts"""
        if quality_score > 0.8 and artifact_count == 0:
            return "excellent"
        elif quality_score > 0.6 and artifact_count <= 1:
            return "good"
        elif quality_score > 0.4 and artifact_count <= 2:
            return "fair"
        elif quality_score > 0.2:
            return "poor"
        else:
            return "very_poor"
    
    def _calculate_quality_trend(self, quality_scores: List[float]) -> str:
        """Calculate quality trend from recent scores"""
        if len(quality_scores) < 3:
            return "insufficient_data"
        
        recent_scores = quality_scores[-5:]  # Last 5 scores
        if len(recent_scores) < 3:
            return "insufficient_data"
        
        # Simple linear trend
        x = np.arange(len(recent_scores))
        coeffs = np.polyfit(x, recent_scores, 1)
        slope = coeffs[0]
        
        if slope > 0.05:
            return "improving"
        elif slope < -0.05:
            return "degrading"
        else:
            return "stable"
    
    def _assess_overall_quality(self, quality_scores: List[float], total_artifacts: int) -> str:
        """Assess overall system quality"""
        if not quality_scores:
            return "no_data"
        
        avg_quality = np.mean(quality_scores)
        artifact_ratio = total_artifacts / len(quality_scores) if quality_scores else 0
        
        if avg_quality > 0.8 and artifact_ratio < 0.1:
            return "excellent"
        elif avg_quality > 0.6 and artifact_ratio < 0.2:
            return "good"
        elif avg_quality > 0.4 and artifact_ratio < 0.5:
            return "acceptable"
        else:
            return "poor"
    
    def _calculate_data_rate(self) -> float:
        """Calculate current data collection rate in samples/second"""
        if not self.active_channels:
            return 0.0
        
        # Estimate based on recent timestamps
        total_rate = 0.0
        active_count = 0
        
        for channel in self.active_channels:
            timestamps = list(self.timestamp_buffers[channel])
            if len(timestamps) > 1:
                duration = timestamps[-1] - timestamps[0]
                if duration > 0:
                    rate = len(timestamps) / duration
                    total_rate += rate
                    active_count += 1
        
        return total_rate / max(active_count, 1)
    
    def _estimate_buffer_memory_usage(self) -> float:
        """Estimate buffer memory usage in MB"""
        # Rough estimate: 8 bytes per float sample + overhead
        total_samples = sum(len(buffer) for buffer in self.signal_buffers.values())
        total_timestamps = sum(len(buffer) for buffer in self.timestamp_buffers.values())
        
        memory_bytes = (total_samples + total_timestamps) * 8  # 8 bytes per float
        memory_bytes += len(self.active_channels) * 1024  # Overhead per channel
        
        return memory_bytes / (1024 * 1024)  # Convert to MB
    
    def _calculate_processing_efficiency(self) -> float:
        """Calculate processing efficiency (0-1)"""
        if not self.processing_stats["processing_time_ms"]:
            return 1.0
        
        avg_time = np.mean(list(self.processing_stats["processing_time_ms"]))
        # Efficiency based on processing time (assume 1ms is optimal)
        efficiency = max(0.0, min(1.0, 1.0 / max(avg_time, 0.1)))
        
        return float(efficiency)
    
    def _assess_memory_efficiency(self) -> str:
        """Assess memory usage efficiency"""
        memory_mb = self._estimate_buffer_memory_usage()
        
        if memory_mb < 10:
            return "excellent"
        elif memory_mb < 50:
            return "good"
        elif memory_mb < 100:
            return "acceptable"
        else:
            return "high"
    
    def _assess_processing_stability(self) -> str:
        """Assess processing stability"""
        if len(self.processing_stats["processing_time_ms"]) < 10:
            return "insufficient_data"
        
        times = list(self.processing_stats["processing_time_ms"])
        cv = np.std(times) / max(np.mean(times), 0.001)  # Coefficient of variation
        
        if cv < 0.1:
            return "very_stable"
        elif cv < 0.3:
            return "stable"
        elif cv < 0.5:
            return "moderately_stable"
        else:
            return "unstable"
    
    def _assess_data_integrity(self) -> str:
        """Assess data integrity"""
        if not self.active_channels:
            return "no_data"
        
        # Check for consistent data flow
        empty_channels = 0
        for channel in self.active_channels:
            if len(self.signal_buffers[channel]) == 0:
                empty_channels += 1
        
        integrity_ratio = 1.0 - (empty_channels / len(self.active_channels))
        
        if integrity_ratio > 0.95:
            return "excellent"
        elif integrity_ratio > 0.8:
            return "good"
        elif integrity_ratio > 0.6:
            return "acceptable"
        else:
            return "poor"
    
    def _calculate_overall_health_score(self) -> float:
        """Calculate overall processor health score (0-1)"""
        scores = []
        
        # Efficiency score
        efficiency = self._calculate_processing_efficiency()
        scores.append(efficiency)
        
        # Memory usage score
        memory_mb = self._estimate_buffer_memory_usage()
        memory_score = max(0.0, 1.0 - (memory_mb / 200.0))  # Penalize high memory usage
        scores.append(memory_score)
        
        # Data integrity score
        integrity = self._assess_data_integrity()
        integrity_scores = {
            "excellent": 1.0, "good": 0.8, "acceptable": 0.6, 
            "poor": 0.3, "no_data": 0.0
        }
        scores.append(integrity_scores.get(integrity, 0.5))
        
        # Active channel utilization score
        utilization = len(self.active_channels) / max(self.max_channels, 1)
        utilization_score = min(1.0, utilization * 2)  # Favor moderate utilization
        scores.append(utilization_score)
        
        return float(np.mean(scores))

# Create backward compatibility alias
EEGProcessor = IndustrialEEGProcessor



