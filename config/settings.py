# ============== AI BACKEND ==============
AI_BACKEND = "groq"                    # "groq" / "ollama" / "sarvam"
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
GROQ_MODEL = "llama-3.1-8b-instant"
OLLAMA_MODEL = "llama3"

# ============== SARVAM AI ==============
SARVAM_API_KEY = "sk_c4fy8xws_XtXVd3hVTStU6GjCqBdSVdYk"  # Sarvam se lo
SARVAM_LLM_MODEL = "sarvam-m"                             # Sarvam Chat Model
SARVAM_STT_MODEL = "saaras:v2.5"                          # Speech to Text
SARVAM_TTS_MODEL = "bulbul:v2"                            # Text to Speech
SARVAM_TTS_SPEAKER = "anushka"                            # Voice: anushka/hema/meera/priya/rahul
SARVAM_DEFAULT_LANGUAGE = "hi-IN"                          # Default Hindi

# ============== PATHS ==============
UPLOAD_DIR = "uploads"

# ============== ANDROID ==============
ADB_PATH = "adb"

# ============== BROWSER ==============
BROWSER_HEADLESS = False
BROWSER_TIMEOUT = 15

# ============== IOT ==============
IOT_DEVICES_FILE = "data/iot_devices.json"

# ============== SMART HOME ==============
SMART_HOME_DEVICES = {
    "living_room_light": {"type": "light", "ip": "192.168.1.100", "port": 80},
    "bedroom_fan":       {"type": "fan", "ip": "192.168.1.101", "port": 80},
    "ac":                {"type": "ac", "ip": "192.168.1.102", "port": 80},
}

# ============== APP ==============
APP_NAME = "EmptySpace AI"
APP_VERSION = "4.0"

# ============================================
# NKJ LAW COMPRESSION (by Nikhil Jatav)
# ============================================
NKJ_ENABLED = True
NKJ_DEFAULT_FREQ = 64
NKJ_COMPRESSION_LEVEL = 'balanced'  # fast, balanced, quality, maximum
NKJ_CREATOR = 'Nikhil Jatav'
NKJ_TECHNOLOGY = 'NKJ Law of Contextual Generation'