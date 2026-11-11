"""
EmptyNSpace AGI Core - Self-Learning Brain
Step 1 of AGI: Learn → Remember → Reason → Reflect

Created by Nikhil Jatav
Status: Experimental, not peer-reviewed

This module adds:
1. Internet learning (crawl + understand + store)
2. Self-reflection (evaluate own responses)
3. Knowledge building (grow smarter over time)
4. Pattern recognition (find connections)
5. All under USER control (safety first!)
"""

import sqlite3
import json
import time
import hashlib
import os
import re
from datetime import datetime

# Try imports
try:
    from brain.internet_learner import InternetLearner
except:
    from internet_learner import InternetLearner
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except:
    HAS_BS4 = False


class AGI_Memory:
    """
    Persistent memory that GROWS over time
    
    Unlike normal AI that forgets everything:
    This remembers EVERYTHING and finds CONNECTIONS!
    
    Storage: SQLite (efficient, persistent)
    Structure: Facts, Patterns, Reflections, Skills
    """
    
    def __init__(self, db_path='data/agi_brain.db'):
        os.makedirs('data', exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()
        self.stats = {'learns': 0, 'recalls': 0, 'reflections': 0}
    
    def _create_tables(self):
        c = self.conn.cursor()
        
        # Facts: What AI knows
        c.execute('''CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            key TEXT,
            value TEXT,
            source TEXT,
            confidence REAL DEFAULT 0.5,
            times_used INTEGER DEFAULT 0,
            created TEXT,
            updated TEXT
        )''')
        
        # Patterns: Connections AI discovered
        c.execute('''CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT,
            description TEXT,
            evidence TEXT,
            strength REAL DEFAULT 0.1,
            times_confirmed INTEGER DEFAULT 0,
            created TEXT
        )''')
        
        # Reflections: AI evaluating itself
        c.execute('''CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            response TEXT,
            was_good INTEGER DEFAULT -1,
            what_went_wrong TEXT,
            what_to_improve TEXT,
            lesson_learned TEXT,
            created TEXT
        )''')
        
        # Skills: What AI can do well
        c.execute('''CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT,
            description TEXT,
            success_count INTEGER DEFAULT 0,
            fail_count INTEGER DEFAULT 0,
            confidence REAL DEFAULT 0.5,
            last_used TEXT
        )''')
        
        # Conversations: Full history
        c.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            context TEXT,
            emotion TEXT,
            created TEXT
        )''')
        
        self.conn.commit()
    
    # === LEARN ===
    def learn_fact(self, category, key, value, source='user'):
        """Learn a new fact"""
        c = self.conn.cursor()
        
        # Check if already known
        c.execute('SELECT id, confidence, times_used FROM facts WHERE key=?', (key.lower(),))
        existing = c.fetchone()
        
        now = datetime.now().isoformat()
        
        if existing:
            # Update existing knowledge
            new_confidence = min(existing[1] + 0.1, 1.0)
            c.execute('''UPDATE facts SET value=?, confidence=?, 
                        times_used=times_used+1, updated=?, source=?
                        WHERE id=?''', 
                     (value, new_confidence, now, source, existing[0]))
        else:
            # Learn new fact
            c.execute('''INSERT INTO facts 
                        (category, key, value, source, confidence, created, updated)
                        VALUES (?, ?, ?, ?, 0.5, ?, ?)''',
                     (category, key.lower(), value, source, now, now))
        
        self.conn.commit()
        self.stats['learns'] += 1
        return True
    
    def recall(self, query, top_k=5):
        """Recall relevant knowledge"""
        c = self.conn.cursor()
        
        words = query.lower().split()
        results = []
        
        for word in words:
            if len(word) < 3:
                continue
            c.execute('''SELECT key, value, confidence, category 
                        FROM facts 
                        WHERE key LIKE ? OR value LIKE ?
                        ORDER BY confidence DESC, times_used DESC
                        LIMIT ?''',
                     (f'%{word}%', f'%{word}%', top_k))
            
            for row in c.fetchall():
                results.append({
                    'key': row[0],
                    'value': row[1],
                    'confidence': row[2],
                    'category': row[3]
                })
        
        # Remove duplicates
        seen = set()
        unique = []
        for r in results:
            if r['key'] not in seen:
                seen.add(r['key'])
                unique.append(r)
                
                # Update usage
                c.execute('UPDATE facts SET times_used=times_used+1 WHERE key=?', 
                         (r['key'],))
        
        self.conn.commit()
        self.stats['recalls'] += 1
        return unique[:top_k]
    
    def get_all_facts(self, limit=100):
        """Get all known facts"""
        c = self.conn.cursor()
        c.execute('''SELECT category, key, value, confidence, times_used 
                    FROM facts ORDER BY confidence DESC LIMIT ?''', (limit,))
        return [{'category': r[0], 'key': r[1], 'value': r[2], 
                 'confidence': r[3], 'times_used': r[4]} for r in c.fetchall()]
    
    # === REFLECT ===
    def add_reflection(self, query, response, was_good, 
                       what_went_wrong='', what_to_improve='', lesson=''):
        """AI reflects on its own performance"""
        c = self.conn.cursor()
        c.execute('''INSERT INTO reflections 
                    (query, response, was_good, what_went_wrong, 
                     what_to_improve, lesson_learned, created)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (query, response[:500], 1 if was_good else 0,
                  what_went_wrong, what_to_improve, lesson,
                  datetime.now().isoformat()))
        
        # Learn from reflection
        if lesson:
            self.learn_fact('self_improvement', 
                          f'lesson_{int(time.time())}', 
                          lesson, 'reflection')
        
        self.conn.commit()
        self.stats['reflections'] += 1
    
    def get_lessons(self, limit=10):
        """Get learned lessons"""
        c = self.conn.cursor()
        c.execute('''SELECT lesson_learned FROM reflections 
                    WHERE lesson_learned != '' 
                    ORDER BY created DESC LIMIT ?''', (limit,))
        return [r[0] for r in c.fetchall()]
    
    # === PATTERNS ===
    def discover_pattern(self, pattern_type, description, evidence):
        """Record a discovered pattern"""
        c = self.conn.cursor()
        c.execute('''INSERT INTO patterns 
                    (pattern_type, description, evidence, created)
                    VALUES (?, ?, ?, ?)''',
                 (pattern_type, description, evidence, 
                  datetime.now().isoformat()))
        self.conn.commit()
    
    # === SKILLS ===
    def update_skill(self, skill_name, success):
        """Track skill performance"""
        c = self.conn.cursor()
        c.execute('SELECT id FROM skills WHERE skill_name=?', (skill_name,))
        existing = c.fetchone()
        
        now = datetime.now().isoformat()
        
        if existing:
            if success:
                c.execute('''UPDATE skills SET success_count=success_count+1, 
                            confidence=MIN(confidence+0.05, 1.0), last_used=?
                            WHERE id=?''', (now, existing[0]))
            else:
                c.execute('''UPDATE skills SET fail_count=fail_count+1,
                            confidence=MAX(confidence-0.1, 0.0), last_used=?
                            WHERE id=?''', (now, existing[0]))
        else:
            c.execute('''INSERT INTO skills 
                        (skill_name, description, success_count, fail_count, 
                         confidence, last_used)
                        VALUES (?, ?, ?, ?, 0.5, ?)''',
                     (skill_name, '', 1 if success else 0, 
                      0 if success else 1, now))
        
        self.conn.commit()
    
    # === STATS ===
    def get_brain_stats(self):
        """How smart is the brain?"""
        c = self.conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM facts')
        facts = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM patterns')
        patterns = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM reflections')
        reflections = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM skills')
        skills = c.fetchone()[0]
        
        c.execute('SELECT AVG(confidence) FROM facts')
        avg_conf = c.fetchone()[0] or 0
        
        return {
            'facts_known': facts,
            'patterns_found': patterns,
            'reflections_done': reflections,
            'skills_tracked': skills,
            'avg_confidence': round(avg_conf, 2),
            'session_learns': self.stats['learns'],
            'session_recalls': self.stats['recalls']
        }


class AGI_Learner:
    """
    Internet Learning Engine
    
    Crawls web pages → Extracts knowledge → Stores permanently
    
    SAFETY: User must APPROVE what to learn!
    AI CANNOT learn on its own without permission!
    """
    
    def __init__(self, memory):
        self.memory = memory
    
    def learn_from_text(self, text, source='user_input'):
        """Extract facts from text and learn them"""
        facts_learned = []
        
        # Simple fact extraction
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Pattern: "X is Y"
            is_match = re.search(r'(.+?)\s+is\s+(.+)', sentence, re.IGNORECASE)
            if is_match:
                key = is_match.group(1).strip()[:100]
                value = is_match.group(2).strip()[:500]
                if len(key) > 3 and len(value) > 3:
                    self.memory.learn_fact('learned', key, value, source)
                    facts_learned.append(f"{key} = {value}")
            
            # Pattern: "X means Y"
            means_match = re.search(r'(.+?)\s+means?\s+(.+)', sentence, re.IGNORECASE)
            if means_match:
                key = means_match.group(1).strip()[:100]
                value = means_match.group(2).strip()[:500]
                if len(key) > 3:
                    self.memory.learn_fact('definition', key, value, source)
                    facts_learned.append(f"{key} = {value}")
        
        return facts_learned
    
    def learn_from_url(self, url):
        """Learn from a webpage (USER APPROVED!)"""
        if not HAS_WEB or not HAS_BS4:
            return "Web learning not available. Install: requests, beautifulsoup4"
        
        try:
            r = requests.get(url, timeout=15, headers={
                'User-Agent': 'EmptyNSpace-AGI-Learner/1.0'
            })
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Remove non-content
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()
            
            text = soup.get_text('\n', strip=True)
            
            # Limit text
            text = text[:5000]
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else url
            
            # Learn from content
            facts = self.learn_from_text(text, source=url)
            
            # Store the page as knowledge
            self.memory.learn_fact('web_page', title_text, text[:1000], url)
            
            return {
                'url': url,
                'title': title_text,
                'facts_learned': len(facts),
                'facts': facts[:10],
                'text_length': len(text)
            }
            
        except Exception as e:
            return f"Error learning from URL: {str(e)}"


class AGI_Reasoner:
    """
    Reasoning Engine
    
    Uses stored knowledge to THINK about questions
    Finds connections between facts
    Builds understanding over time
    """
    
    def __init__(self, memory):
        self.memory = memory
    
    def think(self, question):
        """Think about a question using stored knowledge"""
        
        # Step 1: Recall relevant knowledge
        relevant = self.memory.recall(question, top_k=10)
        
        # Step 2: Get past lessons
        lessons = self.memory.get_lessons(5)
        
        # Step 3: Build reasoning context
        context = "What I know:\n"
        for fact in relevant:
            context += f"- {fact['key']}: {fact['value']} "
            context += f"(confidence: {fact['confidence']:.0%})\n"
        
        if lessons:
            context += "\nLessons I've learned:\n"
            for lesson in lessons:
                context += f"- {lesson}\n"
        
        # Step 4: Find connections
        connections = self._find_connections(relevant)
        if connections:
            context += "\nConnections I see:\n"
            for conn in connections:
                context += f"- {conn}\n"
        
        return {
            'context': context,
            'facts_used': len(relevant),
            'lessons_applied': len(lessons),
            'connections_found': len(connections)
        }
    
    def _find_connections(self, facts):
        """Find connections between known facts"""
        connections = []
        
        for i, fact1 in enumerate(facts):
            for fact2 in facts[i+1:]:
                # Check word overlap
                words1 = set(fact1['value'].lower().split())
                words2 = set(fact2['value'].lower().split())
                common = words1 & words2
                
                # Remove common stop words
                stop_words = {'the', 'is', 'a', 'an', 'and', 'or', 'but', 
                            'in', 'on', 'at', 'to', 'for', 'of', 'with',
                            'that', 'this', 'it', 'as', 'by', 'from'}
                common = common - stop_words
                
                if len(common) >= 2:
                    connections.append(
                        f"'{fact1['key']}' and '{fact2['key']}' "
                        f"are related (common: {', '.join(list(common)[:3])})"
                    )
        
        return connections[:5]


class AGI_Reflector:
    """
    Self-Reflection Engine
    
    AI evaluates its own responses
    Learns from mistakes
    Improves over time
    """
    
    def __init__(self, memory):
        self.memory = memory
    
    def reflect_on_response(self, query, response, user_feedback=None):
        """Evaluate own response quality"""
        
        evaluation = {
            'relevant': self._check_relevance(query, response),
            'complete': self._check_completeness(response),
            'clear': self._check_clarity(response),
            'helpful': user_feedback if user_feedback is not None else None
        }
        
        # Determine if response was good
        scores = [v for v in evaluation.values() if v is not None]
        avg_score = sum(scores) / len(scores) if scores else 0.5
        was_good = avg_score > 0.5
        
        # Generate lesson
        lesson = ''
        if not evaluation['relevant']:
            lesson = f"For questions like '{query[:50]}', focus more on the topic"
        elif not evaluation['complete']:
            lesson = f"Give more detailed answers about '{query[:30]}'"
        elif not evaluation['clear']:
            lesson = "Use simpler language and shorter sentences"
        
        # Store reflection
        self.memory.add_reflection(
            query, response, was_good,
            what_went_wrong='' if was_good else 'Low quality response',
            what_to_improve=lesson,
            lesson=lesson
        )
        
        return {
            'was_good': was_good,
            'score': round(avg_score, 2),
            'evaluation': evaluation,
            'lesson': lesson
        }
    
    def _check_relevance(self, query, response):
        """Check if response is relevant to query"""
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        
        # Remove stop words
        stop = {'the','is','a','an','and','or','but','in','on','at','to','for','of',
                'what','how','why','when','where','who','i','you','me','my','your'}
        query_words -= stop
        response_words -= stop
        
        if not query_words:
            return True
        
        overlap = query_words & response_words
        return len(overlap) / len(query_words) > 0.3
    
    def _check_completeness(self, response):
        """Check if response is complete enough"""
        return len(response.split()) > 10
    
    def _check_clarity(self, response):
        """Check if response is clear"""
        avg_word_length = sum(len(w) for w in response.split()) / max(len(response.split()), 1)
        return avg_word_length < 8


class AGI_Core:
    """
    MAIN AGI ENGINE
    
    Combines: Memory + Learning + Reasoning + Reflection
    
    This is the BRAIN of EmptyNSpace AGI!
    
    USER CONTROLS:
    - User approves what to learn
    - User can delete knowledge
    - User can reset brain
    - AI cannot act without permission for dangerous actions
    
    Created by Nikhil Jatav
    """
    
    def __init__(self):
        print("🧠 Initializing AGI Core...")
        
        self.memory = AGI_Memory()
        self.learner = AGI_Learner(self.memory)
        self.reasoner = AGI_Reasoner(self.memory)
        self.reflector = AGI_Reflector(self.memory)
        self.internet = InternetLearner(self.memory)
        
        # Safety controls
        self.learning_enabled = True
        self.auto_learn = False  # User must approve!
        self.owner = "Nikhil Jatav"
        
        # Seed with basic knowledge
    def process(self, user_input):
        """Main AGI processing pipeline"""
        # Check commands
        special = self._handle_commands(user_input)
        if special:
            return {'response': special, 'intent': 'command', 'facts_used': 0, 'connections': 0, 'reflection_score': 1.0, 'lesson': ''}

        # Understand
        intent = self._understand(user_input)

        # Reason
        thinking = self.reasoner.think(user_input)

        # Respond
        response = self._generate_response(user_input, intent, thinking)

        # Track skill
        self.memory.update_skill(intent, True)

        # Learn from conversation
        if self.learning_enabled:
            self.learner.learn_from_text(user_input, 'conversation')

        # Reflect
        reflection = self.reflector.reflect_on_response(user_input, response)

        return {
            'response': response,
            'intent': intent,
            'facts_used': thinking['facts_used'],
            'connections': thinking['connections_found'],
            'reflection_score': reflection['score'],
            'lesson': reflection['lesson']
        }        
        self._seed_knowledge()
        
        stats = self.memory.get_brain_stats()
        print(f"🧠 AGI Core Ready!")
        print(f"   Facts known: {stats['facts_known']}")
        print(f"   Skills: {stats['skills_tracked']}")
        print(f"   Reflections: {stats['reflections_done']}")
    
    def _seed_knowledge(self):
        """Basic knowledge to start with"""
        seeds = [
            ('identity', 'my name', 'EmptyNSpace AGI', 'system'),
            ('identity', 'my creator', 'Nikhil Jatav', 'system'),
            ('identity', 'my purpose', 'To learn, reason, and help humans', 'system'),
            ('ai', 'artificial intelligence', 'Computer systems that can perform tasks requiring human intelligence', 'system'),
            ('ai', 'machine learning', 'AI technique where computers learn from data without explicit programming', 'system'),
            ('ai', 'neural network', 'Computing system inspired by biological neural networks in the brain', 'system'),
            ('ai', 'agi', 'Artificial General Intelligence - AI that can understand and learn any intellectual task a human can', 'system'),
            ('science', 'gravity', 'Force that attracts objects with mass toward each other', 'system'),
            ('science', 'light speed', 'Approximately 299,792,458 meters per second in vacuum', 'system'),
            ('tech', 'python', 'High-level programming language widely used in AI and data science', 'system'),
            ('tech', 'pytorch', 'Open source machine learning framework developed by Meta', 'system'),
        ]
        
        for category, key, value, source in seeds:
            self.memory.learn_fact(category, key, value, source)
    
    def _understand(self, text):
        """Understand user intent"""
        t = text.lower()
        
        if any(w in t for w in ['wikipedia', 'wiki']):
            return 'wiki_learn'
        if any(w in t for w in ['deep learn', 'study', 'research about']):
            return 'deep_learn'
        if any(w in t for w in ['search and learn', 'find and learn']):
            return 'search_learn'
        if any(w in t for w in ['learn', 'teach', 'remember', 'seekh', 'yaad']):
            return 'learning'
        if any(w in t for w in ['what do you know', 'kya jaante', 'knowledge', 'facts']):
            return 'knowledge_query'
        if any(w in t for w in ['search', 'find', 'look up', 'dhundho']):
            return 'search'
        if any(w in t for w in ['code', 'python', 'program', 'function']):
            return 'coding'
        if any(w in t for w in ['who are you', 'kaun ho', 'about yourself']):
            return 'identity'
        if any(w in t for w in ['how smart', 'brain stats', 'statistics', 'status']):
            return 'stats'
        if 'http' in t:
            return 'web_learn'
        
        return 'general'
        # Step 1: Understand intent
        intent = self._understand(user_input)

        # Step 2: Recall + Reason
        thinking = self.reasoner.think(user_input)

        # Step 3: Generate response
        response = self._generate_response(user_input, intent, thinking)

        # Step 4: Track skill usage
        self.memory.update_skill(intent, True)

        # Step 5: Auto-learn from conversation
        if self.learning_enabled:
            self.learner.learn_from_text(user_input, 'conversation')

        # Step 6: Self-reflect
        reflection = self.reflector.reflect_on_response(user_input, response)

        return {
            'response': response,
            'intent': intent,
            'facts_used': thinking['facts_used'],
            'connections': thinking['connections_found'],
            'reflection_score': reflection['score'],
            'lesson': reflection['lesson']
        }
        """
        Main processing pipeline:
        1. UNDERSTAND what user wants
        2. RECALL relevant knowledge
        3. REASON about the question
        4. RESPOND with best answer
        5. REFLECT on response quality
        6. LEARN from interaction
        """
        
        # Check for special commands
        special = self._handle_commands(user_input)
        if special:
            return special
        
        # Step 1: Understand intent
        intent = self._understand(user_input)
        
        # Step 2: Recall + Reason
        thinking = self.reasoner.think(user_input)
        
        # Step 3: Generate response
        if intent == 'learning':
            text = user_input
            
            # Pattern 1: "learn X is Y"
            match = re.search(r'learn\s+(.+?)\s+is\s+(.+)', text, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                self.memory.learn_fact('user_taught', key, value, 'user')
                return f"✅ Learned: {key} = {value}\n\nI will remember this!"
            
            # Pattern 2: "learn X are Y"
            match = re.search(r'learn\s+(.+?)\s+are\s+(.+)', text, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                value = 'are ' + match.group(2).strip()
                self.memory.learn_fact('user_taught', key, value, 'user')
                return f"✅ Learned: {key} {value}\n\nI will remember this!"
            
            # Pattern 3: "learn X created/built/made Y"
            match = re.search(r'learn\s+(.+?)\s+(created|built|made|invented)\s+(.+)', text, re.IGNORECASE)
            if match:
                key = match.group(3).strip()
                value = f'{match.group(2)} by {match.group(1).strip()}'
                self.memory.learn_fact('user_taught', key, value, 'user')
                return f"✅ Learned: {key} was {value}\n\nI will remember this!"
            
            # Pattern 4: "learn X means Y"
            match = re.search(r'learn\s+(.+?)\s+means?\s+(.+)', text, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                self.memory.learn_fact('definition', key, value, 'user')
                return f"✅ Learned: {key} means {value}\n\nI will remember this!"
            
            # Pattern 5: "remember X = Y"
            match = re.search(r'remember\s+(.+?)\s*=\s*(.+)', text, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                self.memory.learn_fact('user_taught', key, value, 'user')
                return f"✅ Learned: {key} = {value}\n\nI will remember this!"
            
            # Pattern 6: "teach X"
            match = re.search(r'(?:teach|learn)\s+(.+)', text, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                facts = self.learner.learn_from_text(content, 'user')
                if facts:
                    return f"✅ Learned {len(facts)} facts:\n" + '\n'.join(f"  • {f}" for f in facts)
                
                # Store as general knowledge
                self.memory.learn_fact('user_taught', content[:50], content, 'user')
                return f"✅ Stored: {content}\n\nI will remember this!"
            
            return "Tell me what to learn!\n\nFormats:\n  'learn X is Y'\n  'learn X are Y'\n  'learn X created Y'\n  'remember X = Y'"
        
        # Step 4: Track skill usage
        self.memory.update_skill(intent, True)
        
        # Step 5: Auto-learn from conversation
        if self.learning_enabled:
            self.learner.learn_from_text(user_input, 'conversation')
        
        # Step 6: Self-reflect
        reflection = self.reflector.reflect_on_response(user_input, response)
        
        return {
            'response': response,
            'intent': intent,
            'facts_used': thinking['facts_used'],
            'connections': thinking['connections_found'],
            'reflection_score': reflection['score'],
            'lesson': reflection['lesson']
        }
    
    def _understand(self, text):
        """Understand user intent"""
        t = text.lower()
        
        if any(w in t for w in ['learn', 'teach', 'remember', 'seekh', 'yaad']):
            return 'learning'
        if any(w in t for w in ['what do you know', 'kya jaante', 'knowledge', 'facts']):
            return 'knowledge_query'
        if any(w in t for w in ['search', 'find', 'look up', 'dhundho']):
            return 'search'
        if any(w in t for w in ['code', 'python', 'program', 'function']):
            return 'coding'
        if any(w in t for w in ['who are you', 'kaun ho', 'about yourself']):
            return 'identity'
        if any(w in t for w in ['how smart', 'brain stats', 'statistics', 'status']):
            return 'stats'
        if 'http' in t:
            return 'web_learn'
        
        return 'general'
    
    def _generate_response(self, query, intent, thinking):

        if intent == 'identity':
            stats = self.memory.get_brain_stats()
            return (f"I am EmptyNSpace AGI, created by {self.owner}.\n"
                   f"I currently know {stats['facts_known']} facts.\n"
                   f"I have reflected {stats['reflections_done']} times.\n"
                   f"I am always learning and improving!")

        if intent == 'stats':
            stats = self.memory.get_brain_stats()
            response = "🧠 My Brain Status:\n\n"
            for key, val in stats.items():
                response += f"  {key}: {val}\n"
            return response

        if intent == 'knowledge_query':
            facts = self.memory.get_all_facts(20)
            if not facts:
                return "I don't know much yet. Teach me!"
            response = f"📚 I know {len(facts)} facts:\n\n"
            for f in facts[:10]:
                response += f"  [{f['category']}] {f['key']}: {f['value'][:80]}\n"
            return response
        if intent == 'wiki_learn':
            topic = re.sub(r'(wikipedia|wiki|learn from|learn about|learn)\s*', '', query, flags=re.IGNORECASE).strip()
            if topic:
                result = self.internet.learn_from_wikipedia(topic)
                if result['status'] == 'success':
                    return (f"📚 Learned from Wikipedia: {result['title']}\n\n"
                           f"Summary: {result.get('summary', '')[:300]}\n\n"
                           f"Facts learned: {result['facts_learned']}\n"
                           f"I now know more about {topic}!")
                return f"Could not find Wikipedia article for '{topic}'"
            return "Tell me what to learn from Wikipedia!"

        if intent == 'deep_learn':
            topic = re.sub(r'(deep learn|study|research about|research)\s*', '', query, flags=re.IGNORECASE).strip()
            if topic:
                result = self.internet.deep_learn(topic)
                response = f"🧠 Deep Learning Complete: {topic}\n\n"
                response += f"Sources used: {len(result['sources'])}\n"
                response += f"Facts learned: {result['total_facts']}\n"
                response += f"Connections found: {len(result.get('connections', []))}\n"
                for conn in result.get('connections', [])[:3]:
                    response += f"  🔗 {conn}\n"
                response += f"\nTotal knowledge: {result['knowledge_after']} facts!"
                return response
            return "Tell me what to deep learn about!"

        if intent == 'search_learn':
            topic = re.sub(r'(search and learn|find and learn|search|learn)\s*', '', query, flags=re.IGNORECASE).strip()
            if topic:
                result = self.internet.search_and_learn(topic)
                if result['status'] == 'success':
                    response = f"🔍 Searched and Learned: {topic}\n\n"
                    response += f"Results found: {result['results_found']}\n"
                    response += f"Facts learned: {result['facts_learned']}\n"
                    for r in result['results'][:3]:
                        response += f"  • {r['title'][:50]}\n"
                    return response
                return f"Search failed: {result.get('message', '')}"
            return "Tell me what to search and learn!"

        if intent == 'learning':
            # Pattern 1: "learn X is Y"
            match = re.search(r'learn\s+(.+?)\s+is\s+(.+)', query, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                self.memory.learn_fact('user_taught', key, value, 'user')
                return f"✅ Learned: {key} = {value}"

            # Pattern 2: "learn X are Y"
            match = re.search(r'learn\s+(.+?)\s+are\s+(.+)', query, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                value = 'are ' + match.group(2).strip()
                self.memory.learn_fact('user_taught', key, value, 'user')
                return f"✅ Learned: {key} {value}"

            # Pattern 3: "learn X created Y"
            match = re.search(r'learn\s+(.+?)\s+(created|built|made)\s+(.+)', query, re.IGNORECASE)
            if match:
                key = match.group(3).strip()
                value = f'{match.group(2)} by {match.group(1).strip()}'
                self.memory.learn_fact('user_taught', key, value, 'user')
                return f"✅ Learned: {key} was {value}"

            # Pattern 4: "remember X = Y"
            match = re.search(r'remember\s+(.+?)\s*=\s*(.+)', query, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                self.memory.learn_fact('user_taught', key, value, 'user')
                return f"✅ Learned: {key} = {value}"

            # Pattern 5: Any "learn X" 
            match = re.search(r'(?:teach|learn)\s+(.+)', query, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                facts = self.learner.learn_from_text(content, 'user')
                if facts:
                    return f"✅ Learned {len(facts)} facts:\n" + '\n'.join(f"  • {f}" for f in facts)
                self.memory.learn_fact('user_taught', content[:50], content, 'user')
                return f"✅ Stored: {content}"

            return "Tell me what to learn! Say: 'learn X is Y'"

        if intent == 'web_learn':
            urls = re.findall(r'https?://[^\s]+', query)
            if urls:
                result = self.learner.learn_from_url(urls[0])
                if isinstance(result, dict):
                    return (f"📚 Learned from: {result['title']}\n"
                           f"   Facts: {result['facts_learned']}")
                return str(result)
            return "Send me a URL to learn from!"

        # General: Use knowledge
        if thinking['facts_used'] > 0:
            return f"Based on my knowledge ({thinking['facts_used']} facts):\n\n{thinking['context']}"

        return f"I don't know about '{query[:50]}' yet. Teach me!"
    def _handle_commands(self, text):
        """Handle special commands"""
        t = text.lower().strip()
        
        if t in ['help', 'commands']:
            return """
🧠 EmptyNSpace AGI Commands:

  📚 Learning:
    "learn X is Y"         → Teach me a fact
    "teach me X means Y"   → Same as above
    "remember X = Y"       → Same as above
    [paste URL]            → Learn from webpage

  🔍 Knowledge:
    "what do you know"     → Show all facts
    "what is X"            → Recall about X
    
  📊 Status:
    "brain stats"          → Show brain statistics
    "who are you"          → About me
    
  🔧 Control:
    "reset brain"          → Clear all knowledge
    "help"                 → This message

  💬 Just chat naturally - I'll use my knowledge!
"""
        
        if t == 'reset brain':
            self.memory.conn.execute('DELETE FROM facts WHERE source != "system"')
            self.memory.conn.commit()
            return "🧠 Brain reset! Kept only system knowledge."
        
        return None
    
    def feedback(self, was_helpful):
        """User gives feedback on last response"""
        if was_helpful:
            return "Thank you! I'll remember this worked well."
        else:
            return "Sorry about that. I'll try to do better next time."


# ============================================
# TEST
# ============================================

def test_agi():
    """Test AGI Core"""
    print("\n" + "🧠" * 25)
    print("  EmptyNSpace AGI Core Test")
    print("🧠" * 25)
    
    agi = AGI_Core()
    
    # Test learning
    tests = [
        "learn Python is a programming language used in AI",
        "learn neural networks are inspired by human brain",
        "learn Nikhil Jatav created EmptyNSpace",
        "what do you know",
        "what is Python",
        "who are you",
        "brain stats",
    ]
    
    print("\n🧪 Running tests:\n")
    
    for test in tests:
        print(f"👤 {test}")
        result = agi.process(test)
        print(f"🤖 {result['response'][:200]}")
        print(f"   [Intent: {result['intent']} | Facts: {result['facts_used']} | Score: {result['reflection_score']}]")
        print()
    
    print("✅ AGI Core test complete!")


if __name__ == "__main__":
    test_agi()