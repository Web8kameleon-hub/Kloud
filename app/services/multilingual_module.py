"""
Multilingual Module for Kloud Cloud
Real implementation with actual APIs and services
"""

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Third-party imports for real services
import boto3  # AWS Translate
import edge_tts
import requests
import speech_recognition as sr
from google.cloud import translate_v2 as google_translate
from googletrans import Translator as GoogleTranslator
from pydub import AudioSegment

logger = logging.getLogger(__name__)

@dataclass
class TranslationResult:
    """Result container for translation operations"""
    source_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    service_used: str

@dataclass
class SpeechRecognitionResult:
    """Result container for speech recognition"""
    text: str
    language: str
    confidence: float
    duration: float

class RealMultilingualService:
    """
    Real multilingual service using actual APIs:
    - AWS Translate for professional translations
    - Google Cloud Translate for backup
    - Deep Translator for free tier
    - SpeechRecognition with real audio processing
    - Edge TTS for text-to-speech
    """
    
    def __init__(self):
        self.initialize_services()
        self.supported_languages = self.get_supported_languages()
        
    def initialize_services(self):
        """Initialize all real API clients"""
        try:
            # AWS Translate Client (Real API)
            self.aws_translate = boto3.client(
                'translate',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            logger.info("AWS Translate client initialized successfully")
        except Exception as e:
            logger.warning(f"AWS Translate not available: {e}")
            self.aws_translate = None

        try:
            # Google Cloud Translate Client (Real API)
            self.google_translate = google_translate.Client()
            logger.info("Google Cloud Translate client initialized successfully")
        except Exception as e:
            logger.warning(f"Google Cloud Translate not available: {e}")
            self.google_translate = None

        # Speech Recognition
        self.speech_recognizer = sr.Recognizer()
        
        # Translation cache to avoid duplicate API calls
        self.translation_cache = {}
        self.cache_ttl = timedelta(hours=24)
        
    def get_supported_languages(self) -> Dict[str, str]:
        """Get real supported languages from multiple services"""
        languages = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'tr': 'Turkish',
            'nl': 'Dutch',
            'pl': 'Polish',
            'sv': 'Swedish',
            'da': 'Danish',
            'fi': 'Finnish',
            'no': 'Norwegian',
            'cs': 'Czech',
            'ro': 'Romanian',
            'hu': 'Hungarian',
            'bg': 'Bulgarian',
            'el': 'Greek',
            'he': 'Hebrew',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'sq': 'Albanian',
            'sr': 'Serbian',
            'hr': 'Croatian',
            'bs': 'Bosnian',
            'mk': 'Macedonian',
            'sl': 'Slovenian'
        }
        return languages

    def translate_text(self, text: str, target_language: str, source_language: str = 'auto') -> TranslationResult:
        """
        Real text translation using multiple fallback services
        """
        # Check cache first
        cache_key = f"{source_language}_{target_language}_{hash(text)}"
        cached_result = self.translation_cache.get(cache_key)
        if cached_result and datetime.now() - cached_result['timestamp'] < self.cache_ttl:
            return TranslationResult(**cached_result['data'])

        translation_result = None
        
        # Try AWS Translate first (most reliable)
        if self.aws_translate and source_language != 'auto':
            try:
                response = self.aws_translate.translate_text(
                    Text=text,
                    SourceLanguageCode=source_language,
                    TargetLanguageCode=target_language
                )
                translation_result = TranslationResult(
                    source_text=text,
                    translated_text=response['TranslatedText'],
                    source_language=response['SourceLanguageCode'],
                    target_language=target_language,
                    confidence=0.95,  # AWS doesn't provide confidence score
                    service_used='aws_translate'
                )
                logger.info(f"Translation completed via AWS Translate: {source_language} -> {target_language}")
            except Exception as e:
                logger.warning(f"AWS Translate failed: {e}")

        # Try Google Cloud Translate
        if not translation_result and self.google_translate:
            try:
                if source_language == 'auto':
                    result = self.google_translate.translate(text, target_language=target_language)
                else:
                    result = self.google_translate.translate(text, source_language=source_language, target_language=target_language)
                
                translation_result = TranslationResult(
                    source_text=text,
                    translated_text=result['translatedText'],
                    source_language=result.get('detectedSourceLanguage', source_language),
                    target_language=target_language,
                    confidence=float(result.get('confidence', 0.9)),
                    service_used='google_translate'
                )
                logger.info(f"Translation completed via Google Translate: {translation_result.source_language} -> {target_language}")
            except Exception as e:
                logger.warning(f"Google Cloud Translate failed: {e}")

        # Fallback to Deep Translator (free)
        if not translation_result:
            try:
                translated = GoogleTranslator(source=source_language, target=target_language).translate(text)
                translation_result = TranslationResult(
                    source_text=text,
                    translated_text=translated,
                    source_language=source_language,
                    target_language=target_language,
                    confidence=0.85,
                    service_used='deep_translator'
                )
                logger.info(f"Translation completed via Deep Translator: {source_language} -> {target_language}")
            except Exception as e:
                logger.error(f"All translation services failed: {e}")
                raise Exception(f"Translation failed: {e}")

        # Cache the result
        self.translation_cache[cache_key] = {
            'data': translation_result.__dict__,
            'timestamp': datetime.now()
        }

        return translation_result

    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Real language detection using available services
        """
        if self.google_translate:
            try:
                result = self.google_translate.detect_language(text)
                return result['language'], float(result.get('confidence', 0.9))
            except Exception as e:
                logger.warning(f"Google language detection failed: {e}")

        # Fallback to simple character-based detection
        return self._fallback_language_detection(text)

    def _fallback_language_detection(self, text: str) -> Tuple[str, float]:
        """Fallback language detection based on character analysis"""
        # Simple character-based language detection
        import re
        
        # Common patterns for different languages
        patterns = {
            'en': r'[a-zA-Z]',  # Latin script
            'ru': r'[Ð°-ÑÐ-Ð¯]',  # Cyrillic
            'zh': r'[\u4e00-\u9fff]',  # Chinese characters
            'ja': r'[\u3040-\u309f\u30a0-\u30ff]',  # Hiragana/Katakana
            'ar': r'[\u0600-\u06ff]',  # Arabic
            'el': r'[\u0370-\u03ff]',  # Greek
            'he': r'[\u0590-\u05ff]',  # Hebrew
        }
        
        scores = {}
        total_chars = len(re.findall(r'\S', text))  # Non-whitespace characters
        
        for lang, pattern in patterns.items():
            matches = len(re.findall(pattern, text))
            if total_chars > 0:
                scores[lang] = matches / total_chars
        
        if scores:
            best_lang = max(scores, key=lambda k: scores[k])
            return best_lang, scores[best_lang]
        
        return 'en', 0.5  # Default to English with low confidence

    def speech_to_text(self, audio_file_path: str, language: str = 'en-US') -> SpeechRecognitionResult:
        """
        Real speech-to-text conversion using multiple engines
        """
        try:
            # Convert audio to WAV if necessary
            if not audio_file_path.lower().endswith('.wav'):
                audio = AudioSegment.from_file(audio_file_path)
                wav_path = f"/tmp/{uuid.uuid4()}.wav"
                audio.export(wav_path, format="wav")
                audio_file_path = wav_path

            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.speech_recognizer.record(source)
                
                # Try Google Speech Recognition first
                try:
                    text = self.speech_recognizer.recognize_google(audio_data, language=language)
                    confidence = 0.9
                    logger.info(f"Speech-to-text completed via Google: {language}")
                except sr.UnknownValueError:
                    # Fallback to Sphinx (offline)
                    text = self.speech_recognizer.recognize_sphinx(audio_data)
                    confidence = 0.7
                    logger.info(f"Speech-to-text completed via Sphinx: {language}")

            # Calculate audio duration
            audio = AudioSegment.from_file(audio_file_path)
            duration = len(audio) / 1000.0  # Convert to seconds

            return SpeechRecognitionResult(
                text=text,
                language=language,
                confidence=confidence,
                duration=duration
            )

        except Exception as e:
            logger.error(f"Speech-to-text conversion failed: {e}")
            raise Exception(f"Speech recognition failed: {e}")

    async def text_to_speech(self, text: str, language: str = 'en', output_file: Optional[str] = None) -> str:
        """
        Real text-to-speech conversion using Edge TTS
        """
        try:
            if not output_file:
                output_file = f"/tmp/tts_{uuid.uuid4()}.mp3"

            # Map language codes to voice names
            voice_map = {
                'en': 'en-US-AriaNeural',
                'es': 'es-ES-ElviraNeural',
                'fr': 'fr-FR-DeniseNeural',
                'de': 'de-DE-KatjaNeural',
                'it': 'it-IT-ElsaNeural',
                'pt': 'pt-BR-FranciscaNeural',
                'ru': 'ru-RU-SvetlanaNeural',
                'zh': 'zh-CN-XiaoxiaoNeural',
                'ja': 'ja-JP-NanamiNeural',
                'ko': 'ko-KR-SunHiNeural',
                'ar': 'ar-EG-SalmaNeural',
                'hi': 'hi-IN-SwaraNeural',
                'tr': 'tr-TR-EmelNeural',
            }
            
            voice = voice_map.get(language, 'en-US-AriaNeural')
            communicate = edge_tts.Communicate(text, voice)
            
            await communicate.save(output_file)
            logger.info(f"Text-to-speech completed: {language} -> {output_file}")
            
            return output_file

        except Exception as e:
            logger.error(f"Text-to-speech conversion failed: {e}")
            raise Exception(f"TTS failed: {e}")

    def batch_translate(self, texts: List[str], target_language: str, source_language: str = 'auto') -> List[TranslationResult]:
        """Batch translation for multiple texts"""
        results = []
        for text in texts:
            try:
                result = self.translate_text(text, target_language, source_language)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch translation failed for text: {text[:50]}... Error: {e}")
                # Add fallback result
                results.append(TranslationResult(
                    source_text=text,
                    translated_text=text,  # Return original as fallback
                    source_language=source_language,
                    target_language=target_language,
                    confidence=0.0,
                    service_used='fallback'
                ))
        return results

    def get_translation_usage_stats(self) -> Dict:
        """Get real usage statistics"""
        return {
            'cache_size': len(self.translation_cache),
            'supported_languages': len(self.supported_languages),
            'services_available': {
                'aws_translate': self.aws_translate is not None,
                'google_translate': self.google_translate is not None
            },
            'timestamp': datetime.now().isoformat()
        }

    def clear_cache(self):
        """Clear translation cache"""
        self.translation_cache.clear()
        logger.info("Translation cache cleared")

# Singleton instance
_multilingual_service = None

def get_multilingual_service() -> RealMultilingualService:
    """Get singleton instance of multilingual service"""
    global _multilingual_service
    if _multilingual_service is None:
        _multilingual_service = RealMultilingualService()
    return _multilingual_service

# Example usage and testing
if __name__ == "__main__":
    # Initialize service
    service = get_multilingual_service()
    
    # Test translation
    try:
        result = service.translate_text("Hello world!", "es", "en")
        print(f"Translation: {result.translated_text}")
        print(f"Service used: {result.service_used}")
    except Exception as e:
        print(f"Translation test failed: {e}")
    
    # Test language detection
    lang, confidence = service.detect_language("Hola mundo")
    print(f"Detected language: {lang} (confidence: {confidence})")
    
    # Print usage stats
    stats = service.get_translation_usage_stats()
    print(f"Service stats: {stats}")


