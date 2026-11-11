"""
Knowledge Base — SQLite + Vector DB
Ye EmptySpace ka permanent brain hai
Sab kuch yaad rakhta hai
"""

import sqlite3
import os
import json
import hashlib
from datetime import datetime

DB_PATH = "data/knowledge.db"


def _get_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Database tables create karo"""
    conn = _get_db()
    c = conn.cursor()

    # Knowledge table — sab information store
    c.execute("""CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        content TEXT NOT NULL,
        source TEXT,
        category TEXT,
        confidence REAL DEFAULT 0.5,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        access_count INTEGER DEFAULT 0
    )""")

    # Conversations table — har baat yaad
    c.execute("""CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # Skills table — kya kya aata hai
    c.execute("""CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT UNIQUE,
        description TEXT,
        proficiency REAL DEFAULT 0.5,
        learned_from TEXT,
        times_used INTEGER DEFAULT 0,
        last_used TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # Patterns table — patterns seekho
    c.execute("""CREATE TABLE IF NOT EXISTS patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_type TEXT,
        input_pattern TEXT,
        output_pattern TEXT,
        success_rate REAL DEFAULT 0.5,
        times_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # World Facts table — duniya ki knowledge
    c.execute("""CREATE TABLE IF NOT EXISTS world_facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity TEXT,
        fact TEXT,
        category TEXT,
        source TEXT,
        verified BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # User Data table — user ke baare me sab
    c.execute("""CREATE TABLE IF NOT EXISTS user_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # Code History table — likha hua code yaad
    c.execute("""CREATE TABLE IF NOT EXISTS code_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language TEXT,
        code TEXT,
        purpose TEXT,
        result TEXT,
        success BOOLEAN,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # Mistakes table — galtiyan yaad
    c.execute("""CREATE TABLE IF NOT EXISTS mistakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        error TEXT,
        fix TEXT,
        learned BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    conn.commit()
    conn.close()
    return "Database initialized successfully!"


# ===================== KNOWLEDGE =====================
def add_knowledge(topic, content, source="AI", category="general", confidence=0.7):
    conn = _get_db()
    c = conn.cursor()
    c.execute("INSERT INTO knowledge (topic, content, source, category, confidence) VALUES (?,?,?,?,?)",
              (topic, content, source, category, confidence))
    conn.commit()
    conn.close()


def search_knowledge(query, limit=10):
    conn = _get_db()
    c = conn.cursor()
    c.execute("""SELECT * FROM knowledge
                 WHERE topic LIKE ? OR content LIKE ?
                 ORDER BY confidence DESC, access_count DESC
                 LIMIT ?""",
              (f"%{query}%", f"%{query}%", limit))
    results = [dict(r) for r in c.fetchall()]

    # Update access count
    for r in results:
        c.execute("UPDATE knowledge SET access_count = access_count + 1, accessed_at = CURRENT_TIMESTAMP WHERE id = ?",
                  (r['id'],))
    conn.commit()
    conn.close()
    return results


def get_knowledge_count():
    conn = _get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM knowledge")
    count = c.fetchone()[0]
    conn.close()
    return count


# ===================== CONVERSATIONS =====================
def save_conversation(session_id, role, content):
    conn = _get_db()
    c = conn.cursor()
    c.execute("INSERT INTO conversations (session_id, role, content) VALUES (?,?,?)",
              (session_id, role, content))
    conn.commit()
    conn.close()


def get_conversations(session_id, limit=50):
    conn = _get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
              (session_id, limit))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return list(reversed(results))


# ===================== SKILLS =====================
def learn_skill(skill_name, description, learned_from="interaction"):
    conn = _get_db()
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO skills (skill_name, description, proficiency, learned_from, times_used, last_used)
                 VALUES (?, ?, COALESCE((SELECT proficiency + 0.1 FROM skills WHERE skill_name = ?), 0.5), ?, COALESCE((SELECT times_used FROM skills WHERE skill_name = ?), 0), CURRENT_TIMESTAMP)""",
              (skill_name, description, skill_name, learned_from, skill_name))
    conn.commit()
    conn.close()


def use_skill(skill_name):
    conn = _get_db()
    c = conn.cursor()
    c.execute("UPDATE skills SET times_used = times_used + 1, proficiency = MIN(proficiency + 0.05, 1.0), last_used = CURRENT_TIMESTAMP WHERE skill_name = ?",
              (skill_name,))
    conn.commit()
    conn.close()


def get_skills():
    conn = _get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM skills ORDER BY proficiency DESC")
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results


# ===================== PATTERNS =====================
def save_pattern(pattern_type, input_pattern, output_pattern):
    conn = _get_db()
    c = conn.cursor()
    c.execute("INSERT INTO patterns (pattern_type, input_pattern, output_pattern) VALUES (?,?,?)",
              (pattern_type, input_pattern, output_pattern))
    conn.commit()
    conn.close()


def find_pattern(input_text):
    conn = _get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM patterns WHERE input_pattern LIKE ? ORDER BY success_rate DESC LIMIT 5",
              (f"%{input_text}%",))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results


# ===================== WORLD FACTS =====================
def add_fact(entity, fact, category="general", source="web"):
    conn = _get_db()
    c = conn.cursor()
    c.execute("INSERT INTO world_facts (entity, fact, category, source) VALUES (?,?,?,?)",
              (entity, fact, category, source))
    conn.commit()
    conn.close()


def search_facts(query, limit=10):
    conn = _get_db()
    c = conn.cursor()
    c.execute("""SELECT * FROM world_facts
                 WHERE entity LIKE ? OR fact LIKE ?
                 ORDER BY verified DESC LIMIT ?""",
              (f"%{query}%", f"%{query}%", limit))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results


# ===================== USER DATA =====================
def set_user_data(key, value):
    conn = _get_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_data (key, value, updated_at) VALUES (?,?,CURRENT_TIMESTAMP)",
              (key, json.dumps(value) if not isinstance(value, str) else value))
    conn.commit()
    conn.close()


def get_user_data(key=None):
    conn = _get_db()
    c = conn.cursor()
    if key:
        c.execute("SELECT * FROM user_data WHERE key = ?", (key,))
    else:
        c.execute("SELECT * FROM user_data")
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results if not key else (results[0] if results else None)


# ===================== CODE HISTORY =====================
def save_code(language, code, purpose, result, success):
    conn = _get_db()
    c = conn.cursor()
    c.execute("INSERT INTO code_history (language, code, purpose, result, success) VALUES (?,?,?,?,?)",
              (language, code, purpose, result, success))
    conn.commit()
    conn.close()


def get_code_history(limit=20):
    conn = _get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM code_history ORDER BY created_at DESC LIMIT ?", (limit,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results


# ===================== MISTAKES =====================
def save_mistake(task, error, fix=""):
    conn = _get_db()
    c = conn.cursor()
    c.execute("INSERT INTO mistakes (task, error, fix) VALUES (?,?,?)",
              (task, error, fix))
    conn.commit()
    conn.close()


def get_mistakes(limit=20):
    conn = _get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM mistakes ORDER BY created_at DESC LIMIT ?", (limit,))
    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results


# ===================== STATS =====================
def get_stats():
    conn = _get_db()
    c = conn.cursor()

    stats = {}
    for table in ["knowledge", "conversations", "skills", "patterns", "world_facts", "user_data", "code_history", "mistakes"]:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = c.fetchone()[0]

    conn.close()
    return stats


# Initialize on import
init_database()