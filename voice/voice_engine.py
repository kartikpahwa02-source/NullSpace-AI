"""
Voice Engine:
- Sarvam STT (Hindi/Indian languages)
- Sarvam TTS (Indian voices)
- Browser Speech API (fallback)
"""

from tools.sarvam_voice import (
    sarvam_speech_to_text,
    sarvam_text_to_speech,
    sarvam_translate,
    sarvam_transliterate,
    sarvam_detect_language
)

def speech_to_text(audio_bytes, language="hi-IN"):
    """Audio → Text (Sarvam)"""
    return sarvam_speech_to_text(audio_bytes, language)

def text_to_speech(text, language="hi-IN", speaker=None):
    """Text → Audio (Sarvam)"""
    return sarvam_text_to_speech(text, language, speaker)

def translate_text(text, source="en", target="hi"):
    """Translation (Sarvam)"""
    return sarvam_translate(text, source, target)

def transliterate_text(text, source="en", target="hi"):
    """Transliteration (Sarvam)"""
    return sarvam_transliterate(text, source, target)

def detect_language(text):
    """Language detection (Sarvam)"""
    return sarvam_detect_language(text)