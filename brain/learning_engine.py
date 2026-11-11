# brain/learning_engine.py

from memory.memory import get_user_profile, save_learning

def learn_command_pattern(pattern, response):
    """AI ko sikhana ki user kaise baat karta hai"""
    profile = get_user_profile()
    if "patterns" not in profile:
        profile["patterns"] = {}
    profile["patterns"][pattern] = response
    save_learning("patterns", profile["patterns"])

def suggest_tool(query):
    """Query ke hisab se tool suggest karna"""
    # Simple keyword matching
    query = query.lower()
    if "photo" in query or "image" in query:
        return "image_search"
    elif "call" in query or "phone" in query:
        return "call_number"
    elif "file" in query or "download" in query:
        return "file_downloader"
    elif "sign" in query:
        return "signature_tool"
    return None

def learn_from_mistake(mistake, correction):
    """Galati se kuch seekhna"""
    profile = get_user_profile()
    if "mistakes" not in profile:
        profile["mistakes"] = {}
    profile["mistakes"][mistake] = correction
    save_learning("mistakes", profile["mistakes"])