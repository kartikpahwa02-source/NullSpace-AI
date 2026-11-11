import os
import tempfile
import base64
from sarvamai import SarvamAI
from config.settings import (
    SARVAM_API_KEY,
    SARVAM_STT_MODEL,
    SARVAM_TTS_MODEL,
    SARVAM_TTS_SPEAKER,
    SARVAM_DEFAULT_LANGUAGE
)

_client = None

def get_sarvam():
    global _client
    if _client is None:
        _client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
    return _client


# ===================== SPEECH TO TEXT =====================
def sarvam_speech_to_text(audio_bytes, language="hi-IN"):
    """Audio bytes → Text convert karo"""
    try:
        client = get_sarvam()

        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_bytes)
            temp_path = f.name

        # API call
        result = client.speech_to_text.transcribe(
            file=open(temp_path, "rb"),
            model=SARVAM_STT_MODEL,
            language_code=language
        )

        os.unlink(temp_path)

        if hasattr(result, "transcript"):
            return result.transcript
        elif hasattr(result, "text"):
            return result.text
        else:
            return str(result)

    except Exception as e:
        return f"STT Error: {e}"


# ===================== TEXT TO SPEECH =====================
def sarvam_text_to_speech(text, language="hi-IN", speaker=None):
    """Text → Audio bytes convert karo"""
    try:
        client = get_sarvam()
        speaker = speaker or SARVAM_TTS_SPEAKER

        # Sarvam TTS call
        result = client.text_to_speech.convert(
            text=text[:500],       # Limit 500 chars
            model=SARVAM_TTS_MODEL,
            speaker=speaker,
            target_language_code=language
        )

        # Get audio bytes
        if hasattr(result, "audios") and result.audios:
            audio_data = result.audios[0]
            if isinstance(audio_data, str):
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = audio_data
            return audio_bytes

        return None

    except Exception as e:
        print(f"TTS Error: {e}")
        return None


# ===================== TRANSLATION =====================
def sarvam_translate(text, source_lang="en", target_lang="hi"):
    """Text ko ek language se doosri me translate karo"""
    try:
        client = get_sarvam()

        result = client.translate.translate(
            input=text,
            source_language_code=source_lang,
            target_language_code=target_lang,
            model="sarvam-translate:v1"
        )

        if hasattr(result, "translated_text"):
            return result.translated_text
        elif hasattr(result, "output"):
            return result.output
        else:
            return str(result)

    except Exception as e:
        return f"Translation Error: {e}"


# ===================== TRANSLITERATION =====================
def sarvam_transliterate(text, source_lang="en", target_lang="hi"):
    """Text ko ek script se doosri script me convert karo"""
    try:
        client = get_sarvam()

        result = client.transliterate.transliterate(
            input=text,
            source_language_code=source_lang,
            target_language_code=target_lang,
        )

        if hasattr(result, "transliterated_text"):
            return result.transliterated_text
        else:
            return str(result)

    except Exception as e:
        return f"Transliteration Error: {e}"


# ===================== LANGUAGE DETECT =====================
def sarvam_detect_language(text):
    """Text ki language detect karo"""
    try:
        client = get_sarvam()

        result = client.language_identification.identify(
            input=text
        )

        if hasattr(result, "language_code"):
            return result.language_code
        else:
            return str(result)

    except Exception as e:
        return f"Detection Error: {e}"