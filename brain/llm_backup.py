import requests
import json
import os

# NKJ Compression Engine
try:
    from brain.nkj_engine import NKJ_Engine
    nkj_engine = NKJ_Engine()
    NKJ_AVAILABLE = True
    print("🧠 NKJ Engine: ✅ Loaded")
except Exception as e:
    NKJ_AVAILABLE = False
    print(f"🧠 NKJ Engine: ❌ {e}")

OLLAMA_URL = "http://localhost:11434"
MODEL = "nkj-ai"

TRAINING_DATA = []
data_path = os.path.join(os.path.dirname(__file__), '..', 'nkj_training_data.json')
try:
    with open(data_path, 'r', encoding='utf-8') as f:
        TRAINING_DATA = json.load(f)
    print(f"📚 Loaded {len(TRAINING_DATA)} trained responses")
except:
    print("⚠️ No training data found")

def find_match(user_input):
    user_lower = user_input.lower().strip()
    best_match = None
    best_score = 0
    for item in TRAINING_DATA:
        input_lower = item['input'].lower().strip()
        if user_lower == input_lower:
            return item['output']
        user_words = set(user_lower.split())
        input_words = set(input_lower.split())
        if not user_words or not input_words:
            continue
        common = user_words & input_words
        score = len(common) / max(len(user_words), len(input_words))
        for kw in ['open', 'call', 'search', 'write', 'code', 'what', 'who', 'send']:
            if kw in user_lower and kw in input_lower:
                score += 0.3
        if score > best_score:
            best_score = score
            best_match = item['output']
    return best_match if best_score > 0.5 else None

def chat(messages):
    user_message = messages[-1]['content']
    matched = find_match(user_message)
    if matched:
        return matched
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={"model": MODEL, "messages": messages, "stream": False},
            timeout=60
        )
        return response.json()["message"]["content"]
    except Exception as e:
        return f"NKJ AI offline. Start Ollama first."

def check_nkj_status():
    try:
        return requests.get(f"{OLLAMA_URL}/api/tags", timeout=2).status_code == 200
    except:
        return False