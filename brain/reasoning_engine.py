"""
EmptyNSpace AGI - Reasoning Engine (Level 2)
AI that actually THINKS, not just stores!

Level 1: Store facts ✅ (DONE - 13,093 facts!)
Level 2: REASON about facts ← THIS FILE!
Level 3: INFER new facts (next!)

Created by Nikhil Jatav
"""

import sqlite3
import os
import re
import json
import time
from datetime import datetime


class ReasoningEngine:
    """
    Makes AI actually THINK!
    
    Current AI: "Python is a language" (just stored text)
    
    With Reasoning:
      Fact 1: "Python is a programming language"
      Fact 2: "Programming languages are used to write software"
      REASON: "Python can be used to write software" ← NEW knowledge!
      
    This is what humans do - CONNECT dots!
    """
    
    def __init__(self, db_path='data/agi_brain.db'):
        os.makedirs('data', exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()
        self.reasoning_count = 0
    
    def _create_tables(self):
        c = self.conn.cursor()
        
        # Derived facts (reasoned, not just stored!)
        c.execute('''CREATE TABLE IF NOT EXISTS derived_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact1_key TEXT,
            fact2_key TEXT,
            derived_knowledge TEXT,
            reasoning_type TEXT,
            confidence REAL DEFAULT 0.3,
            verified INTEGER DEFAULT 0,
            created TEXT
        )''')
        
        # Reasoning chains
        c.execute('''CREATE TABLE IF NOT EXISTS reasoning_chains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            steps TEXT,
            conclusion TEXT,
            num_steps INTEGER,
            facts_used INTEGER,
            created TEXT
        )''')
        
        # Concepts (higher level understanding)
        c.execute('''CREATE TABLE IF NOT EXISTS concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept_name TEXT UNIQUE,
            related_facts TEXT,
            definition TEXT,
            examples TEXT,
            confidence REAL DEFAULT 0.3,
            created TEXT
        )''')
        
        self.conn.commit()
    
    def _get_facts(self, limit=500):
        """Get all stored facts"""
        c = self.conn.cursor()
        c.execute('SELECT key, value, category, confidence FROM facts ORDER BY confidence DESC LIMIT ?', (limit,))
        return [{'key': r[0], 'value': r[1], 'category': r[2], 'confidence': r[3]} for r in c.fetchall()]
    
    def _search_facts(self, query, limit=20):
        """Search facts by keyword"""
        c = self.conn.cursor()
        words = query.lower().split()
        results = []
        
        for word in words:
            if len(word) < 3:
                continue
            c.execute('''SELECT key, value, confidence FROM facts 
                        WHERE key LIKE ? OR value LIKE ? 
                        ORDER BY confidence DESC LIMIT ?''',
                     (f'%{word}%', f'%{word}%', limit))
            for r in c.fetchall():
                results.append({'key': r[0], 'value': r[1], 'confidence': r[2]})
        
        # Remove duplicates
        seen = set()
        unique = []
        for r in results:
            if r['key'] not in seen:
                seen.add(r['key'])
                unique.append(r)
        
        return unique[:limit]
    
    # ============================================
    # REASONING TYPE 1: Chain Reasoning
    # "A is B" + "B is C" = "A is C"
    # ============================================
    
    def chain_reason(self, topic=None):
        """
        Find chains: If A→B and B→C then A→C
        
        Example:
          "Python is a programming language"
          "Programming languages create software"
          DERIVE: "Python creates software"
        """
        if topic:
            facts = self._search_facts(topic, 50)
        else:
            facts = self._get_facts(200)
        
        derived = []
        
        for i, fact1 in enumerate(facts):
            # Get key concepts from fact1's value
            words1 = set(fact1['value'].lower().split())
            stop = {'the','is','a','an','and','or','in','on','to','for','of',
                    'it','that','this','with','are','was','were','be','been',
                    'has','have','had','do','does','did','will','would','can',
                    'could','should','may','might','not','no','but','if','so',
                    'at','by','from','up','about','into','through','during',
                    'its','also','such','these','those','which','their','them'}
            keywords1 = words1 - stop
            
            for fact2 in facts[i+1:]:
                # Check if fact2's key appears in fact1's value
                key2_words = set(fact2['key'].lower().split()) - stop
                
                overlap = keywords1 & key2_words
                
                if len(overlap) >= 1 and overlap:
                    # Found a chain!
                    derived_text = f"Since {fact1['key']} {fact1['value'][:100]}, " \
                                  f"and {fact2['key']} {fact2['value'][:100]}, " \
                                  f"therefore {fact1['key']} relates to {fact2['value'][:100]}"
                    
                    confidence = (fact1['confidence'] + fact2['confidence']) / 2 * 0.7
                    
                    derived.append({
                        'fact1': fact1['key'],
                        'fact2': fact2['key'],
                        'derived': derived_text,
                        'confidence': round(confidence, 2),
                        'connection': list(overlap)[:3]
                    })
                    
                    # Store in database
                    try:
                        self.conn.execute('''INSERT INTO derived_facts 
                            (fact1_key, fact2_key, derived_knowledge, reasoning_type, confidence, created)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                            (fact1['key'], fact2['key'], derived_text, 'chain',
                             confidence, datetime.now().isoformat()))
                    except:
                        pass
        
        self.conn.commit()
        self.reasoning_count += len(derived)
        
        return derived[:20]
    
    # ============================================
    # REASONING TYPE 2: Category Reasoning
    # Group similar facts into concepts
    # ============================================
    
    def categorize(self):
        """
        Group facts into categories/concepts
        
        Example:
          "Python is a language"
          "Java is a language"
          "C++ is a language"
          CONCEPT: "Programming Languages" includes Python, Java, C++
        """
        facts = self._get_facts(500)
        concepts = {}
        
        for fact in facts:
            value_lower = fact['value'].lower()
            
            # Find category patterns
            # "X is a TYPE of Y"
            match = re.search(r'is\s+(?:a|an)\s+(.{3,30})', value_lower)
            if match:
                category = match.group(1).strip()
                # Clean category
                category = re.sub(r'\s+(?:that|which|where|used|created).*', '', category)
                category = category.strip()[:30]
                
                if len(category) > 3:
                    if category not in concepts:
                        concepts[category] = []
                    concepts[category].append(fact['key'])
            
            # "X are Y"
            match = re.search(r'are\s+(.{3,30})', value_lower)
            if match:
                category = match.group(1).strip()[:30]
                if len(category) > 3:
                    if category not in concepts:
                        concepts[category] = []
                    concepts[category].append(fact['key'])
        
        # Filter: Only concepts with 2+ members
        real_concepts = {k: v for k, v in concepts.items() if len(v) >= 2}
        
        # Store concepts
        for concept_name, members in real_concepts.items():
            try:
                self.conn.execute('''INSERT OR REPLACE INTO concepts 
                    (concept_name, related_facts, definition, examples, confidence, created)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (concept_name, json.dumps(members[:20]),
                     f"Category containing: {', '.join(members[:5])}",
                     json.dumps(members[:10]),
                     min(len(members) * 0.1, 0.9),
                     datetime.now().isoformat()))
            except:
                pass
        
        self.conn.commit()
        
        return real_concepts
    
    # ============================================
    # REASONING TYPE 3: Analogy Reasoning
    # "A is to B as C is to D"
    # ============================================
    
    def find_analogies(self):
        """
        Find analogies between facts
        
        Example:
          "CPU is the brain of computer"
          "Nucleus is the brain of cell"
          ANALOGY: CPU is to Computer as Nucleus is to Cell
        """
        facts = self._get_facts(300)
        analogies = []
        
        for i, f1 in enumerate(facts):
            for f2 in facts[i+1:]:
                # Check if values have similar structure
                v1_words = set(f1['value'].lower().split())
                v2_words = set(f2['value'].lower().split())
                
                stop = {'the','is','a','an','and','or','in','on','to','for','of','it','that','this','with','are'}
                v1_clean = v1_words - stop
                v2_clean = v2_words - stop
                
                common = v1_clean & v2_clean
                
                if len(common) >= 3 and f1['key'] != f2['key']:
                    analogy = f"'{f1['key']}' is similar to '{f2['key']}' " \
                             f"(shared concepts: {', '.join(list(common)[:4])})"
                    analogies.append({
                        'item1': f1['key'],
                        'item2': f2['key'],
                        'shared': list(common)[:5],
                        'analogy': analogy
                    })
        
        return analogies[:15]
    
    # ============================================
    # REASONING TYPE 4: Question Answering
    # Use stored facts to answer questions
    # ============================================
    
    def answer_with_reasoning(self, question):
        """
        Answer question using REASONING over stored facts!
        Not just recall - actually THINK!
        
        Steps:
        1. Find relevant facts
        2. Chain them together
        3. Derive answer
        4. Explain reasoning
        """
        steps = []
        
        # Step 1: Find relevant facts
        relevant = self._search_facts(question, 15)
        steps.append(f"Step 1: Found {len(relevant)} relevant facts")
        
        if not relevant:
            return {
                'answer': f"I don't have enough knowledge to answer: '{question}'",
                'steps': steps,
                'confidence': 0,
                'facts_used': 0
            }
        
        # Step 2: Find connections
        connections = []
        for i, f1 in enumerate(relevant):
            for f2 in relevant[i+1:]:
                w1 = set(f1['value'].lower().split())
                w2 = set(f2['value'].lower().split())
                stop = {'the','is','a','an','and','or','in','on','to','for','of','it','are','was'}
                common = (w1 & w2) - stop
                if len(common) >= 2:
                    connections.append({
                        'fact1': f1['key'],
                        'fact2': f2['key'],
                        'link': list(common)[:3]
                    })
        
        steps.append(f"Step 2: Found {len(connections)} connections between facts")
        
        # Step 3: Build answer from facts
        answer = f"Based on my reasoning ({len(relevant)} facts, {len(connections)} connections):\n\n"
        
        # Primary facts
        answer += "What I know:\n"
        for f in relevant[:5]:
            answer += f"  • {f['key']}: {f['value'][:100]}\n"
        
        # Connections
        if connections:
            answer += "\nConnections I found:\n"
            for c in connections[:3]:
                answer += f"  🔗 '{c['fact1']}' and '{c['fact2']}' are connected via: {', '.join(c['link'])}\n"
        
        # Derived conclusion
        if len(relevant) >= 2:
            answer += f"\nMy reasoning:\n"
            answer += f"  Since {relevant[0]['key']} {relevant[0]['value'][:60]},\n"
            answer += f"  and {relevant[1]['key']} {relevant[1]['value'][:60]},\n"
            answer += f"  I conclude they are related topics.\n"
        
        steps.append(f"Step 3: Built answer from {len(relevant)} facts")
        
        # Confidence based on facts found
        confidence = min(len(relevant) * 0.1, 0.9)
        
        # Store reasoning chain
        try:
            self.conn.execute('''INSERT INTO reasoning_chains 
                (question, steps, conclusion, num_steps, facts_used, created)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (question, json.dumps(steps), answer[:500], 
                 len(steps), len(relevant), datetime.now().isoformat()))
            self.conn.commit()
        except:
            pass
        
        return {
            'answer': answer,
            'steps': steps,
            'confidence': round(confidence, 2),
            'facts_used': len(relevant),
            'connections': len(connections)
        }
    
    # ============================================
    # REASONING TYPE 5: Contradiction Detection
    # Find conflicting facts
    # ============================================
    
    def find_contradictions(self):
        """
        Find facts that might contradict each other
        
        Example:
          Fact 1: "Python is slow"
          Fact 2: "Python is fast for development"
          CONTRADICTION: Different claims about Python's speed!
        """
        facts = self._get_facts(300)
        contradictions = []
        
        positive = ['good', 'fast', 'best', 'great', 'better', 'advantage', 'easy', 'simple', 'efficient']
        negative = ['bad', 'slow', 'worst', 'poor', 'worse', 'disadvantage', 'hard', 'complex', 'inefficient']
        
        for i, f1 in enumerate(facts):
            for f2 in facts[i+1:]:
                # Same topic?
                if f1['key'] == f2['key'] or f1['key'] in f2['key'] or f2['key'] in f1['key']:
                    v1 = f1['value'].lower()
                    v2 = f2['value'].lower()
                    
                    # Check sentiment mismatch
                    f1_pos = any(w in v1 for w in positive)
                    f1_neg = any(w in v1 for w in negative)
                    f2_pos = any(w in v2 for w in positive)
                    f2_neg = any(w in v2 for w in negative)
                    
                    if (f1_pos and f2_neg) or (f1_neg and f2_pos):
                        contradictions.append({
                            'topic': f1['key'],
                            'fact1': f1['value'][:100],
                            'fact2': f2['value'][:100],
                            'type': 'sentiment_conflict'
                        })
        
        return contradictions[:10]
    
    # ============================================
    # FULL REASONING SESSION
    # ============================================
    
    def full_reasoning_session(self):
        """Run all reasoning types!"""
        results = {}
        
        print("🧠 Running reasoning session...\n")
        
        # Chain reasoning
        print("  1. Chain reasoning...")
        chains = self.chain_reason()
        results['chains'] = len(chains)
        print(f"     Found {len(chains)} chains!")
        
        # Categorization
        print("  2. Categorizing knowledge...")
        concepts = self.categorize()
        results['concepts'] = len(concepts)
        print(f"     Found {len(concepts)} concepts!")
        
        # Analogies
        print("  3. Finding analogies...")
        analogies = self.find_analogies()
        results['analogies'] = len(analogies)
        print(f"     Found {len(analogies)} analogies!")
        
        # Contradictions
        print("  4. Checking contradictions...")
        contradictions = self.find_contradictions()
        results['contradictions'] = len(contradictions)
        print(f"     Found {len(contradictions)} contradictions!")
        
        # Stats
        c = self.conn.cursor()
        c.execute('SELECT COUNT(*) FROM derived_facts')
        results['total_derived'] = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM concepts')
        results['total_concepts'] = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM reasoning_chains')
        results['total_chains'] = c.fetchone()[0]
        
        return results
    
    def get_stats(self):
        """Reasoning statistics"""
        c = self.conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM derived_facts')
        derived = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM concepts')
        concepts = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM reasoning_chains')
        chains = c.fetchone()[0]
        
        return {
            'derived_facts': derived,
            'concepts': concepts,
            'reasoning_chains': chains,
            'session_reasonings': self.reasoning_count
        }


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print(f"\n{'🧠' * 20}")
    print(f"  Reasoning Engine Test")
    print(f"{'🧠' * 20}\n")
    
    engine = ReasoningEngine()
    
    # Check facts available
    facts = engine._get_facts(10)
    print(f"📊 Facts in brain: {len(engine._get_facts(10000))}\n")
    
    if len(engine._get_facts(10000)) < 10:
        print("⚠️ Not enough facts! Run auto_learner.py first!")
        print("   Need 100+ facts for good reasoning.\n")
    
    # Run full reasoning
    print("🧠 Running full reasoning session...\n")
    results = engine.full_reasoning_session()
    
    print(f"\n📊 Reasoning Results:")
    for key, val in results.items():
        print(f"   {key}: {val}")
    
    # Test question answering
    print(f"\n🤔 Testing question answering:\n")
    
    questions = [
        "What is artificial intelligence?",
        "How do neural networks work?",
        "What is Python used for?",
        "What is machine learning?"
    ]
    
    for q in questions:
        result = engine.answer_with_reasoning(q)
        print(f"Q: {q}")
        print(f"A: {result['answer'][:200]}...")
        print(f"   [Facts: {result['facts_used']} | Connections: {result['connections']} | Confidence: {result['confidence']}]")
        print()
    
    print(f"\n📊 Final Stats:")
    stats = engine.get_stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")
    
    print(f"\n✅ Reasoning Engine Test Complete!")