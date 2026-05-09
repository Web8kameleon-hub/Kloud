"""
Kloud Audio Synthesizer
----------------------------
Modern implementation of the Kloud audio synthesizer engine.

This module provides utilities for generating, mixing, and exporting
synthetic audio waveforms for use in cognitive simulation or
neural pattern sonification.

Author: Kloud Systems
"""

import numpy as np
from scipy.io.wavfile import write
from pathlib import Path
from typing import Literal, Optional


WaveType = Literal["sine", "square", "triangle", "sawtooth", "noise"]


class AudioSynthesizer:
    """
    Core class for Kloud audio synthesis.
    Supports basic waveform generation and export to WAV.
    """

    def __init__(self, sample_rate: int = 44100, amplitude: float = 0.5):
        self.sample_rate = sample_rate
        self.amplitude = amplitude

    def generate_wave(
        self,
        frequency: float,
        duration: float,
        wave_type: WaveType = "sine",
    ) -> np.ndarray:
        """Generate a single waveform array."""

        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)

        if wave_type == "sine":
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == "square":
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == "triangle":
            wave = 2 * np.abs(2 * ((t * frequency) % 1) - 1) - 1
        elif wave_type == "sawtooth":
            wave = 2 * ((t * frequency) % 1) - 1
        elif wave_type == "noise":
            wave = np.random.uniform(-1, 1, len(t))
        else:
            raise ValueError(f"Unsupported wave type: {wave_type}")

        return (self.amplitude * wave).astype(np.float32)

    def mix_waves(self, *waves: np.ndarray) -> np.ndarray:
        """Mix multiple wave arrays into a single normalized waveform."""
        if not waves:
            raise ValueError("No waves provided for mixing.")
        mix = np.sum(waves, axis=0)
        mix /= np.max(np.abs(mix)) + 1e-8
        return (self.amplitude * mix).astype(np.float32)

    def export_wave(
        self,
        wave: np.ndarray,
        output_path: str,
        normalize: bool = True,
        sample_rate: Optional[int] = None,
    ) -> Path:
        """Export waveform to a .wav file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        sr = sample_rate or self.sample_rate
        data = wave
        if normalize:
            data = (data / np.max(np.abs(data))) * 32767
        write(output_path, sr, data.astype(np.int16))
        return output_path

    def synthesize_pattern(
        self,
        pattern: list[tuple[float, float, WaveType]],
        output_path: Optional[str] = None,
    ) -> np.ndarray:
        """
        Generate a multi-tone pattern (sequence of waves).

        Example pattern:
        [
            (440, 0.5, "sine"),
            (880, 0.25, "square"),
            (660, 0.75, "triangle"),
        ]
        """
        segments = []
        for freq, dur, wtype in pattern:
            segments.append(self.generate_wave(freq, dur, wtype))

        combined = np.concatenate(segments)
        if output_path:
            self.export_wave(combined, output_path)
        return combined


# ðŸ”§ Shembull pÃ«rdorimi
if __name__ == "__main__":
    synth = AudioSynthesizer(sample_rate=44100, amplitude=0.4)

    pattern = [
        (440, 0.5, "sine"),
        (660, 0.5, "square"),
        (550, 0.5, "triangle"),
        (880, 0.5, "sawtooth"),
    ]

    wave = synth.synthesize_pattern(pattern, output_path="output/Kloud_demo.wav")

    print("ðŸŽ§ Generated:", len(wave), "samples")
    print("âœ… File saved to: output/Kloud_demo.wav")



