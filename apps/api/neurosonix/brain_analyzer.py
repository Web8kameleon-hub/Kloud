"""
Kloud Brain Wave Analyzer
Advanced analysis of brain wave patterns and cognitive states
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
from .eeg_processor import EEGProcessor

logger = logging.getLogger(__name__)


class BrainWaveAnalyzer:
    """Advanced brain wave pattern analysis"""
    
    def __init__(self, eeg_processor: EEGProcessor):
        self.eeg_processor = eeg_processor
        
        # Cognitive state thresholds (based on research)
        self.cognitive_states = {
            "relaxed": {"alpha": (8, 13), "beta": (13, 20), "alpha_dominance": True},
            "focused": {"beta": (13, 30), "gamma": (30, 50), "beta_dominance": True},
            "meditative": {"theta": (4, 8), "alpha": (8, 10), "theta_dominance": True},
            "stressed": {"beta": (20, 30), "gamma": (30, 100), "high_beta": True},
            "drowsy": {"delta": (0.5, 4), "theta": (4, 8), "delta_dominance": True}
        }
        
        logger.info("Brain Wave Analyzer initialized")
    
    def analyze_cognitive_state(self, channel_data: Dict[str, np.ndarray]) -> Dict:
        """Analyze current cognitive state from multi-channel EEG"""
        if not channel_data:
            return {"state": "no_data", "confidence": 0.0, "details": {}}
        
        # Calculate average band powers across channels
        all_band_powers = []
        for channel, data in channel_data.items():
            if len(data) > 0:
                band_powers = self.eeg_processor.extract_frequency_bands(data)
                all_band_powers.append(band_powers)
        
        if not all_band_powers:
            return {"state": "no_data", "confidence": 0.0, "details": {}}
        
        # Average band powers
        avg_bands = {}
        for band in ["delta", "theta", "alpha", "beta", "gamma"]:
            avg_bands[band] = np.mean([bp[band] for bp in all_band_powers])
        
        # Determine dominant cognitive state
        state_scores = {}
        
        for state_name, criteria in self.cognitive_states.items():
            score = 0.0
            
            if state_name == "relaxed":
                alpha_ratio = avg_bands["alpha"] / (avg_bands["beta"] + 1e-6)
                score = min(alpha_ratio / 2.0, 1.0)
            
            elif state_name == "focused":
                beta_ratio = avg_bands["beta"] / (avg_bands["alpha"] + 1e-6)
                gamma_boost = avg_bands["gamma"] / (np.mean(list(avg_bands.values())) + 1e-6)
                score = min((beta_ratio + gamma_boost) / 3.0, 1.0)
            
            elif state_name == "meditative":
                theta_alpha = (avg_bands["theta"] + avg_bands["alpha"]) / 2
                other_avg = (avg_bands["delta"] + avg_bands["beta"] + avg_bands["gamma"]) / 3
                score = min(theta_alpha / (other_avg + 1e-6) / 2.0, 1.0)
            
            elif state_name == "stressed":
                high_beta = avg_bands["beta"] > np.mean(list(avg_bands.values()))
                high_gamma = avg_bands["gamma"] > np.mean(list(avg_bands.values()))
                score = 0.8 if (high_beta and high_gamma) else 0.2
            
            elif state_name == "drowsy":
                delta_dominance = avg_bands["delta"] / (np.mean(list(avg_bands.values())) + 1e-6)
                score = min(delta_dominance / 2.0, 1.0)
            
            state_scores[state_name] = max(0.0, min(1.0, score))
        
        # Find dominant state
        dominant_state = max(state_scores.items(), key=lambda x: x[1])
        
        return {
            "state": dominant_state[0],
            "confidence": dominant_state[1],
            "all_scores": state_scores,
            "band_powers": avg_bands,
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_brain_symmetry(self, left_channels: List[str], right_channels: List[str]) -> Dict:
        """Calculate left-right brain hemisphere symmetry"""
        left_data = []
        right_data = []
        
        # Collect data from left hemisphere channels
        for channel in left_channels:
            data = self.eeg_processor.get_channel_data(channel, 2.0)
            if len(data) > 0:
                left_data.extend(data)
        
        # Collect data from right hemisphere channels  
        for channel in right_channels:
            data = self.eeg_processor.get_channel_data(channel, 2.0)
            if len(data) > 0:
                right_data.extend(data)
        
        if not left_data or not right_data:
            return {"symmetry_index": 0.5, "dominant_hemisphere": "unknown", "details": {}}
        
        left_power = np.mean([x**2 for x in left_data])
        right_power = np.mean([x**2 for x in right_data])
        
        # Symmetry index (0 = left dominant, 1 = right dominant, 0.5 = balanced)
        symmetry_index = right_power / (left_power + right_power + 1e-6)
        
        if symmetry_index < 0.45:
            dominant = "left"
        elif symmetry_index > 0.55:
            dominant = "right"
        else:
            dominant = "balanced"
        
        return {
            "symmetry_index": float(symmetry_index),
            "dominant_hemisphere": dominant,
            "left_power": float(left_power),
            "right_power": float(right_power),
            "timestamp": datetime.now().isoformat()
        }
    
    def detect_brain_events(self, channel_data: Dict[str, np.ndarray]) -> List[Dict]:
        """Detect significant brain events (spikes, bursts, etc.)"""
        events = []
        
        for channel, data in channel_data.items():
            if len(data) < 50:  # Need minimum data
                continue
            
            # Detect amplitude spikes
            threshold = np.std(data) * 3
            spikes = np.where(np.abs(data) > threshold)[0]
            
            if len(spikes) > 0:
                events.append({
                    "type": "amplitude_spike",
                    "channel": channel,
                    "count": len(spikes),
                    "max_amplitude": float(np.max(np.abs(data[spikes]))),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Detect frequency bursts
            band_powers = self.eeg_processor.extract_frequency_bands(data)
            
            for band, power in band_powers.items():
                if power > np.mean(list(band_powers.values())) * 2:
                    events.append({
                        "type": "frequency_burst",
                        "channel": channel,
                        "frequency_band": band,
                        "power": float(power),
                        "timestamp": datetime.now().isoformat()
                    })
        
        return events
    
    def get_brain_analysis_summary(self) -> Dict:
        """Get comprehensive brain analysis summary"""
        # Get data from all channels
        channel_data = {}
        for channel in self.eeg_processor.channels:
            data = self.eeg_processor.get_channel_data(channel, 4.0)
            if len(data) > 0:
                channel_data[channel] = data
        
        if not channel_data:
            return {
                "status": "no_data",
                "cognitive_state": {"state": "unknown", "confidence": 0.0},
                "brain_symmetry": {"symmetry_index": 0.5, "dominant_hemisphere": "unknown"},
                "events": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # Run analyses
        cognitive_state = self.analyze_cognitive_state(channel_data)
        
        # Define hemisphere channels
        left_channels = ["Fp1", "F3", "C3", "P3", "O1", "F7", "T3", "T5"]
        right_channels = ["Fp2", "F4", "C4", "P4", "O2", "F8", "T4", "T6"]
        
        brain_symmetry = self.calculate_brain_symmetry(left_channels, right_channels)
        events = self.detect_brain_events(channel_data)
        
        return {
            "status": "active",
            "channels_analyzed": len(channel_data),
            "cognitive_state": cognitive_state,
            "brain_symmetry": brain_symmetry,
            "events": events,
            "signal_quality": self._assess_overall_quality(channel_data),
            "timestamp": datetime.now().isoformat()
        }
    
    def _assess_overall_quality(self, channel_data: Dict[str, np.ndarray]) -> str:
        """Assess overall signal quality across all channels"""
        if not channel_data:
            return "no_data"
        
        quality_scores = []
        for channel, data in channel_data.items():
            artifacts = self.eeg_processor.detect_artifacts(data)
            artifact_count = sum(artifacts.values())
            quality_score = max(0, 1.0 - (artifact_count * 0.3))
            quality_scores.append(quality_score)
        
        avg_quality = np.mean(quality_scores)
        
        if avg_quality > 0.8:
            return "excellent"
        elif avg_quality > 0.6:
            return "good"
        elif avg_quality > 0.4:
            return "fair"
        else:
            return "poor"



