"""
Self-Learning Engine — AI khud seekhta hai aur improve hota hai
"""

from brain.llm import ask_llm_direct
from brain.knowledge_base import (
    save_pattern, find_pattern, learn_skill, use_skill,
    save_mistake, get_mistakes, save_code, add_knowledge,
    get_knowledge_count, get_stats
)
from memory.memory import learn as mem_learn


def learn_from_interaction(user_input, ai_response, result, success):
    """Har interaction se seekho"""

    # Skill extract karo
    skill_prompt = f"""What skill was used in this interaction?

User: {user_input}
AI: {ai_response}
Result: {result}
Success: {success}

Reply with ONLY:
SKILL: (skill name)
DESC: (what was done)
"""

    skill_text = ask_llm_direct(skill_prompt)

    try:
        lines = skill_text.strip().split("\n")
        skill_name = "general"
        skill_desc = user_input

        for line in lines:
            if line.startswith("SKILL:"):
                skill_name = line.replace("SKILL:", "").strip()
            elif line.startswith("DESC:"):
                skill_desc = line.replace("DESC:", "").strip()

        learn_skill(skill_name, skill_desc)
        use_skill(skill_name)
    except Exception:
        pass

    # Pattern store karo
    if success:
        save_pattern("command", user_input, ai_response)

    # Knowledge store karo
    if success and len(result) > 50:
        add_knowledge(user_input[:100], result[:500], source="interaction", category="learned", confidence=0.6)

    # Mistake yaad karo
    if not success:
        mistake_prompt = f"What went wrong and how to fix?\nTask: {user_input}\nError: {result}\nGive brief fix."
        fix = ask_llm_direct(mistake_prompt)
        save_mistake(user_input, result, fix)


def learn_from_mistake(task, error):
    """Galti se seekho"""
    fix_prompt = f"Fix this error:\nTask: {task}\nError: {error}\nGive ONLY the fix/solution."
    fix = ask_llm_direct(fix_prompt)
    save_mistake(task, error, fix)
    learn_skill("error_fixing", f"Fixed: {error[:100]}")
    return fix


def self_improve():
    """AI apne aap improve hota hai"""

    # Past mistakes analyze karo
    mistakes = get_mistakes(limit=10)

    if not mistakes:
        return "No mistakes to learn from. I'm already great! 🧠"

    mistakes_text = "\n".join([f"- Task: {m['task']}\n  Error: {m['error']}\n  Fix: {m['fix']}" for m in mistakes])

    prompt = f"""Analyze these past mistakes and find patterns:

{mistakes_text}

Answer:
1) What are the common mistakes?
2) How to avoid them in future?
3) What improvements should be made?
4) Any new skills to learn?

Reply in Hindi/Hinglish."""

    analysis = ask_llm_direct(prompt)

    add_knowledge("self_improvement", analysis, source="self_analysis", category="meta", confidence=0.9)

    return f"🧠 Self-Improvement Analysis:\n\n{analysis}"


def predict_task(user_input):
    """User kya karna chahta hai predict karo"""

    # Check patterns
    patterns = find_pattern(user_input)

    if patterns:
        best = patterns[0]
        use_skill(best.get("pattern_type", "general"))
        return {
            "predicted": True,
            "pattern": best["output_pattern"],
            "confidence": best["success_rate"]
        }

    return {"predicted": False}


def get_learning_report():
    """Learning ka report do"""
    stats = get_stats()

    report = f"""🧠 Self-Learning Report:

📊 Database Stats:
  - Knowledge: {stats.get('knowledge', 0)} entries
  - Skills: {stats.get('skills', 0)} skills
  - Patterns: {stats.get('patterns', 0)} patterns
  - Code Written: {stats.get('code_history', 0)} programs
  - Mistakes Learned: {stats.get('mistakes', 0)} lessons
  - World Facts: {stats.get('world_facts', 0)} facts
  - Conversations: {stats.get('conversations', 0)} chats

Total Knowledge: {stats.get('knowledge', 0) + stats.get('world_facts', 0)} items"""

    return report
    def infinite_learn(self, questions_per_batch=10, delay=1, max_total=10000):
        """
        CONTINUOUS LEARNING MODE!
        
        AI learns non-stop until stopped!
        Smart topic selection - no repeats!
        Gets smarter with every question!
        
        Run in background - learns while you sleep! 🌙
        
        Args:
            questions_per_batch: Questions before showing progress
            delay: Seconds between questions
            max_total: Safety limit (default 10,000)
        """
        self.is_running = True
        self.questions_asked = 0
        self.facts_learned = 0
        self.session_log = []
        
        asked_questions = set()  # Never repeat!
        explored_topics = set()
        
        stats_before = self.memory.get_brain_stats()
        start_time = time.time()
        
        print(f"\n🧠 INFINITE LEARNING MODE ACTIVATED!")
        print(f"   Safety limit: {max_total} questions")
        print(f"   Brain before: {stats_before['facts_known']} facts")
        print(f"   Press Ctrl+C to stop anytime!\n")
        print(f"{'='*60}")
        
        batch_num = 0
        
        try:
            while self.is_running and self.questions_asked < max_total:
                batch_num += 1
                batch_facts = 0
                
                print(f"\n📦 Batch {batch_num} ({self.questions_asked}/{max_total}):")
                
                for i in range(questions_per_batch):
                    if not self.is_running:
                        break
                    if self.questions_asked >= max_total:
                        break
                    
                    # Smart topic selection
                    topic = self._smart_pick_topic(explored_topics)
                    question = self._smart_question(topic, asked_questions)
                    
                    # Skip if already asked
                    q_hash = question.lower().strip()
                    if q_hash in asked_questions:
                        continue
                    asked_questions.add(q_hash)
                    explored_topics.add(topic.lower())
                    
                    # Ask and learn
                    answer = self._ask_llm(question)
                    
                    if answer:
                        facts = self._extract_and_learn(question, answer, topic)
                        batch_facts += facts
                        self.facts_learned += facts
                        
                        # Learn NEW topics from answer
                        new_topics = self._discover_topics(answer)
                        self.seed_topics.extend(new_topics)
                    
                    self.questions_asked += 1
                    
                    # Small delay
                    time.sleep(delay)
                
                # Batch summary
                current_stats = self.memory.get_brain_stats()
                elapsed = (time.time() - start_time) / 60
                
                print(f"   ✅ Batch {batch_num}: +{batch_facts} facts")
                print(f"   📊 Total: {current_stats['facts_known']} facts | "
                      f"{self.questions_asked} questions | "
                      f"{elapsed:.1f} min")
                print(f"   🧠 Topics explored: {len(explored_topics)}")
                
                # Save progress
                self._save_progress(explored_topics, asked_questions)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹ Learning stopped by user!")
        
        self.is_running = False
        
        # Final report
        stats_after = self.memory.get_brain_stats()
        total_time = (time.time() - start_time) / 60
        
        print(f"\n{'='*60}")
        print(f"🏆 INFINITE LEARNING SESSION COMPLETE!")
        print(f"{'='*60}")
        print(f"   Duration:         {total_time:.1f} minutes")
        print(f"   Questions asked:  {self.questions_asked}")
        print(f"   Facts learned:    {self.facts_learned}")
        print(f"   Topics explored:  {len(explored_topics)}")
        print(f"   Brain before:     {stats_before['facts_known']} facts")
        print(f"   Brain after:      {stats_after['facts_known']} facts")
        print(f"   NEW knowledge:    {stats_after['facts_known'] - stats_before['facts_known']} facts!")
        print(f"   Learning rate:    {self.facts_learned/max(total_time,0.1):.1f} facts/min")
        print(f"{'='*60}")
        
        return {
            'duration_min': round(total_time, 1),
            'questions': self.questions_asked,
            'facts': self.facts_learned,
            'topics': len(explored_topics),
            'before': stats_before['facts_known'],
            'after': stats_after['facts_known']
        }
    
    def _smart_pick_topic(self, explored):
        """Pick topic SMARTLY - prioritize unexplored areas!"""
        
        # 40% chance: Pick from seed topics (not yet explored)
        unexplored_seeds = [t for t in self.seed_topics if t.lower() not in explored]
        if unexplored_seeds and random.random() < 0.4:
            return random.choice(unexplored_seeds)
        
        # 30% chance: Pick from learned facts (expand knowledge!)
        facts = self.memory.get_all_facts(100)
        if facts and random.random() < 0.3:
            fact = random.choice(facts)
            topic = fact['key'].replace('_fact', '').replace('_', ' ').strip()
            if len(topic) > 3 and topic.lower() not in explored:
                return topic
        
        # 20% chance: Combine two known topics
        if len(facts) >= 2 and random.random() < 0.2:
            f1, f2 = random.sample(facts[:50], 2)
            combined = f"{f1['key']} and {f2['key']}"
            return combined[:50]
        
        # 10% chance: Random from all seeds
        return random.choice(self.seed_topics)
    
    def _smart_question(self, topic, asked_already):
        """Generate SMART question that hasn't been asked"""
        
        # Try different templates
        templates = list(self.question_templates)
        random.shuffle(templates)
        
        for template in templates:
            question = template.format(topic=topic)
            if question.lower() not in asked_already:
                return question
        
        # Advanced questions if basic ones exhausted
        advanced = [
            f"What is the mathematical foundation of {topic}?",
            f"How has {topic} evolved over the last decade?",
            f"What are the current research challenges in {topic}?",
            f"Compare {topic} with similar approaches.",
            f"What are the ethical implications of {topic}?",
            f"How does {topic} impact society?",
            f"What skills are needed to work in {topic}?",
            f"What are the latest breakthroughs in {topic}?",
            f"How is {topic} used in industry?",
            f"What tools and frameworks are used in {topic}?"
        ]
        
        for q in advanced:
            if q.lower() not in asked_already:
                return q
        
        return f"Tell me everything important about {topic}"
    
    def _discover_topics(self, text):
        """Find new topics mentioned in answer"""
        import re
        
        new_topics = []
        
        # Find capitalized phrases (likely proper nouns/topics)
        caps = re.findall(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
        for cap in caps:
            if len(cap) > 4 and cap not in self.seed_topics:
                new_topics.append(cap)
        
        # Find quoted terms
        quoted = re.findall(r'"([^"]+)"', text)
        for q in quoted:
            if len(q) > 3 and q not in self.seed_topics:
                new_topics.append(q)
        
        # Limit new topics
        return list(set(new_topics))[:5]
    
    def _save_progress(self, explored, asked):
        """Save learning progress to file"""
        try:
            progress = {
                'timestamp': datetime.now().isoformat(),
                'questions_asked': self.questions_asked,
                'facts_learned': self.facts_learned,
                'topics_explored': list(explored)[:100],
                'total_questions_ever': len(asked)
            }
            
            with open('data/learning_progress.json', 'w') as f:
                json.dump(progress, f, indent=2)
        except:
            pass