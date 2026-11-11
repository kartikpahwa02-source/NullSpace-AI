"""
EmptyNSpace Brain - LLM Engine
With NKJ Law Smart Caching
Created by Nikhil Jatav
"""

import requests
import json
import hashlib
import time
import os

OLLAMA_URL = 'http://localhost:11434/api/generate'
OLLAMA_CHAT_URL = 'http://localhost:11434/api/chat'
DEFAULT_MODEL = 'llama3.2:1b'

try:
    from brain.nkj_engine import NKJ_Engine
    nkj_engine = NKJ_Engine()
    NKJ_LOADED = True
    print("🧠 NKJ Engine: ✅ Loaded")
except:
    nkj_engine = None
    NKJ_LOADED = False


class NKJ_SmartCache:
    def __init__(self):
        self.cache = {}
        self.stats = {'hits': 0, 'misses': 0, 'saved_time': 0}
        self.cache_file = 'data/nkj_cache.json'
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache = data.get('cache', {})
                    self.stats = data.get('stats', self.stats)
        except:
            pass

    def _save(self):
        try:
            os.makedirs('data', exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({'cache': self.cache, 'stats': self.stats}, f, ensure_ascii=False)
        except:
            pass

    def _key(self, msg):
        normalized = ' '.join(msg.lower().strip().split())
        return hashlib.md5(normalized.encode()).hexdigest(), normalized

    def get(self, message):
        key, normalized = self._key(message)
        if key in self.cache:
            self.stats['hits'] += 1
            self.stats['saved_time'] += 3
            return self.cache[key]['response'], True
        self.stats['misses'] += 1
        return None, False

    def put(self, message, response):
        key, normalized = self._key(message)
        self.cache[key] = {
            'message': message,
            'normalized': normalized,
            'response': response,
            'time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        if len(self.cache) > 500:
            keys = sorted(self.cache.keys(), key=lambda k: self.cache[k].get('time', ''))
            for old in keys[:50]:
                del self.cache[old]
        self._save()

    def get_stats(self):
        total = self.stats['hits'] + self.stats['misses']
        rate = (self.stats['hits'] / total * 100) if total > 0 else 0
        return {
            'queries': total,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': f"{rate:.1f}%",
            'time_saved': f"{self.stats['saved_time']}s",
            'cache_size': len(self.cache)
        }


nkj_cache = NKJ_SmartCache()


def check_nkj_status():
    try:
        r = requests.get('http://localhost:11434/api/tags', timeout=3)
        return r.status_code == 200
    except:
        return False


def chat(messages, model=None, agent_name='NKJ_AI'):
    user_msg = ""
    for msg in reversed(messages):
        if msg.get('role') == 'user':
            user_msg = msg.get('content', '')
            break

    if not user_msg:
        return "No message provided."

    cached, from_cache = nkj_cache.get(user_msg)
    if from_cache:
        return cached

    if model is None:
        model = DEFAULT_MODEL

    try:
        r = requests.post(OLLAMA_CHAT_URL, json={
            'model': model,
            'messages': messages,
            'stream': False
        }, timeout=60)

        if r.status_code == 200:
            data = r.json()
            response = data.get('message', {}).get('content', 'No response')
            nkj_cache.put(user_msg, response)
            return response
        else:
            return f'Error: Status {r.status_code}'
    except requests.exceptions.Timeout:
        return "Response timeout. Try shorter question."
    except Exception as e:
        return f'Error: {str(e)}'


def generate(prompt, model=DEFAULT_MODEL):
    cached, from_cache = nkj_cache.get(prompt)
    if from_cache:
        return cached

    try:
        r = requests.post(OLLAMA_URL, json={
            'model': model,
            'prompt': prompt,
            'stream': False
        }, timeout=60)

        if r.status_code == 200:
            response = r.json().get('response', 'No response')
            nkj_cache.put(prompt, response)
            return response
        return f'Error: {r.status_code}'
    except Exception as e:
        return f'Error: {e}'


def get_nkj_stats():
    return {
        'cache': nkj_cache.get_stats(),
        'engine': nkj_engine.get_stats() if nkj_engine else 'Not loaded',
        'status': 'Active' if NKJ_LOADED else 'Inactive'
    }