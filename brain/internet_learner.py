
"""
EmptyNSpace AGI - Internet Learning Engine
Learns from: Search, Wikipedia, Websites, News

Safety: User controls what AI learns!
Created by Nikhil Jatav
"""

import re
import time
import json
import hashlib
import os
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except:
    HAS_BS4 = False

try:
    from ddgs import DDGS
except:
    from duckduckgo_search import DDGS


class InternetLearner:
    """
    Internet Learning Engine for AGI
    
    Capabilities:
    1. Search any topic (DuckDuckGo)
    2. Read any webpage
    3. Learn from Wikipedia
    4. Extract facts automatically
    5. Store everything permanently
    6. Build knowledge over time
    
    All under USER control!
    """
    
    def __init__(self, memory):
        self.memory = memory
        self.session_learned = 0
        self.crawl_history = []
        self.rate_limit = 2  # seconds between requests
        self.last_request = 0
        
        # Learning log file
        os.makedirs('data', exist_ok=True)
        self.log_file = 'data/learning_log.json'
    
    def _wait_rate_limit(self):
        """Prevent too fast requests"""
        elapsed = time.time() - self.last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request = time.time()
    
    def _log_learning(self, source, topic, facts_count):
        """Log what was learned"""
        entry = {
            'time': datetime.now().isoformat(),
            'source': source,
            'topic': topic,
            'facts': facts_count
        }
        
        self.crawl_history.append(entry)
        
        # Save to file
        try:
            history = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    history = json.load(f)
            
            history.append(entry)
            
            # Keep last 500 entries
            if len(history) > 500:
                history = history[-500:]
            
            with open(self.log_file, 'w') as f:
                json.dump(history, f, indent=2)
        except:
            pass
    
    # ============================================
    # SEARCH & LEARN
    # ============================================
    
    def search_and_learn(self, topic, max_results=5):
        """
        Search internet → Extract facts → Store in memory
        
        User says: "search and learn about quantum computing"
        AI: Searches → Reads → Extracts facts → Stores!
        """
        if not HAS_SEARCH:
            return {
                'status': 'error',
                'message': 'Search not available. Run: pip install duckduckgo-search'
            }
        
        self._wait_rate_limit()
        
        try:
            results = []
            total_facts = 0
            
            with DDGS() as ddgs:
                search_results = list(ddgs.text(topic, max_results=max_results))
            
            for r in search_results:
                title = r.get('title', '')
                snippet = r.get('body', '')
                url = r.get('href', '')
                
                # Extract facts from snippet
                facts = self._extract_facts(snippet, topic)
                
                # Store each fact
                for fact_key, fact_value in facts:
                    self.memory.learn_fact(
                        category='internet_search',
                        key=fact_key,
                        value=fact_value,
                        source=f'search:{url}'
                    )
                    total_facts += 1
                
                # Store search result itself
                self.memory.learn_fact(
                    category='search_result',
                    key=title[:100],
                    value=snippet[:500],
                    source=url
                )
                total_facts += 1
                
                results.append({
                    'title': title,
                    'snippet': snippet[:200],
                    'url': url,
                    'facts_extracted': len(facts)
                })
            
            self.session_learned += total_facts
            self._log_learning('search', topic, total_facts)
            
            return {
                'status': 'success',
                'topic': topic,
                'results_found': len(results),
                'facts_learned': total_facts,
                'results': results
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    # ============================================
    # WIKIPEDIA LEARNING
    # ============================================
    
    def learn_from_wikipedia(self, topic):
        """
        Learn from Wikipedia article
        
        Best source for structured knowledge!
        """
        if not HAS_REQUESTS or not HAS_BS4:
            return {'status': 'error', 'message': 'Install: requests beautifulsoup4'}
        
        self._wait_rate_limit()
        
        try:
            # Wikipedia API
            url = 'https://en.wikipedia.org/api/rest_v1/page/summary/' + topic.replace(' ', '_')
            
            r = requests.get(url, timeout=10, headers={
                'User-Agent': 'EmptyNSpace-AGI/1.0'
            })
            
            if r.status_code != 200:
                # Try search
                return self._wiki_search(topic)
            
            data = r.json()
            
            title = data.get('title', topic)
            extract = data.get('extract', '')
            description = data.get('description', '')
            
            if not extract:
                return {'status': 'error', 'message': f'No Wikipedia article for "{topic}"'}
            
            # Store main article
            self.memory.learn_fact('wikipedia', title, extract[:1000], f'wikipedia:{title}')
            
            if description:
                self.memory.learn_fact('wikipedia', f'{title} (description)', description, f'wikipedia:{title}')
            
            # Extract facts from text
            facts = self._extract_facts(extract, topic)
            
            for fact_key, fact_value in facts:
                self.memory.learn_fact('wikipedia_fact', fact_key, fact_value, f'wikipedia:{title}')
            
            total = len(facts) + 2
            self.session_learned += total
            self._log_learning('wikipedia', topic, total)
            
            return {
                'status': 'success',
                'title': title,
                'description': description,
                'summary': extract[:500],
                'facts_learned': total,
                'source': f'wikipedia:{title}'
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _wiki_search(self, topic):
        """Search Wikipedia if direct article not found"""
        try:
            url = f'https://en.wikipedia.org/w/api.php?action=opensearch&search={topic}&limit=3&format=json'
            r = requests.get(url, timeout=10)
            data = r.json()
            
            if len(data) > 1 and data[1]:
                # Try first result
                return self.learn_from_wikipedia(data[1][0])
            
            return {'status': 'error', 'message': f'No Wikipedia results for "{topic}"'}
        except:
            return {'status': 'error', 'message': 'Wikipedia search failed'}
    
    # ============================================
    # WEBPAGE LEARNING
    # ============================================
    
    def learn_from_url(self, url):
        """
        Read any webpage → Extract knowledge → Store
        """
        if not HAS_REQUESTS or not HAS_BS4:
            return {'status': 'error', 'message': 'Install: requests beautifulsoup4'}
        
        self._wait_rate_limit()
        
        try:
            r = requests.get(url, timeout=15, headers={
                'User-Agent': 'EmptyNSpace-AGI/1.0'
            })
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Remove non-content
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            
            # Get title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else url
            
            # Get main content
            text = soup.get_text('\n', strip=True)[:5000]
            
            # Get headings for structure
            headings = []
            for h in soup.find_all(['h1', 'h2', 'h3']):
                headings.append(h.get_text().strip())
            
            # Store page summary
            self.memory.learn_fact('webpage', title_text, text[:1000], url)
            
            # Extract and store facts
            facts = self._extract_facts(text, title_text)
            
            for fact_key, fact_value in facts:
                self.memory.learn_fact('web_fact', fact_key, fact_value, url)
            
            # Store headings as topics
            for heading in headings[:10]:
                if len(heading) > 5:
                    self.memory.learn_fact('web_topic', heading, f'Topic from {title_text}', url)
            
            total = len(facts) + len(headings[:10]) + 1
            self.session_learned += total
            self._log_learning('webpage', url, total)
            
            return {
                'status': 'success',
                'title': title_text,
                'text_length': len(text),
                'headings': headings[:10],
                'facts_learned': total,
                'source': url
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    # ============================================
    # DEEP LEARNING (Multiple Sources)
    # ============================================
    
    def deep_learn(self, topic):
        """
        Learn EVERYTHING about a topic!
        
        1. Wikipedia article
        2. Web search (5 results)
        3. Extract all facts
        4. Find connections
        
        This is the MOST POWERFUL learning function!
        """
        results = {
            'topic': topic,
            'sources': [],
            'total_facts': 0,
            'status': 'success'
        }
        
        # Step 1: Wikipedia
        wiki = self.learn_from_wikipedia(topic)
        if wiki.get('status') == 'success':
            results['sources'].append({
                'type': 'wikipedia',
                'title': wiki.get('title', ''),
                'facts': wiki.get('facts_learned', 0)
            })
            results['total_facts'] += wiki.get('facts_learned', 0)
        
        # Step 2: Web Search
        search = self.search_and_learn(topic, max_results=3)
        if search.get('status') == 'success':
            results['sources'].append({
                'type': 'search',
                'results': search.get('results_found', 0),
                'facts': search.get('facts_learned', 0)
            })
            results['total_facts'] += search.get('facts_learned', 0)
        
        # Step 3: Find connections
        all_facts = self.memory.recall(topic, top_k=20)
        connections = []
        
        for i, f1 in enumerate(all_facts):
            for f2 in all_facts[i+1:]:
                words1 = set(f1['value'].lower().split())
                words2 = set(f2['value'].lower().split())
                stop = {'the','is','a','an','and','or','in','on','to','for','of','it','that','this','with'}
                common = (words1 & words2) - stop
                
                if len(common) >= 3:
                    conn = f"'{f1['key']}' relates to '{f2['key']}'"
                    connections.append(conn)
                    
                    self.memory.discover_pattern(
                        'topic_connection',
                        conn,
                        f"Common words: {', '.join(list(common)[:5])}"
                    )
        
        results['connections'] = connections[:10]
        results['knowledge_after'] = self.memory.get_brain_stats()['facts_known']
        
        self._log_learning('deep_learn', topic, results['total_facts'])
        
        return results
    
    # ============================================
    # FACT EXTRACTION
    # ============================================
    
    def _extract_facts(self, text, topic):
        """Extract facts from any text"""
        facts = []
        
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            
            if len(sentence) < 15 or len(sentence) > 300:
                continue
            
            # Skip non-informative sentences
            skip_words = ['click', 'subscribe', 'cookie', 'privacy', 'login', 'sign up', 'advertisement']
            if any(w in sentence.lower() for w in skip_words):
                continue
            
            # Pattern: "X is Y"
            match = re.search(r'^(.{3,50}?)\s+is\s+(.{10,200})', sentence, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                
                # Clean key
                key = re.sub(r'^(the|a|an)\s+', '', key, flags=re.IGNORECASE)
                
                if len(key) > 3 and len(value) > 10:
                    facts.append((key[:100], value[:500]))
                    continue
            
            # Pattern: "X are Y"
            match = re.search(r'^(.{3,50}?)\s+are\s+(.{10,200})', sentence, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                value = 'are ' + match.group(2).strip()
                if len(key) > 3:
                    facts.append((key[:100], value[:500]))
                    continue
            
            # Pattern: "X was Y"
            match = re.search(r'^(.{3,50}?)\s+was\s+(.{10,200})', sentence, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                value = 'was ' + match.group(2).strip()
                if len(key) > 3:
                    facts.append((key[:100], value[:500]))
                    continue
            
            # Pattern: "X means Y" or "X refers to Y"
            match = re.search(r'^(.{3,50}?)\s+(?:means?|refers?\s+to)\s+(.{10,200})', sentence, re.IGNORECASE)
            if match:
                facts.append((match.group(1).strip()[:100], match.group(2).strip()[:500]))
                continue
            
            # If sentence contains topic keyword, store as related fact
            if topic.lower().split()[0] in sentence.lower() and len(sentence) > 20:
                key = f"{topic}_fact_{len(facts)}"
                facts.append((key[:100], sentence[:500]))
        
        # Remove duplicates
        seen = set()
        unique = []
        for key, value in facts:
            if key.lower() not in seen:
                seen.add(key.lower())
                unique.append((key, value))
        
        return unique[:20]  # Max 20 facts per text
    
    # ============================================
    # CONTINUOUS LEARNING
    # ============================================
    
    def auto_explore(self, seed_topics=None):
        """
        Autonomous exploration!
        
        Start with seed topics → Learn → Find new topics → Learn more
        
        USER MUST APPROVE before running!
        """
        if seed_topics is None:
            seed_topics = ['artificial intelligence', 'machine learning', 'python programming']
        
        explored = []
        new_topics = []
        
        for topic in seed_topics[:3]:  # Limit to 3
            result = self.deep_learn(topic)
            explored.append({
                'topic': topic,
                'facts': result.get('total_facts', 0),
                'connections': len(result.get('connections', []))
            })
            
            # Find new topics from connections
            for conn in result.get('connections', []):
                words = conn.split("'")
                for w in words:
                    if len(w) > 5 and w not in seed_topics:
                        new_topics.append(w)
        
        return {
            'explored': explored,
            'new_topics_found': new_topics[:5],
            'total_facts': sum(e['facts'] for e in explored),
            'suggestion': f"Next, I could learn about: {', '.join(new_topics[:3])}"
        }
    
    # ============================================
    # STATS
    # ============================================
    
    def get_learning_stats(self):
        """Learning statistics"""
        history = []
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    history = json.load(f)
        except:
            pass
        
        return {
            'session_facts': self.session_learned,
            'total_sessions': len(history),
            'total_crawls': len(self.crawl_history),
            'sources_used': len(set(h.get('source', '') for h in history)),
            'capabilities': {
                'search': HAS_SEARCH,
                'web_crawl': HAS_REQUESTS and HAS_BS4,
                'wikipedia': HAS_REQUESTS
            }
        }


# ============================================
# TEST
# ============================================

def test_internet_learner():
    """Test Internet Learning"""
    
    # Need AGI Memory
def test_internet_learner():
    from agi_core import AGI_Memory
    
    print("\n" + "🌐" * 25)
    print("  Internet Learning Engine Test")
    print("🌐" * 25)
    
    memory = AGI_Memory()
    learner = InternetLearner(memory)
    
    stats_before = memory.get_brain_stats()
    print(f"\n📊 Before: {stats_before['facts_known']} facts\n")
    
    # Test 1: Wikipedia
    print("📚 Test 1: Wikipedia...")
    result = learner.learn_from_wikipedia("Artificial intelligence")
    if result['status'] == 'success':
        print(f"   ✅ Facts learned: {result['facts_learned']}")
    else:
        print(f"   ❌ {result['message']}")
    
    # Test 2: Search
    print("\n🔍 Test 2: Search...")
    result = learner.search_and_learn("machine learning", max_results=3)
    if result['status'] == 'success':
        print(f"   ✅ Facts learned: {result['facts_learned']}")
    else:
        print(f"   ❌ {result['message']}")
    
    # Final stats
    stats_after = memory.get_brain_stats()
    print(f"\n📊 Before: {stats_before['facts_known']} facts")
    print(f"📊 After: {stats_after['facts_known']} facts")
    print(f"📊 Learned: {stats_after['facts_known'] - stats_before['facts_known']} new facts!")
    print("\n✅ Test Complete!")
    
    # Test 2: Search
    print("\n🔍 Test 2: Search and Learn...")
    result = learner.search_and_learn("machine learning basics", max_results=3)
    if result['status'] == 'success':
        print(f"   ✅ Results: {result['results_found']}")
        print(f"   Facts learned: {result['facts_learned']}")
        for r in result['results'][:2]:
            print(f"   • {r['title'][:50]}")
    else:
        print(f"   ❌ {result['message']}")
    
    # Test 3: Deep Learn
    print("\n🧠 Test 3: Deep Learning about 'Neural Networks'...")
    result = learner.deep_learn("neural networks")
    print(f"   ✅ Sources: {len(result['sources'])}")
    print(f"   Total facts: {result['total_facts']}")
    print(f"   Connections: {len(result.get('connections', []))}")
    
    for conn in result.get('connections', [])[:3]:
        print(f"   🔗 {conn}")
    
    # Final stats
    stats_after = memory.get_brain_stats()
    print(f"\n📊 After: {stats_after['facts_known']} facts")
    print(f"   Learned: {stats_after['facts_known'] - stats_before['facts_known']} new facts!")
    
    # Learning stats
    lstats = learner.get_learning_stats()
    print(f"\n📊 Learning Stats:")
    for k, v in lstats.items():
        print(f"   {k}: {v}")
    
    print("\n✅ Internet Learning Test Complete!")


if __name__ == "__main__":
    test_internet_learner()