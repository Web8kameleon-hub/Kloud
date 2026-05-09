"""
Kloud Signal Filter
Real-time signal filtering and noise reduction for EEG data
"""

import numpy as np
from scipy import signal
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SignalFilter:
    """Real-time EEG signal filtering and preprocessing"""
    
    def __init__(self, sampling_rate: int = 256):
        self.sampling_rate = sampling_rate
        self.nyquist_freq = sampling_rate / 2
        
        # Pre-designed filters
        self.filters = {}
        self._initialize_filters()
        
        logger.info(f"Signal Filter initialized with {sampling_rate}Hz sampling rate")
    
    def _initialize_filters(self):
        """Initialize commonly used filters"""
        try:
            # Bandpass filter (0.5-50 Hz) - Standard EEG range
            low_freq = 0.5 / self.nyquist_freq
            high_freq = 50.0 / self.nyquist_freq
            self.filters['eeg_bandpass'] = signal.butter(4, [low_freq, high_freq], btype='band')
            
            # Notch filter (50 Hz) - Power line interference
            notch_freq = 50.0 / self.nyquist_freq
            self.filters['notch_50hz'] = signal.iirnotch(notch_freq, 30)
            
            # High-pass filter (0.1 Hz) - DC removal
            highpass_freq = 0.1 / self.nyquist_freq
            self.filters['dc_removal'] = signal.butter(2, highpass_freq, btype='high')
            
        except Exception as e:
            logger.error(f"Filter initialization error: {e}")
    
    def apply_bandpass_filter(self, data: np.ndarray, low_freq: float = 0.5, 
                             high_freq: float = 50.0) -> np.ndarray:
        """Apply bandpass filter to remove noise outside EEG range"""
        if len(data) < 20:  # Need minimum samples for filtering
            return data
        
        try:
            low = low_freq / self.nyquist_freq
            high = high_freq / self.nyquist_freq
            
            b, a = signal.butter(4, [low, high], btype='band')
            filtered_data = signal.filtfilt(b, a, data)
            return filtered_data
        except Exception as e:
            logger.warning(f"Bandpass filter error: {e}")
            return data
    
    def remove_power_line_noise(self, data: np.ndarray, power_freq: float = 50.0) -> np.ndarray:
        """Remove power line interference (50Hz or 60Hz)"""
        if len(data) < 20:
            return data
        
        try:
            notch_freq = power_freq / self.nyquist_freq
            b, a = signal.iirnotch(notch_freq, 30)
            filtered_data = signal.filtfilt(b, a, data)
            return filtered_data
        except Exception as e:
            logger.warning(f"Notch filter error: {e}")
            return data
    
    def remove_baseline_drift(self, data: np.ndarray) -> np.ndarray:
        """Remove slow baseline drift using high-pass filter"""
        if len(data) < 20:
            return data
        
        try:
            highpass_freq = 0.1 / self.nyquist_freq
            b, a = signal.butter(2, highpass_freq, btype='high')
            filtered_data = signal.filtfilt(b, a, data)
            return filtered_data
        except Exception as e:
            logger.warning(f"Baseline removal error: {e}")
            return data
    
    def smooth_signal(self, data: np.ndarray, window_size: int = 5) -> np.ndarray:
        """Apply moving average smoothing"""
        if len(data) < window_size:
            return data
        
        kernel = np.ones(window_size) / window_size
        smoothed = np.convolve(data, kernel, mode='same')
        return smoothed
    
    def detect_and_remove_outliers(self, data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """Detect and interpolate outliers based on standard deviation"""
        if len(data) < 10:
            return data
        
        # Calculate outlier threshold
        mean_val = np.mean(data)
        std_val = np.std(data)
        outlier_threshold = threshold * std_val
        
        # Find outliers
        outlier_mask = np.abs(data - mean_val) > outlier_threshold
        
        if np.any(outlier_mask):
            # Replace outliers with interpolated values
            clean_data = data.copy()
            outlier_indices = np.where(outlier_mask)[0]
            
            for idx in outlier_indices:
                # Simple interpolation between neighbors
                if idx > 0 and idx < len(data) - 1:
                    clean_data[idx] = (data[idx-1] + data[idx+1]) / 2
                elif idx == 0:
                    clean_data[idx] = data[1] if len(data) > 1 else mean_val
                else:  # idx == len(data) - 1
                    clean_data[idx] = data[-2] if len(data) > 1 else mean_val
            
            return clean_data
        
        return data
    
    def apply_comprehensive_filter(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Apply comprehensive filtering pipeline"""
        if len(data) == 0:
            return {"original": data, "filtered": data}
        
        # Step-by-step filtering
        step1_baseline = self.remove_baseline_drift(data)
        step2_bandpass = self.apply_bandpass_filter(step1_baseline)
        step3_notch = self.remove_power_line_noise(step2_bandpass)
        step4_outliers = self.detect_and_remove_outliers(step3_notch)
        step5_smooth = self.smooth_signal(step4_outliers)
        
        return {
            "original": data,
            "baseline_removed": step1_baseline,
            "bandpass_filtered": step2_bandpass,
            "notch_filtered": step3_notch,
            "outliers_removed": step4_outliers,
            "final_filtered": step5_smooth
        }
    
    def get_filter_status(self) -> Dict:
        """Get current filter configuration status"""
        return {
            "sampling_rate": self.sampling_rate,
            "nyquist_frequency": self.nyquist_freq,
            "available_filters": list(self.filters.keys()),
            "default_bandpass": "0.5-50 Hz",
            "power_line_notch": "50 Hz",
            "outlier_threshold": "3 std deviations"
        }



