"""
EmptyNSpace AGI - Auto Learning Engine
AI teaches ITSELF by asking questions to LLM!

Created by Nikhil Jatav
"""

import time
import json
import os
import re
import random
import hashlib
import sqlite3
import requests
from datetime import datetime


OLLAMA_URL = 'http://localhost:11434/api/chat'
MODEL = 'llama3.2:1b'


class SimpleMemory:
    """Simple memory if AGI_Memory not available"""
    def __init__(self):
        os.makedirs('data', exist_ok=True)
        self.conn = sqlite3.connect('data/auto_brain.db', check_same_thread=False)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT, key TEXT, value TEXT,
            source TEXT, confidence REAL DEFAULT 0.5,
            times_used INTEGER DEFAULT 0,
            created TEXT, updated TEXT
        )''')
        self.conn.commit()

    def learn_fact(self, category, key, value, source='auto'):
        now = datetime.now().isoformat()
        c = self.conn.cursor()
        c.execute('SELECT id, confidence FROM facts WHERE key=?', (key.lower(),))
        existing = c.fetchone()
        if existing:
            c.execute('UPDATE facts SET value=?, confidence=MIN(confidence+0.1,1.0), times_used=times_used+1, updated=? WHERE id=?',
                     (value, now, existing[0]))
        else:
            c.execute('INSERT INTO facts (category,key,value,source,confidence,created,updated) VALUES (?,?,?,?,0.5,?,?)',
                     (category, key.lower(), value, source, now, now))
        self.conn.commit()

    def get_all_facts(self, limit=100):
        c = self.conn.cursor()
        c.execute('SELECT category,key,value,confidence,times_used FROM facts ORDER BY confidence DESC LIMIT ?', (limit,))
        return [{'category':r[0],'key':r[1],'value':r[2],'confidence':r[3],'times_used':r[4]} for r in c.fetchall()]

    def get_brain_stats(self):
        c = self.conn.cursor()
        c.execute('SELECT COUNT(*) FROM facts')
        facts = c.fetchone()[0]
        c.execute('SELECT AVG(confidence) FROM facts')
        avg = c.fetchone()[0] or 0
        return {'facts_known': facts, 'avg_confidence': round(avg, 2)}


class AutoLearner:
    """
    AI that teaches ITSELF!

    Process:
    1. Pick topic
    2. Generate smart question
    3. Ask LLM for answer
    4. Extract facts from answer
    5. Store in permanent memory
    6. Discover new topics from answer
    7. Repeat!
    """

    def __init__(self, memory=None):
        if memory is None:
            try:
                from agi_core import AGI_Memory
                self.memory = AGI_Memory()
            except:
                self.memory = SimpleMemory()
        else:
            self.memory = memory

        self.is_running = False
        self.questions_asked = 0
        self.facts_learned = 0
        self.session_log = []

        self.seed_topics = [
            'artificial intelligence', 'machine learning', 'neural networks',
            'python programming', 'computer science', 'deep learning',
            'natural language processing', 'computer vision', 'robotics',
            'data science', 'algorithms', 'mathematics', 'physics',
            'biology', 'chemistry', 'history of computing', 'internet',
            'cloud computing', 'cybersecurity', 'quantum computing',
            'blockchain', 'space exploration', 'genetics', 'economics',
            'psychology', 'philosophy', 'music theory', 'astronomy',
            'medicine', 'engineering', 'statistics', 'databases',
            'operating systems', 'web development', 'mobile apps',
            'game development', 'virtual reality', 'climate science',
            'renewable energy', 'nanotechnology'
        ]

        self.question_templates = [
            "What is {topic}?",
            "How does {topic} work?",
            "What are the main types of {topic}?",
            "What is the history of {topic}?",
            "What are the applications of {topic}?",
            "What are the advantages of {topic}?",
            "What are the challenges in {topic}?",
            "Who invented or created {topic}?",
            "What are the key concepts in {topic}?",
            "How is {topic} used in the real world?",
            "What is the future of {topic}?",
            "Explain {topic} in simple terms.",
            "What are 5 important facts about {topic}?",
            "What are the latest developments in {topic}?",
            "How does {topic} relate to artificial intelligence?"
        ]

        self.advanced_templates = [
            "What is the mathematical foundation of {topic}?",
            "How has {topic} evolved over the last decade?",
            "What are the current research challenges in {topic}?",
            "Compare {topic} with similar approaches.",
            "What are the ethical implications of {topic}?",
            "How does {topic} impact society?",
            "What skills are needed to work in {topic}?",
            "What tools and frameworks are used in {topic}?",
            "What are common misconceptions about {topic}?",
            "How do experts learn {topic}?"
        ]

    def _ask_llm(self, question):
        """Ask LLM a question"""
        try:
            r = requests.post(OLLAMA_URL, json={
                'model': MODEL,
                'messages': [
                    {"role": "system", "content": "You are a knowledgeable teacher. Give clear, factual answers using 'X is Y' format. Be concise but informative. Include specific facts, dates, and names."},
                    {"role": "user", "content": question}
                ],
                'stream': False
            }, timeout=60)

            if r.status_code == 200:
                return r.json().get('message', {}).get('content', '')
            return None
        except:
            return None

    def _extract_facts(self, text, topic):
        """Extract facts from LLM answer"""
        if not text:
            return 0

        facts_count = 0
        sentences = re.split(r'[.!?]\s+', text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 15 or len(sentence) > 500:
                continue

            skip = ['click', 'subscribe', 'cookie', 'privacy', 'http']
            if any(w in sentence.lower() for w in skip):
                continue

            # Pattern: "X is Y"
            match = re.search(r'^(.{3,60}?)\s+is\s+(.{10,300})', sentence, re.IGNORECASE)
            if match:
                key = re.sub(r'^(the|a|an)\s+', '', match.group(1).strip(), flags=re.IGNORECASE)
                value = match.group(2).strip()
                if len(key) > 3 and len(value) > 10:
                    self.memory.learn_fact('auto_learned', key, value, f'auto:{topic}')
                    facts_count += 1
                    continue

            # Pattern: "X are Y"
            match = re.search(r'^(.{3,60}?)\s+are\s+(.{10,300})', sentence, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                if len(key) > 3:
                    self.memory.learn_fact('auto_learned', key, 'are ' + match.group(2).strip(), f'auto:{topic}')
                    facts_count += 1
                    continue

            # Pattern: "X was Y"
            match = re.search(r'^(.{3,60}?)\s+was\s+(.{10,300})', sentence, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                if len(key) > 3:
                    self.memory.learn_fact('auto_learned', key, 'was ' + match.group(2).strip(), f'auto:{topic}')
                    facts_count += 1
                    continue

            # Pattern: "X means Y"
            match = re.search(r'^(.{3,60}?)\s+means?\s+(.{10,300})', sentence, re.IGNORECASE)
            if match:
                self.memory.learn_fact('auto_learned', match.group(1).strip(), match.group(2).strip(), f'auto:{topic}')
                facts_count += 1
                continue

            # Topic-related sentence
            if topic.lower().split()[0] in sentence.lower() and len(sentence) > 30:
                self.memory.learn_fact('auto_learned', f"{topic}_info", sentence[:300], f'auto:{topic}')
                facts_count += 1

        return facts_count

    def _discover_topics(self, text):
        """Find new topics from answer"""
        new = []
        caps = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text)
        for cap in caps:
            if 4 < len(cap) < 40 and cap.lower() not in [t.lower() for t in self.seed_topics]:
                new.append(cap)
        return list(set(new))[:5]

    def _smart_pick_topic(self, explored):
        """Pick unexplored topic"""
        unexplored = [t for t in self.seed_topics if t.lower() not in explored]
        if unexplored and random.random() < 0.5:
            return random.choice(unexplored)

        facts = self.memory.get_all_facts(50)
        if facts and random.random() < 0.3:
            fact = random.choice(facts)
            topic = fact['key'].replace('_info', '').replace('_', ' ').strip()
            if len(topic) > 3 and topic.lower() not in explored:
                return topic

        return random.choice(self.seed_topics)

    def _smart_question(self, topic, asked):
        """Generate unique question"""
        all_templates = self.question_templates + self.advanced_templates
        random.shuffle(all_templates)
        for t in all_templates:
            q = t.format(topic=topic)
            if q.lower() not in asked:
                return q
        return f"Tell me important facts about {topic}"

    def learn_one(self, asked_set=None):
        """Learn one thing"""
        if asked_set is None:
            asked_set = set()

        topic = self._smart_pick_topic(set())
        question = self._smart_question(topic, asked_set)

        print(f"   🤔 Q: {question[:60]}...")

        answer = self._ask_llm(question)
        if not answer:
            return 0, topic

        facts = self._extract_facts(answer, topic)
        new_topics = self._discover_topics(answer)
        self.seed_topics.extend(new_topics)

        self.questions_asked += 1
        self.facts_learned += facts

        print(f"   📚 Learned: {facts} facts | New topics: {len(new_topics)}")
        return facts, topic

    def infinite_learn(self, batch_size=10, delay=1, max_total=10000):
        """
        CONTINUOUS LEARNING!
        Runs until stopped or max reached!
        """
        self.is_running = True
        self.questions_asked = 0
        self.facts_learned = 0

        asked = set()
        explored = set()

        stats_before = self.memory.get_brain_stats()
        start_time = time.time()

        print(f"\n{'🧠' * 20}")
        print(f"  INFINITE LEARNING MODE!")
        print(f"{'🧠' * 20}")
        print(f"\n   Brain: {stats_before['facts_known']} facts")
        print(f"   Limit: {max_total} questions")
        print(f"   Ctrl+C to stop!\n")

        batch = 0

        try:
            while self.is_running and self.questions_asked < max_total:
                batch += 1
                batch_facts = 0

                print(f"\n📦 Batch {batch}:")

                for i in range(batch_size):
                    if not self.is_running or self.questions_asked >= max_total:
                        break

                    topic = self._smart_pick_topic(explored)
                    question = self._smart_question(topic, asked)

                    if question.lower() in asked:
                        continue

                    asked.add(question.lower())
                    explored.add(topic.lower())

                    print(f"   🤔 Q: {question[:55]}...")

                    answer = self._ask_llm(question)

                    if answer:
                        facts = self._extract_facts(answer, topic)
                        batch_facts += facts
                        self.facts_learned += facts

                        new_topics = self._discover_topics(answer)
                        self.seed_topics.extend(new_topics)

                        print(f"   📚 +{facts} facts")
                    else:
                        print(f"   ❌ No answer")

                    self.questions_asked += 1
                    time.sleep(delay)

                # Batch summary
                current = self.memory.get_brain_stats()
                elapsed = (time.time() - start_time) / 60

                print(f"\n   ✅ Batch {batch}: +{batch_facts} facts")
                print(f"   📊 Total: {current['facts_known']} facts | "
                      f"{self.questions_asked} Qs | "
                      f"{elapsed:.1f} min | "
                      f"Topics: {len(explored)}")

                # Save progress
                try:
                    with open('data/learn_progress.json', 'w') as f:
                        json.dump({
                            'time': datetime.now().isoformat(),
                            'questions': self.questions_asked,
                            'facts': self.facts_learned,
                            'topics': len(explored),
                            'brain_size': current['facts_known']
                        }, f)
                except:
                    pass

        except KeyboardInterrupt:
            print(f"\n\n⏹ Stopped!")

        self.is_running = False

        # Final report
        stats_after = self.memory.get_brain_stats()
        total_time = (time.time() - start_time) / 60

        print(f"\n{'='*60}")
        print(f"🏆 LEARNING COMPLETE!")
        print(f"{'='*60}")
        print(f"   Time:      {total_time:.1f} minutes")
        print(f"   Questions: {self.questions_asked}")
        print(f"   Facts:     {self.facts_learned}")
        print(f"   Topics:    {len(explored)}")
        print(f"   Before:    {stats_before['facts_known']} facts")
        print(f"   After:     {stats_after['facts_known']} facts")
        print(f"   NEW:       {stats_after['facts_known'] - stats_before['facts_known']} facts!")
        print(f"   Rate:      {self.facts_learned/max(total_time,0.1):.0f} facts/min")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    print(f"\n{'🤖' * 20}")
    print(f"  EmptyNSpace Auto-Learner")
    print(f"{'🤖' * 20}")

    # Check Ollama
    try:
        r = requests.get('http://localhost:11434/api/tags', timeout=3)
        if r.status_code != 200:
            print("\n❌ Ollama not running!")
            exit()
        print("\n✅ Ollama connected!")
    except:
        print("\n❌ Ollama not running! Start: ollama serve")
        exit()

    learner = AutoLearner()
    stats = learner.memory.get_brain_stats()
    print(f"📊 Brain: {stats['facts_known']} facts\n")

    print("Choose mode:")
    print("  1. Quick    (10 questions, ~30 sec)")
    print("  2. Medium   (50 questions, ~3 min)")
    print("  3. Long     (200 questions, ~12 min)")
    print("  4. INFINITE (until Ctrl+C!)")

    choice = input("\nEnter 1-4: ").strip()

    if choice == '1':
        learner.infinite_learn(batch_size=5, max_total=10, delay=1)
    elif choice == '2':
        learner.infinite_learn(batch_size=10, max_total=50, delay=1)
    elif choice == '3':
        learner.infinite_learn(batch_size=10, max_total=200, delay=1)
    elif choice == '4':
        learner.infinite_learn(batch_size=10, max_total=10000, delay=1)
    else:
        learner.infinite_learn(batch_size=5, max_total=10, delay=1)

    final = learner.memory.get_brain_stats()
    print(f"📊 Final brain: {final['facts_known']} facts")
    print("✅ Done!")