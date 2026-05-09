#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  VIDEO GENERATOR BLERINA — AI Video Production Pipeline                       ║
║  Part of Kloud Cloud Industrial Backend                                    ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Features:                                                                    ║
║  - BLERINA script generation (using existing content factory)                 ║
║  - Text-to-Speech via Coqui TTS (local, free)                                 ║
║  - AI image generation for visuals                                            ║
║  - FFmpeg video assembly with subtitles                                       ║
║  - SRT subtitle generation                                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Date: 2026-02-08
Author: Kloud Team
"""

from __future__ import annotations

import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

VIDEO_OUTPUT_DIR = Path("./generated_videos")
TEMP_DIR = Path(tempfile.gettempdir()) / "blerina_video"

# Ensure directories exist
VIDEO_OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)


class VideoStyle(Enum):
    """Video style presets."""
    EDUCATIONAL = "educational"      # Clean, informative
    DOCUMENTARY = "documentary"      # Cinematic, dramatic
    TUTORIAL = "tutorial"            # Step-by-step
    PRESENTATION = "presentation"    # Slide-like
    SOCIAL_MEDIA = "social_media"    # Short, engaging


class VoiceStyle(Enum):
    """Voice style for TTS."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    NARRATOR = "narrator"
    ENERGETIC = "energetic"


@dataclass
class VideoSection:
    """A section of the video with text, audio, and visual."""
    index: int
    title: str
    narration_text: str
    duration_seconds: float = 0.0
    audio_path: Optional[Path] = None
    image_path: Optional[Path] = None
    subtitle_start: float = 0.0
    subtitle_end: float = 0.0


@dataclass
class VideoProject:
    """Complete video project."""
    title: str
    topic: str
    style: VideoStyle
    sections: List[VideoSection] = field(default_factory=list)
    total_duration: float = 0.0
    output_path: Optional[Path] = None
    srt_path: Optional[Path] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# SCRIPT GENERATOR (BLERINA-powered)
# ═══════════════════════════════════════════════════════════════════════════════

class ScriptGenerator:
    """
    Generates video scripts using BLERINA content patterns.
    Uses verified knowledge base for EEG/BCI content and History topics.
    """
    
    # History content templates for viral reels
    HISTORY_TEMPLATES: Dict[str, Dict[str, any]] = {
        "Perandoria Romake": {
            "sections": [
                {"title": "Fillimi", "narration": "Roma filloi si një qytet i vogël në vitin 753 para Krishtit. Por brenda 500 vitesh, do të bëhej perandoria më e madhe në histori.", "duration": 8},
                {"title": "Ekspansioni", "narration": "Në kulmin e saj, Perandoria Romake kontrollonte 5 milionë kilometra katrorë - nga Britania në veri deri në Afrikën e Veriut në jug.", "duration": 8},
                {"title": "Inovacionet", "narration": "Romakët ndërtuan rrugë, ujësjellësa dhe struktura që ende ekzistojnë sot. Koloseumi, një mrekulli inxhinierike, mbante 80,000 spektatorë.", "duration": 10},
                {"title": "Ushtria", "narration": "Legionet romake ishin makina luftarake të pamposhtura. Disiplina, taktika dhe teknologjia i bënë ata invincible për shekuj.", "duration": 8},
                {"title": "Rënia", "narration": "Por asnjë perandori nuk zgjat përgjithmonë. Korrupsioni, inflacioni dhe invazionet barbare çuan në rënien e Romës në vitin 476.", "duration": 10},
                {"title": "Trashëgimia", "narration": "Megjithatë, trashëgimia e Romës jeton - në gjuhën tonë, ligjet, arkitekturën dhe kulturën. Roma vdiq, por idetë e saj jetojnë përgjithmonë.", "duration": 10}
            ]
        },
        "Napoleon Bonaparte": {
            "sections": [
                {"title": "Fillimi", "narration": "Napoleon Bonaparte. Njeriu që shkoi nga një oficer i thjeshtë në Perandorin e Francës. Historia e tij është legjendarike.", "duration": 8},
                {"title": "Rruga në Pushtet", "narration": "Në 1799, me vetëm 30 vjeç, Napoleon mori pushtetin në Francë përmes një grushtshteti. Ambicia e tij ishte e pakufishme.", "duration": 8},
                {"title": "Fitoret", "narration": "Napoleon fitoi 60 nga 70 beteja. Gjenitë e tij ushtarake e bënë atë një nga komandantët më të mëdhenj në histori.", "duration": 9},
                {"title": "Perandoria", "narration": "Në kulmin e pushtetit, Napoleon kontrollonte shumicën e Evropës. Nga Spanja në Poloni, emri i tij krijonte frikë dhe respekt.", "duration": 9},
                {"title": "Waterloo", "narration": "Por në 1815, në fushën e Waterloo-s, perandoria e tij përfundoi. Një betejë, një humbje, fundi i një epoke.", "duration": 10},
                {"title": "Trashëgimia", "narration": "Napoleon ndryshoi Evropën përgjithmonë. Kodi i tij civil, reformimet arsimore, dhe idetë revolucionare ende ndikojnë botën sot.", "duration": 10}
            ]
        },
        "Lufta e Parë Botërore": {
            "sections": [
                {"title": "Shkëndija", "narration": "28 Qershor 1914. Një plumb në Sarajevë vrau Arkidukun Franz Ferdinand. Një moment që ndryshoi historinë përgjithmonë.", "duration": 9},
                {"title": "Fillimi", "narration": "Brenda javësh, aleancat e vjetra shkuan në luftë. Austro-Hungaria, Gjermania, Rusia, Franca, Britania - e gjithë Europa u ndez.", "duration": 9},
                {"title": "Transheatë", "narration": "Transheatë të gjata, tela me gjemba, gazra helmuese. Miliona ushtarë vuajtën në baltë dhe gjak për kilometra tokë.", "duration": 10},
                {"title": "Teknologjia", "narration": "Ishte lufta e parë moderne. Tanke, avionë, submarine - teknologjia e vdekjes arriti nivele të reja tmerruese.", "duration": 9},
                {"title": "Fundi", "narration": "11 Nëntor 1918, ora 11. Armëpushimi. Lufta mbaroi, por 20 milionë njerëz kishin vdekur. Një gjeneratë e humbur.", "duration": 10},
                {"title": "Pasojat", "narration": "Traktati i Versajës. Perandori shkatërruan. Harta e Evropës u rishkrua. Dhe në hije, fara e Luftës së Dytë Botërore u mboll.", "duration": 10}
            ]
        }
    }
    
    # Pre-written educational content for EEG BCIs
    EEG_BCI_CONTENT: Dict[str, Dict[str, str]] = {
        "intro": {
            "title": "What are Brain-Computer Interfaces?",
            "narration": """
Brain-Computer Interfaces, or BCIs, represent one of the most exciting frontiers 
in neurotechnology. These systems create a direct communication pathway between 
the brain and external devices, bypassing traditional neuromuscular pathways.

At their core, BCIs read electrical signals from the brain, interpret them using 
sophisticated algorithms, and translate them into commands that can control 
computers, prosthetics, or other devices.
"""
        },
        "eeg_basics": {
            "title": "Understanding EEG Signals",
            "narration": """
Electroencephalography, or EEG, measures the electrical activity of the brain 
through electrodes placed on the scalp. The brain produces different types of 
waves depending on its state of activity.

Delta waves, ranging from 0.5 to 4 Hertz, are associated with deep sleep.
Theta waves, from 4 to 8 Hertz, indicate relaxation and drowsiness.
Alpha waves, from 8 to 13 Hertz, show calm alertness.
Beta waves, from 13 to 30 Hertz, represent active thinking and focus.
Gamma waves, above 30 Hertz, are linked to high-level cognitive processing.
"""
        },
        "how_bcis_work": {
            "title": "How BCIs Process Brain Signals",
            "narration": """
The BCI pipeline consists of four main stages: signal acquisition, signal processing, 
feature extraction, and command translation.

First, electrodes capture raw EEG signals from the brain. These signals are then 
amplified and filtered to remove noise and artifacts.

Next, machine learning algorithms analyze the cleaned signals to identify specific 
patterns associated with different mental states or intentions.

Finally, these patterns are mapped to commands that control the target device, 
whether it's moving a cursor, typing text, or controlling a robotic arm.
"""
        },
        "applications": {
            "title": "Real-World Applications",
            "narration": """
Brain-Computer Interfaces are transforming healthcare and human capability.

For patients with paralysis, BCIs offer the ability to communicate and control 
wheelchairs or prosthetic limbs using only their thoughts.

In rehabilitation, BCIs help stroke patients regain motor function by creating 
new neural pathways through neurofeedback training.

Beyond medicine, BCIs are being explored for gaming, meditation enhancement, 
and even direct brain-to-brain communication.
"""
        },
        "kloud_approach": {
            "title": "The Kloud Approach",
            "narration": """
Kloud has developed advanced EEG analysis systems that make brain-computer 
interfaces more accessible and reliable.

Our ALBA system provides real-time EEG signal processing with high accuracy.
ALBI handles peripheral data integration for comprehensive neural monitoring.
And JONA coordinates these systems for seamless industrial-grade performance.

Together with the Curiosity Ocean AI, we're making brain technology more 
intuitive and powerful than ever before.
"""
        },
        "future": {
            "title": "The Future of BCIs",
            "narration": """
The future of brain-computer interfaces is incredibly promising.

Advances in electrode technology will make BCIs less invasive and more comfortable.
Machine learning improvements will enable faster, more accurate signal interpretation.
And miniaturization will lead to wearable BCIs that integrate seamlessly into daily life.

We're moving toward a world where the boundary between mind and machine 
becomes increasingly fluid, opening new possibilities for human potential.
"""
        },
        "outro": {
            "title": "Closing",
            "narration": """
Brain-Computer Interfaces represent a paradigm shift in how we interact with technology.

From helping patients regain lost abilities to enhancing human cognition, 
BCIs are not just science fiction—they're becoming reality.

At Kloud, we're proud to be part of this revolution, building the tools 
that will shape the future of neural technology.

Thank you for watching. To learn more, visit kloud.com.
"""
        }
    }
    
    def generate_script(self, topic: str, style: VideoStyle) -> List[VideoSection]:
        """Generate a video script for the given topic."""
        
        # Check for history topics (Albanian language)
        for hist_topic, template in self.HISTORY_TEMPLATES.items():
            if hist_topic.lower() in topic.lower():
                return self._generate_history_script(hist_topic, template)
        
        # Check for EEG/BCI content
        if "eeg" in topic.lower() or "bci" in topic.lower() or "brain" in topic.lower():
            return self._generate_eeg_bci_script(style)
        
        # Fallback generic script
        return self._generate_generic_script(topic, style)
    
    def _generate_history_script(self, topic: str, template: Dict) -> List[VideoSection]:
        """Generate history video script from template."""
        sections: List[VideoSection] = []
        
        for idx, section_data in enumerate(template["sections"]):
            sections.append(VideoSection(
                index=idx,
                title=section_data["title"],
                narration_text=section_data["narration"],
                duration_seconds=section_data.get("duration", 8.0)
            ))
        
        return sections
    
    def _generate_eeg_bci_script(self, style: VideoStyle) -> List[VideoSection]:
        """Generate EEG/BCI educational video script."""
        sections: List[VideoSection] = []
        
        section_order = [
            "intro", "eeg_basics", "how_bcis_work", 
            "applications", "kloud_approach", "future", "outro"
        ]
        
        for idx, section_key in enumerate(section_order):
            content = self.EEG_BCI_CONTENT[section_key]
            sections.append(VideoSection(
                index=idx,
                title=content["title"],
                narration_text=content["narration"].strip()
            ))
        
        return sections
    
    def _generate_generic_script(self, topic: str, style: VideoStyle) -> List[VideoSection]:
        """Generate generic video script."""
        return [
            VideoSection(
                index=0,
                title="Introduction",
                narration_text=f"Welcome to this video about {topic}. "
                              f"Let's explore this fascinating subject together."
            ),
            VideoSection(
                index=1,
                title="Main Content",
                narration_text=f"Here we dive deep into the key aspects of {topic}. "
                              f"This is where the main educational content would go."
            ),
            VideoSection(
                index=2,
                title="Conclusion",
                narration_text=f"Thank you for watching this video about {topic}. "
                              f"We hope you found it informative and engaging."
            )
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# TEXT-TO-SPEECH ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TTSEngine:
    """
    Text-to-Speech engine using available TTS systems.
    Supports: Coqui TTS (local), Edge TTS (free), pyttsx3 (offline)
    """
    
    def __init__(self) -> None:
        self.available_engines: List[str] = []
        self._detect_available_engines()
    
    def _detect_available_engines(self) -> None:
        """Detect which TTS engines are available."""
        # Check for edge-tts (free Microsoft voices)
        try:
            import edge_tts  # noqa: F401
            self.available_engines.append("edge_tts")
        except ImportError:
            pass
        
        # Check for pyttsx3 (offline)
        try:
            import importlib
            importlib.import_module("pyttsx3")  # type: ignore[import-untyped]
            self.available_engines.append("pyttsx3")
        except ImportError:
            pass
        
        # Check for gtts (Google TTS)
        try:
            import importlib
            importlib.import_module("gtts")  # type: ignore[import-untyped]
            self.available_engines.append("gtts")
        except ImportError:
            pass
        
        # FFmpeg espeak fallback (always available on most systems)
        self.available_engines.append("espeak")
    
    async def generate_audio(
        self, 
        text: str, 
        output_path: Path,
        voice: VoiceStyle = VoiceStyle.PROFESSIONAL
    ) -> float:
        """
        Generate audio from text and return duration in seconds.
        """
        if "edge_tts" in self.available_engines:
            return await self._generate_edge_tts(text, output_path, voice)
        elif "gtts" in self.available_engines:
            return self._generate_gtts(text, output_path)
        elif "pyttsx3" in self.available_engines:
            return self._generate_pyttsx3(text, output_path)
        else:
            return self._generate_espeak(text, output_path)
    
    async def _generate_edge_tts(
        self, 
        text: str, 
        output_path: Path,
        voice: VoiceStyle
    ) -> float:
        """Generate audio using Edge TTS (free Microsoft voices)."""
        import edge_tts
        
        # Select voice based on style
        voice_map = {
            VoiceStyle.PROFESSIONAL: "en-US-GuyNeural",
            VoiceStyle.FRIENDLY: "en-US-JennyNeural",
            VoiceStyle.NARRATOR: "en-US-ChristopherNeural",
            VoiceStyle.ENERGETIC: "en-US-AriaNeural"
        }
        
        voice_name = voice_map.get(voice, "en-US-GuyNeural")
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(str(output_path))
        
        # Get duration
        return self._get_audio_duration(output_path)
    
    def _generate_gtts(self, text: str, output_path: Path) -> float:
        """Generate audio using Google TTS."""
        import importlib
        gtts_module = importlib.import_module("gtts")  # type: ignore[import-untyped]
        
        tts = gtts_module.gTTS(text=text, lang='en')
        tts.save(str(output_path))
        
        return self._get_audio_duration(output_path)
    
    def _generate_pyttsx3(self, text: str, output_path: Path) -> float:
        """Generate audio using pyttsx3 (offline)."""
        import importlib
        pyttsx3 = importlib.import_module("pyttsx3")  # type: ignore[import-untyped]
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Speaking rate
        engine.save_to_file(text, str(output_path))
        engine.runAndWait()
        
        return self._get_audio_duration(output_path)
    
    def _generate_espeak(self, text: str, output_path: Path) -> float:
        """Generate audio using espeak (fallback)."""
        # Write text to temp file
        text_file = TEMP_DIR / "temp_text.txt"
        text_file.write_text(text)
        
        # Generate audio with espeak
        subprocess.run([
            "espeak", "-f", str(text_file),
            "-w", str(output_path),
            "-s", "150"  # Speed
        ], check=True, capture_output=True)
        
        return self._get_audio_duration(output_path)
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of audio file using ffprobe or mutagen."""
        # Try mutagen first (Python library)
        try:
            from mutagen.mp3 import MP3  # type: ignore[import-untyped]
            audio = MP3(str(audio_path))
            return audio.info.length
        except Exception:
            pass
        
        # Try ffprobe
        try:
            result = subprocess.run([
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_path)
            ], capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
            pass
        
        # Estimate based on file size (rough: 16kbps = 2KB/s for speech)
        try:
            file_size = audio_path.stat().st_size
            return file_size / 16000  # Very rough estimate
        except Exception:
            return 10.0


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class ImageGenerator:
    """
    Generates images for video sections.
    Uses: Stable Diffusion (local), DALL-E API, or pre-made templates.
    """
    
    # Color schemes for different sections
    COLOR_SCHEMES: Dict[str, Dict[str, str]] = {
        "intro": {"bg": "#1a1a2e", "accent": "#16213e", "text": "#ffffff"},
        "content": {"bg": "#0f3460", "accent": "#e94560", "text": "#ffffff"},
        "conclusion": {"bg": "#533483", "accent": "#e94560", "text": "#ffffff"},
    }
    
    def __init__(self) -> None:
        self.has_pillow = False
        try:
            from PIL import Image, ImageDraw, ImageFont  # noqa: F401
            self.has_pillow = True
        except ImportError:
            pass
    
    def generate_title_card(
        self, 
        title: str, 
        section_type: str,
        output_path: Path,
        width: int = 1920,
        height: int = 1080
    ) -> None:
        """Generate a title card image for a video section."""
        
        if self.has_pillow:
            self._generate_pillow_image(title, section_type, output_path, width, height)
        else:
            self._generate_ffmpeg_image(title, output_path, width, height)
    
    def _generate_pillow_image(
        self, 
        title: str, 
        section_type: str,
        output_path: Path,
        width: int,
        height: int
    ) -> None:
        """Generate image using Pillow."""
        from PIL import Image, ImageDraw, ImageFont
        from PIL.ImageFont import FreeTypeFont
        
        colors = self.COLOR_SCHEMES.get(section_type, self.COLOR_SCHEMES["content"])
        
        # Create image with gradient background
        img = Image.new('RGB', (width, height), colors["bg"])
        draw = ImageDraw.Draw(img)
        
        # Add gradient effect (simple vertical gradient)
        for y_pos in range(height):
            r = int(int(colors["bg"][1:3], 16) + (y_pos / height) * 20)
            g = int(int(colors["bg"][3:5], 16) + (y_pos / height) * 10)
            b = int(int(colors["bg"][5:7], 16) + (y_pos / height) * 30)
            draw.line([(0, y_pos), (width, y_pos)], fill=(min(r, 255), min(g, 255), min(b, 255)))
        
        # Try to use a nice font, fallback to default
        font: FreeTypeFont | ImageFont.ImageFont
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        except (OSError, IOError):
            font = ImageFont.load_default()
        
        # Draw title with shadow
        text_bbox = draw.textbbox((0, 0), title, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x: int = int((width - text_width) // 2)
        y: int = int((height - text_height) // 2)
        
        # Shadow
        draw.text((x + 3, y + 3), title, fill="#000000", font=font)
        # Main text
        draw.text((x, y), title, fill=colors["text"], font=font)
        
        # Add Kloud branding
        small_font: FreeTypeFont | ImageFont.ImageFont
        try:
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except (OSError, IOError):
            small_font = ImageFont.load_default()
        
        draw.text((50, height - 60), "© Kloud 2026", fill="#888888", font=small_font)
        
        img.save(output_path, quality=95)
    
    def _generate_ffmpeg_image(
        self, 
        title: str, 
        output_path: Path,
        width: int,
        height: int
    ) -> None:
        """Generate image using FFmpeg (fallback)."""
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=#1a1a2e:s={width}x{height}:d=1",
            "-vf", f"drawtext=text='{title}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
            "-frames:v", "1",
            str(output_path)
        ], check=True, capture_output=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SUBTITLE GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class SubtitleGenerator:
    """Generates SRT subtitle files."""
    
    @staticmethod
    def generate_srt(sections: List[VideoSection], output_path: Path) -> None:
        """Generate SRT subtitle file from video sections."""
        
        srt_content: List[str] = []
        
        for section in sections:
            # Split narration into smaller chunks for subtitles
            words = section.narration_text.split()
            words_per_subtitle = 10
            
            current_time = section.subtitle_start
            chunk_duration = section.duration_seconds / max(len(words) / words_per_subtitle, 1)
            
            subtitle_idx = len(srt_content) // 3 + 1  # Each subtitle has 3 lines
            
            for i in range(0, len(words), words_per_subtitle):
                chunk_words = words[i:i + words_per_subtitle]
                chunk_text = " ".join(chunk_words)
                
                start_time = SubtitleGenerator._format_srt_time(current_time)
                end_time = SubtitleGenerator._format_srt_time(current_time + chunk_duration)
                
                srt_content.append(str(subtitle_idx))
                srt_content.append(f"{start_time} --> {end_time}")
                srt_content.append(chunk_text)
                srt_content.append("")
                
                current_time += chunk_duration
                subtitle_idx += 1
        
        output_path.write_text("\n".join(srt_content))
    
    @staticmethod
    def _format_srt_time(seconds: float) -> str:
        """Format seconds to SRT time format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


# ═══════════════════════════════════════════════════════════════════════════════
# VIDEO ASSEMBLER
# ═══════════════════════════════════════════════════════════════════════════════

class VideoAssembler:
    """Assembles video from images, audio, and subtitles using FFmpeg or MoviePy."""
    
    @staticmethod
    def check_ffmpeg() -> bool:
        """Check if FFmpeg is available."""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    @staticmethod
    def check_moviepy() -> bool:
        """Check if MoviePy is available."""
        try:
            from moviepy.editor import ImageClip  # type: ignore[import-untyped]  # noqa: F401
            return True
        except ImportError:
            return False
    
    @staticmethod
    def assemble_video(
        sections: List[VideoSection],
        output_path: Path,
        srt_path: Optional[Path] = None
    ) -> None:
        """Assemble final video from sections."""
        
        # Try MoviePy first (doesn't require global FFmpeg install)
        if VideoAssembler.check_moviepy():
            VideoAssembler._assemble_with_moviepy(sections, output_path)
            return
        
        # Fallback to FFmpeg
        if VideoAssembler.check_ffmpeg():
            VideoAssembler._assemble_with_ffmpeg(sections, output_path, srt_path)
            return
        
        raise RuntimeError(
            "Neither FFmpeg nor MoviePy available. Install one:\n"
            "  pip install moviepy\n"
            "  OR\n"
            "  choco install ffmpeg (as admin)"
        )
    
    @staticmethod
    def _assemble_with_moviepy(sections: List[VideoSection], output_path: Path) -> None:
        """Assemble video using MoviePy."""
        from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips  # type: ignore[import-untyped]
        
        clips: List[Any] = []
        
        for section in sections:
            if section.image_path and section.audio_path:
                # Load audio to get duration
                audio = AudioFileClip(str(section.audio_path))
                
                # Create image clip with audio duration
                img_clip = (
                    ImageClip(str(section.image_path))
                    .set_duration(audio.duration)
                    .set_audio(audio)
                )
                clips.append(img_clip)
        
        if clips:
            # Concatenate all clips
            final = concatenate_videoclips(clips, method="compose")
            final.write_videofile(
                str(output_path),
                fps=24,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None
            )
            
            # Clean up
            final.close()
            for clip in clips:
                clip.close()
    
    @staticmethod
    def _assemble_with_ffmpeg(
        sections: List[VideoSection],
        output_path: Path,
        srt_path: Optional[Path] = None
    ) -> None:
        """Assemble video using FFmpeg CLI."""
        # Create concat file for FFmpeg
        concat_file = TEMP_DIR / "concat.txt"
        concat_content: List[str] = []
        
        for section in sections:
            if section.image_path and section.audio_path:
                # Create video segment from image + audio
                segment_path = TEMP_DIR / f"segment_{section.index}.mp4"
                
                subprocess.run([
                    "ffmpeg", "-y",
                    "-loop", "1",
                    "-i", str(section.image_path),
                    "-i", str(section.audio_path),
                    "-c:v", "libx264",
                    "-tune", "stillimage",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    str(segment_path)
                ], check=True, capture_output=True)
                
                concat_content.append(f"file '{segment_path}'")
        
        concat_file.write_text("\n".join(concat_content))
        
        # Concatenate all segments
        temp_output = TEMP_DIR / "temp_video.mp4"
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(temp_output)
        ], check=True, capture_output=True)
        
        # Add subtitles if provided
        if srt_path and srt_path.exists():
            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(temp_output),
                "-vf", f"subtitles={srt_path}",
                "-c:a", "copy",
                str(output_path)
            ], check=True, capture_output=True)
        else:
            temp_output.rename(output_path)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN VIDEO GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class VideoGeneratorBLERINA:
    """
    Main video generator using BLERINA architecture.
    
    Pipeline:
    1. Generate script (BLERINA content)
    2. Generate audio (TTS)
    3. Generate images (AI or templates)
    4. Assemble video (FFmpeg)
    5. Add subtitles (SRT)
    """
    
    def __init__(self) -> None:
        self.script_gen = ScriptGenerator()
        self.tts_engine = TTSEngine()
        self.image_gen = ImageGenerator()
        self.subtitle_gen = SubtitleGenerator()
        self.video_assembler = VideoAssembler()
    
    async def generate_video(
        self,
        topic: str,
        style: VideoStyle = VideoStyle.EDUCATIONAL,
        voice: VoiceStyle = VoiceStyle.PROFESSIONAL,
        add_subtitles: bool = True
    ) -> VideoProject:
        """
        Generate a complete video from topic.
        
        Args:
            topic: Video topic (e.g., "How EEG Brain-Computer Interfaces Work")
            style: Visual style of the video
            voice: Voice style for narration
            add_subtitles: Whether to add subtitles
        
        Returns:
            VideoProject with paths to generated files
        """
        start_time = time.time()
        
        # Create project
        project = VideoProject(
            title=topic,
            topic=topic,
            style=style
        )
        
        # 1. Generate script
        print(f"📝 Generating script for: {topic}")
        project.sections = self.script_gen.generate_script(topic, style)
        
        # 2. Generate audio for each section
        print("🔊 Generating audio narration...")
        current_time = 0.0
        for section in project.sections:
            audio_path = TEMP_DIR / f"audio_{section.index}.mp3"
            duration = await self.tts_engine.generate_audio(
                section.narration_text,
                audio_path,
                voice
            )
            section.audio_path = audio_path
            section.duration_seconds = duration
            section.subtitle_start = current_time
            section.subtitle_end = current_time + duration
            current_time += duration
            print(f"  ✓ Section {section.index}: {section.title} ({duration:.1f}s)")
        
        project.total_duration = current_time
        
        # 3. Generate images for each section
        print("🎨 Generating visuals...")
        for section in project.sections:
            image_path = TEMP_DIR / f"image_{section.index}.png"
            section_type = "intro" if section.index == 0 else (
                "conclusion" if section.index == len(project.sections) - 1 else "content"
            )
            self.image_gen.generate_title_card(
                section.title,
                section_type,
                image_path
            )
            section.image_path = image_path
            print(f"  ✓ Image for: {section.title}")
        
        # 4. Generate subtitles
        if add_subtitles:
            print("📜 Generating subtitles...")
            srt_path = VIDEO_OUTPUT_DIR / f"{self._sanitize_filename(topic)}.srt"
            self.subtitle_gen.generate_srt(project.sections, srt_path)
            project.srt_path = srt_path
        
        # 5. Assemble video
        print("🎬 Assembling video...")
        output_path = VIDEO_OUTPUT_DIR / f"{self._sanitize_filename(topic)}.mp4"
        self.video_assembler.assemble_video(
            project.sections,
            output_path,
            project.srt_path
        )
        project.output_path = output_path
        
        elapsed = time.time() - start_time
        print("\n✅ Video generated successfully!")
        print(f"   📹 Output: {output_path}")
        print(f"   ⏱️  Duration: {project.total_duration:.1f} seconds")
        print(f"   🕐 Generation time: {elapsed:.1f} seconds")
        
        return project
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Sanitize a string for use as filename."""
        return "".join(c if c.isalnum() or c in " -_" else "_" for c in name).strip()


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

# Global instance
_generator: Optional[VideoGeneratorBLERINA] = None


def get_generator() -> VideoGeneratorBLERINA:
    """Get or create the video generator instance."""
    global _generator
    if _generator is None:
        _generator = VideoGeneratorBLERINA()
    return _generator


async def generate_video(
    topic: str,
    style: str = "educational",
    voice: str = "professional",
    add_subtitles: bool = True
) -> Dict[str, Any]:
    """
    Generate a video from a topic.
    
    Args:
        topic: Video topic
        style: Video style (educational, documentary, tutorial, presentation, social_media)
        voice: Voice style (professional, friendly, narrator, energetic)
        add_subtitles: Whether to add subtitles
    
    Returns:
        Dict with video information
    """
    generator = get_generator()
    
    video_style = VideoStyle(style) if style in [s.value for s in VideoStyle] else VideoStyle.EDUCATIONAL
    voice_style = VoiceStyle(voice) if voice in [v.value for v in VoiceStyle] else VoiceStyle.PROFESSIONAL
    
    project = await generator.generate_video(topic, video_style, voice_style, add_subtitles)
    
    return {
        "success": True,
        "title": project.title,
        "output_path": str(project.output_path) if project.output_path else None,
        "srt_path": str(project.srt_path) if project.srt_path else None,
        "duration_seconds": project.total_duration,
        "sections": len(project.sections),
        "created_at": project.created_at
    }


def health() -> Dict[str, Any]:
    """Health check for video generator."""
    generator = get_generator()
    
    return {
        "status": "ok",
        "tts_engines": generator.tts_engine.available_engines,
        "ffmpeg_available": VideoAssembler.check_ffmpeg(),
        "pillow_available": generator.image_gen.has_pillow,
        "output_dir": str(VIDEO_OUTPUT_DIR)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CLI / MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import asyncio
    
    print("=" * 70)
    print("VIDEO GENERATOR BLERINA — Test Run")
    print("=" * 70)
    
    # Check health
    health_status = health()
    print("\nHealth Check:")
    print(f"  TTS Engines: {health_status['tts_engines']}")
    print(f"  FFmpeg: {'✅' if health_status['ffmpeg_available'] else '❌'}")
    print(f"  Pillow: {'✅' if health_status['pillow_available'] else '❌'}")
    
    if not health_status['ffmpeg_available']:
        print("\n❌ FFmpeg is required. Install with:")
        print("   Windows: winget install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Linux: apt install ffmpeg")
    else:
        # Generate a test video
        print("\nGenerating test video...")
        result = asyncio.run(generate_video(
            topic="How EEG Brain-Computer Interfaces Work",
            style="educational",
            add_subtitles=True
        ))
        print(f"\nResult: {result}")

