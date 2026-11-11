import json
import os
from datetime import datetime

# =========================
# FILE PATHS
# =========================

MEMORY_FILE = "data/user_brain.json"

# =========================
# RUNTIME STORAGE
# =========================

_histories = {}
_file_store = {}
_user_profile = {}
_learned_data = {}
_task_history = []
_opinions = {}
_learnings = {}

# =========================
# LOAD / SAVE
# =========================

def load_memory():

    global _user_profile, _learned_data, _task_history, _opinions, _learnings

    try:

        if os.path.exists(MEMORY_FILE):

            with open(MEMORY_FILE, "r", encoding="utf-8") as f:

                data = json.load(f)

            _user_profile = data.get("user_profile", {})
            _learned_data = data.get("learned_data", {})
            _task_history = data.get("task_history", [])
            _opinions = data.get("opinions", {})
            _learnings = data.get("learnings", {})

    except Exception:

        pass


def save_memory():

    try:

        os.makedirs("data", exist_ok=True)

        data = {
            "user_profile": _user_profile,
            "learned_data": _learned_data,
            "task_history": _task_history,
            "opinions": _opinions,
            "learnings": _learnings
        }

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:

            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception:

        pass


# =========================
# CHAT HISTORY
# =========================

def get_history(cid):

    if cid not in _histories:
        _histories[cid] = []

    return _histories[cid]


def add_message(cid, role, content):

    get_history(cid).append({
        "role": role,
        "content": content
    })


def reset_history(cid):

    _histories.pop(cid, None)
    _file_store.pop(cid, None)


# =========================
# FILE STORAGE
# =========================

def save_file_info(cid, info):

    _file_store[cid] = info


def get_file_info(cid):

    return _file_store.get(cid)


# =========================
# USER PROFILE
# =========================

def update_user_profile(key, value):

    _user_profile[key] = value

    save_memory()


def get_user_profile(key=None):

    if key:
        return _user_profile.get(key)

    return _user_profile


# =========================
# LEARNING SYSTEM
# =========================

def learn(key, value):

    if key not in _learned_data:
        _learned_data[key] = []

    _learned_data[key].append({
        "value": value,
        "timestamp": datetime.now().isoformat()
    })

    save_memory()


def get_learned(key=None):

    if key:
        return _learned_data.get(key, [])

    return _learned_data


def get_all_learnings():

    return _learned_data


def save_learning(key, value):

    learn(key, value)


def get_learnings(key=None):

    return get_learned(key)


# =========================
# TASK HISTORY
# =========================

def add_task_history(task, result, success):

    _task_history.append({
        "task": task,
        "result": str(result)[:500],
        "success": success,
        "timestamp": datetime.now().isoformat()
    })

    save_memory()


def get_task_history(limit=20):

    return _task_history[-limit:]


# =========================
# OPINIONS
# =========================

def save_opinion(topic, opinion):

    _opinions[topic] = {
        "opinion": opinion,
        "timestamp": datetime.now().isoformat()
    }

    save_memory()


def get_opinion(topic=None):

    if topic:
        return _opinions.get(topic)

    return _opinions


# =========================
# GENERIC STORAGE
# =========================

def store(key, value):

    _learnings[key] = value

    save_memory()


def retrieve(key):

    return _learnings.get(key)


# =========================
# USER BRAIN (PER USER MEMORY)
# =========================

def learn_user(cid, key, value):

    if cid not in _user_profile:

        _user_profile[cid] = {
            "preferences": {},
            "habits": {},
            "history": []
        }

    _user_profile[cid]["preferences"][key] = value

    save_memory()


def get_user_data(cid):

    return _user_profile.get(cid, {
        "preferences": {},
        "habits": {},
        "history": []
    })


# =========================
# INITIAL LOAD
# =========================

load_memory()