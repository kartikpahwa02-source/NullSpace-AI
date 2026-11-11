"""
NKJ EmptyNSpace v7.0 - SMART BRAIN
Small model + Smart strategy = Big output!

Secret: It's not about MODEL SIZE
        It's about HOW you use it!

Created by Nikhil Jatav
"""

import requests
import json
import os
import time
import hashlib

OLLAMA_URL = 'http://localhost:11434/api/chat'


class SmartRouter:
    """
    Decide: Is this query EASY, MEDIUM, or HARD?
    
    Easy (80% queries): Use 1B model (instant!)
    Medium (15%): Use 4B model (fast!)
    Hard (5%): Use Chain of Thought (smart!)
    
    Result: 80% of time = FAST response!
    """
    
    def classify(self, query):
        q = query.lower()
        
        # EASY: Greetings, simple facts
        easy_keywords = [
            'hello', 'hi', 'hey', 'bye', 'thanks', 'name',
            'time', 'date', 'weather', 'who are you',
            'what is your', 'how are you'
        ]
        
        # HARD: Complex reasoning, coding, research
        hard_keywords = [
            'explain why', 'compare', 'analyze', 'write code',
            'debug', 'research', 'step by step', 'create',
            'build', 'design', 'plan', 'strategy',
            'difference between', 'pros and cons',
            'write a program', 'solve this'
        ]
        
        # Check easy
        if any(kw in q for kw in easy_keywords):
            return 'easy', 'llama3.2:1b'
        
        # Check hard
        if any(kw in q for kw in hard_keywords):
            return 'hard', 'gemma3:4b'
        
        # Check length
        if len(q.split()) <= 5:
            return 'easy', 'llama3.2:1b'
        elif len(q.split()) > 20:
            return 'hard', 'gemma3:4b'
        
        return 'medium', 'llama3.2:1b'


class KnowledgeRAG:
    """
    RAG: Retrieval Augmented Generation
    
    Instead of model KNOWING everything:
    Store knowledge in file → Retrieve when needed!
    
    Small model + Big knowledge = Smart AI!
    
    Like: Student with textbook > Student without!
    """
    
    def __init__(self):
        self.knowledge_file = 'data/knowledge_base.json'
        self.knowledge = {}
        self._load()
        self._add_default_knowledge()
    
    def _load(self):
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge = json.load(f)
        except:
            pass
    
    def _save(self):
        try:
            os.makedirs('data', exist_ok=True)
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def _add_default_knowledge(self):
        """Pre-load important knowledge"""
        defaults = {
            'nkj law': 'NKJ Law of Contextual Generation is a neural network compression technique created by Nikhil Jatav. It achieves 86.1x compression by using positional information as free data through Fourier wave decomposition. 2,730 parameters can generate 235,146 weights. Proven on MNIST (80.55% accuracy) and CIFAR-10 (86.70% accuracy).',
            
            'nikhil jatav': 'Nikhil Jatav is an AI researcher who created the NKJ Law and EmptyNSpace AI. He built an autonomous multi-agent AI system with 10+ specialized agents, self-learning capability, and hardware control. All built independently on a laptop with RTX 3050.',
            
            'emptynspace': 'EmptyNSpace AI (also called NKJ EmptyNSpace) is an autonomous multi-agent AI operating system created by Nikhil Jatav. It features 10+ specialized agents (Game, Phone, Research, Code, SmartHome, etc.), self-learning with SQLite knowledge base, 8+ Indian language voice support, and a cyberpunk sci-fi interface.',
            
            'nkj cloud': 'NKJ Cloud is an AI deployment platform that makes deploying AI models 86x cheaper than AWS. It uses NKJ Law compression to automatically compress models. Pricing: Free (₹0), Pro (₹999/month), Enterprise (₹4,999/month).',
            
            'power encoding': 'Power Encoding is a neural network compression technique that uses seed matrices and power transformations with Kronecker products to generate full weight matrices. Achieves 19.6x compression with 78.88% accuracy on MNIST.',
            
            'agentic ai': 'Agentic AI refers to AI systems that can think, plan, act, and learn autonomously. Key components: Brain (LLM), Tools (actions), Memory (persistence), Planning (step decomposition), Loop (iterative execution). EmptyNSpace is an agentic AI system.',
            
            'machine learning': 'Machine Learning is a subset of AI where computers learn from data without being explicitly programmed. Types: Supervised (labeled data), Unsupervised (unlabeled), Reinforcement (reward-based). Common algorithms: Neural Networks, Decision Trees, SVM.',
            
            'neural network': 'A neural network is a computing system inspired by biological neural networks. It consists of layers of interconnected nodes (neurons) that process information. Key types: CNN (images), RNN (sequences), Transformer (attention-based).',
            
            'transformer': 'Transformer is a neural network architecture introduced in "Attention is All You Need" (2017). Uses self-attention mechanism. Powers GPT, BERT, and modern LLMs. Key components: Multi-head attention, Feed-forward layers, Positional encoding.',
            
            'python': 'Python is a high-level programming language widely used in AI/ML. Key libraries: PyTorch (deep learning), NumPy (math), Pandas (data), Flask/FastAPI (web). Created by Guido van Rossum in 1991.',
        }
        
        for key, value in defaults.items():
            if key not in self.knowledge:
                self.knowledge[key] = value
        
        self._save()
    
    def search(self, query):
        """Find relevant knowledge for query"""
        q_lower = query.lower()
        q_words = set(q_lower.split())
        
        results = []
        
        for key, value in self.knowledge.items():
            key_words = set(key.lower().split())
            
            # Exact match
            if key.lower() in q_lower:
                results.append({'key': key, 'value': value, 'score': 1.0})
                continue
            
            # Word overlap
            common = q_words & key_words
            if common:
                score = len(common) / len(key_words)
                if score >= 0.5:
                    results.append({'key': key, 'value': value, 'score': score})
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:3]
    
    def add_knowledge(self, key, value):
        """Learn new knowledge"""
        self.knowledge[key.lower()] = value
        self._save()
    
    def get_context(self, query):
        """Get relevant context for LLM prompt"""
        results = self.search(query)
        
        if not results:
            return ""
        
        context = "Relevant knowledge:\n"
        for r in results:
            context += f"- {r['key']}: {r['value']}\n"
        
        return context


class ChainOfThought:
    """
    Chain of Thought: Think step by step!
    
    Small model thinking 5 steps 
    > Big model thinking 1 step!
    
    "Let me think about this step by step..."
    """
    
    def create_cot_prompt(self, query, context=""):
        """Create Chain of Thought prompt"""
        return f"""You are NKJ EmptyNSpace AI, a highly capable assistant created by Nikhil Jatav.

{context}

User's question: {query}

Think step by step:
1. First, understand what the user is asking
2. Break down the problem into parts
3. Consider relevant knowledge
4. Formulate a clear, helpful response

Give a detailed, accurate answer:"""
    
    def create_simple_prompt(self, query, context=""):
        """Simple prompt for easy queries"""
        return f"""You are NKJ EmptyNSpace AI, created by Nikhil Jatav. You are powered by NKJ Law (86x compression technology).

{context}

User: {query}

Give a brief, helpful response:"""


class NKJ_SmartBrain:
    """
    THE ULTIMATE BRAIN!
    
    Combines:
    1. Smart Routing (right model for right task)
    2. RAG (knowledge retrieval)
    3. Chain of Thought (step by step thinking)
    4. NKJ Caching (instant repeated answers)
    5. Learning (gets smarter over time!)
    
    Result: LAPTOP pe GPT-4 level output! 🤯
    """
    
    def __init__(self):
        print("🧠 Loading Smart Brain...")
        
        self.router = SmartRouter()
        self.rag = KnowledgeRAG()
        self.cot = ChainOfThought()
        
        # NKJ Cache
        self.cache = {}
        self.cache_file = 'data/smart_cache.json'
        self._load_cache()
        
        # Stats
        self.stats = {
            'easy': 0, 'medium': 0, 'hard': 0,
            'cache_hits': 0, 'rag_hits': 0,
            'total_queries': 0, 'time_saved': 0
        }
        
        print("🧠 Smart Brain Ready!")
        print(f"   Knowledge: {len(self.rag.knowledge)} facts")
        print(f"   Cache: {len(self.cache)} entries")
    
    def _load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
        except:
            pass
    
    def _save_cache(self):
        try:
            os.makedirs('data', exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False)
        except:
            pass
    
    def _cache_key(self, msg):
        return hashlib.md5(msg.lower().strip().encode()).hexdigest()
    
    def think(self, query):
        """
        Main thinking function!
        
        Flow:
        1. Check cache (instant!)
        2. Route query (easy/medium/hard)
        3. Get relevant knowledge (RAG)
        4. Build smart prompt (CoT if hard)
        5. Call model
        6. Cache response
        7. Learn from interaction
        """
        
        start_time = time.time()
        self.stats['total_queries'] += 1
        
        # STEP 1: Check cache
        cache_key = self._cache_key(query)
        if cache_key in self.cache:
            self.stats['cache_hits'] += 1
            self.stats['time_saved'] += 3
            elapsed = time.time() - start_time
            return {
                'response': self.cache[cache_key],
                'source': 'cache',
                'model': 'cached',
                'time': round(elapsed, 3),
                'difficulty': 'cached'
            }
        
        # STEP 2: Route query
        difficulty, model = self.router.classify(query)
        self.stats[difficulty] += 1
        
        # STEP 3: Get knowledge (RAG)
        context = self.rag.get_context(query)
        if context:
            self.stats['rag_hits'] += 1
        
        # STEP 4: Build prompt
        if difficulty == 'hard':
            prompt = self.cot.create_cot_prompt(query, context)
        else:
            prompt = self.cot.create_simple_prompt(query, context)
        
        # STEP 5: Call model
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}
        ]
        
        try:
            r = requests.post(OLLAMA_URL, json={
                'model': model,
                'messages': messages,
                'stream': False
            }, timeout=60)
            
            if r.status_code == 200:
                response = r.json().get('message', {}).get('content', 'No response')
            else:
                response = f"Error: Status {r.status_code}"
        except Exception as e:
            response = f"Error: {str(e)}"
        
        # STEP 6: Cache
        self.cache[cache_key] = response
        self._save_cache()
        
        # STEP 7: Learn (extract facts from conversation)
        self._learn_from_query(query, response)
        
        elapsed = time.time() - start_time
        
        return {
            'response': response,
            'source': 'generated',
            'model': model,
            'time': round(elapsed, 3),
            'difficulty': difficulty,
            'rag_used': bool(context)
        }
    
    def _learn_from_query(self, query, response):
        """Learn from interactions - get smarter!"""
        q_lower = query.lower()
        
        # If user teaches something
        if 'remember' in q_lower or 'learn' in q_lower:
            if '=' in query or 'is' in q_lower or ':' in query:
                parts = query.replace('remember', '').replace('learn', '')
                for sep in ['=', ' is ', ':']:
                    if sep in parts:
                        key, value = parts.split(sep, 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if key and value:
                            self.rag.add_knowledge(key, value)
    
    def get_stats(self):
        """Performance statistics"""
        total = self.stats['total_queries']
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            'cache_rate': f"{self.stats['cache_hits']/total*100:.1f}%",
            'rag_rate': f"{self.stats['rag_hits']/total*100:.1f}%",
            'easy_rate': f"{self.stats['easy']/total*100:.1f}%",
            'knowledge_count': len(self.rag.knowledge),
            'cache_count': len(self.cache)
        }


# Test
if __name__ == "__main__":
    brain = NKJ_SmartBrain()
    
    print("\n🧪 Testing Smart Brain:\n")
    
    tests = [
        "hello",
        "what is NKJ Law",
        "who created you",
        "explain how neural networks work step by step",
        "hello",
        "what is NKJ Law",
    ]
    
    for query in tests:
        result = brain.think(query)
        print(f"Q: {query}")
        print(f"A: {result['response'][:100]}...")
        print(f"   Model: {result['model']} | Difficulty: {result['difficulty']} | Time: {result['time']}s")
        print(f"   Source: {result['source']}")
        print()
    
    print("📊 Stats:")
    stats = brain.get_stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")