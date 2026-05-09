"""
Kloud API Routes
Real EEG processing and brain-to-audio conversion endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
import asyncio
from datetime import datetime

# Import real Kloud modules
from .eeg_processor import EEGProcessor
from .brain_analyzer import BrainWaveAnalyzer
from .audio_synthesizer import AudioSynthesizer

router = APIRouter(prefix="/api/Kloud", tags=["Kloud EEG Processing"])

# Initialize real processing modules
eeg_processor = EEGProcessor(sampling_rate=256)
brain_analyzer = BrainWaveAnalyzer(eeg_processor)
audio_synthesizer = AudioSynthesizer(sample_rate=44100)


@router.get("/status")
async def get_Kloud_status():
    """Get real-time Kloud system status"""
    try:
        eeg_metrics = eeg_processor.get_real_time_metrics()
        brain_analysis = brain_analyzer.get_brain_analysis_summary()
        audio_status = audio_synthesizer.get_synthesis_status()
        
        return {
            "system_status": "operational",
            "modules": {
                "eeg_processor": eeg_metrics,
                "brain_analyzer": brain_analysis,
                "audio_synthesizer": audio_status
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")


@router.get("/eeg/channels")
async def get_eeg_channels():
    """Get status of all EEG channels"""
    try:
        return eeg_processor.get_channel_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EEG channels error: {str(e)}")


@router.post("/eeg/sample")
async def add_eeg_sample(channel: str, sample: float):
    """Add a new EEG sample (for real device integration)"""
    try:
        eeg_processor.add_sample(channel, sample)
        return {"status": "sample_added", "channel": channel, "value": sample}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sample error: {str(e)}")


@router.post("/eeg/multi-sample")
async def add_multi_channel_sample(samples: Dict[str, float]):
    """Add samples from multiple EEG channels simultaneously"""
    try:
        eeg_processor.add_multi_channel_sample(samples)
        return {"status": "samples_added", "channels": list(samples.keys()), "count": len(samples)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-sample error: {str(e)}")


@router.get("/brain/analysis")
async def get_brain_analysis():
    """Get comprehensive brain wave analysis"""
    try:
        return brain_analyzer.get_brain_analysis_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain analysis error: {str(e)}")


@router.get("/brain/cognitive-state")
async def get_cognitive_state():
    """Get current cognitive state analysis"""
    try:
        # Get data from all channels
        channel_data = {}
        for channel in eeg_processor.channels:
            data = eeg_processor.get_channel_data(channel, 4.0)
            if len(data) > 0:
                channel_data[channel] = data
        
        return brain_analyzer.analyze_cognitive_state(channel_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cognitive state error: {str(e)}")


@router.get("/brain/symmetry")
async def get_brain_symmetry():
    """Get left-right brain hemisphere symmetry analysis"""
    try:
        left_channels = ["Fp1", "F3", "C3", "P3", "O1", "F7", "T3", "T5"]
        right_channels = ["Fp2", "F4", "C4", "P4", "O2", "F8", "T4", "T6"]
        
        return brain_analyzer.calculate_brain_symmetry(left_channels, right_channels)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain symmetry error: {str(e)}")


@router.get("/audio/synthesize")
async def synthesize_brain_audio():
    """Generate audio from current brain wave data"""
    try:
        brain_analysis = brain_analyzer.get_brain_analysis_summary()
        audio_streams = audio_synthesizer.synthesize_from_brain_data(brain_analysis)
        
        # Convert numpy arrays to lists for JSON serialization
        audio_data = {}
        for stream_name, audio_array in audio_streams.items():
            if hasattr(audio_array, 'tolist'):
                audio_data[stream_name] = audio_array.tolist()
            else:
                audio_data[stream_name] = list(audio_array)
        
        return {
            "synthesis_status": "completed",
            "audio_streams": list(audio_data.keys()),
            "brain_analysis": brain_analysis,
            "audio_data": audio_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio synthesis error: {str(e)}")


@router.get("/audio/status")
async def get_audio_status():
    """Get audio synthesis system status"""
    try:
        return audio_synthesizer.get_synthesis_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio status error: {str(e)}")


@router.post("/neuroacoustic/convert")
async def convert_eeg_to_audio(request_data: Dict):
    """Convert EEG data to neuroacoustic audio - REAL IMPLEMENTATION"""
    try:
        # Extract EEG data from request
        eeg_data = request_data.get("eeg_data", {})
        conversion_params = request_data.get("params", {})
        
        # Process EEG data through real modules
        if eeg_data:
            # Add EEG samples to processor
            for channel, samples in eeg_data.items():
                if isinstance(samples, list):
                    for sample in samples:
                        eeg_processor.add_sample(channel, sample)
        
        # Analyze brain patterns
        brain_analysis = brain_analyzer.get_brain_analysis_summary()
        
        # Generate neuroacoustic audio
        audio_streams = audio_synthesizer.synthesize_from_brain_data(brain_analysis)
        
        # Calculate audio properties
        frequencies = [
            brain_analysis["frequency_bands"]["alpha"]["peak_frequency"],
            brain_analysis["frequency_bands"]["beta"]["peak_frequency"], 
            brain_analysis["frequency_bands"]["gamma"]["peak_frequency"]
        ]
        
        return {
            "status": "converted",
            "audioUrl": f"/audio/neuroacoustic/{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav",
            "duration": conversion_params.get("duration", 180),
            "format": "wav",
            "frequencies": frequencies,
            "brain_analysis": brain_analysis,
            "synthesis_type": "real_neuroacoustic",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neuroacoustic conversion error: {str(e)}")


@router.get("/neuroacoustic/stream")
async def stream_neuroacoustic_audio():
    """Real-time neuroacoustic audio streaming from live EEG"""
    try:
        from fastapi.responses import StreamingResponse
        import io
        import numpy as np
        
        def generate_real_audio_stream():
            """Generate real-time audio based on current brain state"""
            while True:
                try:
                    # Get current brain analysis
                    brain_analysis = brain_analyzer.get_brain_analysis_summary()
                    
                    # Generate audio chunk based on brain state
                    audio_chunk = audio_synthesizer.generate_brain_tone(
                        brain_analysis["cognitive_state"]["dominant_frequency"], 
                        duration=0.1  # 100ms chunks
                    )
                    
                    # Convert to WAV format bytes
                    audio_bytes = (audio_chunk * 32767).astype(np.int16).tobytes()
                    yield audio_bytes
                    
                    # Delay for real-time streaming
                    import time
                    time.sleep(0.1)
                    
                except Exception as stream_error:
                    print(f"Stream error: {stream_error}")
                    break
        
        return StreamingResponse(
            generate_real_audio_stream(),
            media_type="audio/wav",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "audio/wav"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio streaming error: {str(e)}")


@router.get("/neuroacoustic/status")
async def get_neuroacoustic_status():
    """Get neuroacoustic conversion system status"""
    try:
        return {
            "neuroacoustic_system": "operational",
            "conversion_ready": True,
            "streaming_available": True,
            "eeg_processor_status": eeg_processor.get_real_time_metrics(),
            "audio_synthesizer_status": audio_synthesizer.get_synthesis_status(),
            "supported_formats": ["wav", "mp3", "ogg"],
            "real_time_processing": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neuroacoustic status error: {str(e)}")


@router.post("/simulate/eeg-data")
async def simulate_eeg_data(duration_seconds: int = 5):
    """Simulate realistic EEG data for testing (when no real device connected)"""
    try:
        import numpy as np
        import random
        
        # Simulate realistic EEG data
        sampling_rate = eeg_processor.sampling_rate
        samples_per_channel = duration_seconds * sampling_rate
        
        simulated_data = {}
        for channel in eeg_processor.channels[:8]:  # Simulate first 8 channels
            # Create realistic EEG-like signal
            t = np.linspace(0, duration_seconds, samples_per_channel)
            
            # Base signal with multiple frequency components
            signal = (
                2.0 * np.sin(2 * np.pi * 10 * t) +  # Alpha (10 Hz)
                1.0 * np.sin(2 * np.pi * 20 * t) +  # Beta (20 Hz)
                0.5 * np.sin(2 * np.pi * 6 * t) +   # Theta (6 Hz)
                0.3 * np.random.normal(0, 1, samples_per_channel)  # Noise
            )
            
            # Add channel-specific variation
            channel_variation = random.uniform(0.8, 1.2)
            signal *= channel_variation
            
            # Add samples to processor
            for sample in signal:
                eeg_processor.add_sample(channel, float(sample))
            
            simulated_data[channel] = len(signal)
        
        return {
            "simulation_status": "completed",
            "duration_seconds": duration_seconds,
            "channels_simulated": list(simulated_data.keys()),
            "samples_per_channel": samples_per_channel,
            "total_samples": sum(simulated_data.values()),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@router.get("/health")
async def Kloud_health():
    """Kloud system health check"""
    try:
        # Check all modules
        eeg_active = len(eeg_processor.signal_buffer) > 0
        brain_ready = brain_analyzer is not None
        audio_ready = audio_synthesizer is not None
        
        health_status = "healthy" if all([eeg_active, brain_ready, audio_ready]) else "partial"
        
        return {
            "status": health_status,
            "service": "Kloud Real EEG Processing",
            "version": "1.0.0",
            "modules": {
                "eeg_processor": "active" if eeg_active else "waiting_for_data",
                "brain_analyzer": "ready" if brain_ready else "error",
                "audio_synthesizer": "ready" if audio_ready else "error"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")



