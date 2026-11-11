"""
World Knowledge — Internet se knowledge crawl + store karo
"""

import requests
from bs4 import BeautifulSoup
from brain.knowledge_base import add_knowledge, add_fact, search_knowledge, search_facts
from brain.llm import ask_llm_direct

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def learn_about(topic):
    """Topic ke baare me sab kuch seekho"""
    # Step 1: Check existing knowledge
    existing = search_knowledge(topic, limit=3)
    if existing:
        existing_text = "\n".join([f"- {r['content'][:200]}" for r in existing])
    else:
        existing_text = "No prior knowledge"

    # Step 2: Web se nayi knowledge lo
    web_results = _search_web(topic)

    # Step 3: Wikipedia se lo
    wiki_result = _search_wikipedia(topic)

    # Step 4: AI se summary lo
    prompt = f"""Research this topic thoroughly: "{topic}"

Existing Knowledge:
{existing_text}

Web Results:
{web_results}

Wikipedia:
{wiki_result}

Provide:
1) Complete detailed explanation
2) Key facts (bullet points)
3) Important dates/numbers
4) Related topics
5) Interesting facts

Reply in Hindi/English/Hinglish."""

    detailed = ask_llm_direct(prompt)

    # Step 5: Store in database
    add_knowledge(topic, detailed, source="web_research", category="research", confidence=0.8)

    # Step 6: Extract and store individual facts
    facts_prompt = f"""Extract 5-10 individual facts from this text.
Reply ONLY with JSON array:
[{{"entity":"...", "fact":"...", "category":"..."}}, ...]

Text:
{detailed[:2000]}"""

    facts_text = ask_llm_direct(facts_prompt)

    try:
        import json
        s = facts_text.find("[")
        e = facts_text.rfind("]") + 1
        if s != -1 and e > s:
            facts = json.loads(facts_text[s:e])
            for f in facts:
                add_fact(f.get("entity", topic), f.get("fact", ""), f.get("category", "general"), "web_research")
    except Exception:
        pass

    return detailed


def learn_from_url(url):
    """URL se knowledge extract karo"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)[:5000]
        title = soup.title.string if soup.title else url

        # AI se summary
        prompt = f"Summarize this webpage:\nTitle: {title}\n\nContent:\n{text[:3000]}\n\nProvide key facts and important information."
        summary = ask_llm_direct(prompt)

        # Store
        add_knowledge(title, summary, source=url, category="web", confidence=0.7)
        add_fact(title, summary[:500], "web_content", url)

        return f"Learned from: {title}\n\n{summary}"

    except Exception as e:
        return f"Learning Error: {e}"


def learn_from_text(text, topic="general"):
    """Kisi bhi text se seekho"""
    prompt = f"""Extract all important facts and knowledge from this text:

{text[:3000]}

Reply with:
1) Key topics
2) Important facts
3) Summary"""

    extracted = ask_llm_direct(prompt)
    add_knowledge(topic, extracted, source="user_input", category="learned", confidence=0.6)
    return extracted


def _search_web(query):
    """DuckDuckGo se search karo"""
    try:
        from tools.web_scraper import search_web
        results = search_web(query, num=5)
        text = ""
        for i, r in enumerate(results, 1):
            text += f"{i}. {r['title']}\n   {r['snippet']}\n\n"
        return text if text else "No web results"
    except Exception as e:
        return f"Search error: {e}"


def _search_wikipedia(topic):
    """Wikipedia se information lo"""
    try:
        import wikipedia
        wikipedia.set_lang("en")
        summary = wikipedia.summary(topic, sentences=5)
        return summary
    except Exception:
        try:
            import wikipedia
            wikipedia.set_lang("hi")
            summary = wikipedia.summary(topic, sentences=3)
            return summary
        except Exception:
            return "Wikipedia me nahi mila"


def get_knowledge_report():
    """Apni knowledge ka report do"""
    from brain.knowledge_base import get_stats, get_skills

    stats = get_stats()
    skills = get_skills()

    report = "📊 EmptySpace AI Knowledge Report\n\n"
    report += f"📚 Knowledge entries: {stats.get('knowledge', 0)}\n"
    report += f"💬 Conversations: {stats.get('conversations', 0)}\n"
    report += f"🧠 Skills learned: {stats.get('skills', 0)}\n"
    report += f"🔄 Patterns: {stats.get('patterns', 0)}\n"
    report += f"🌍 World facts: {stats.get('world_facts', 0)}\n"
    report += f"💻 Code written: {stats.get('code_history', 0)}\n"
    report += f"❌ Mistakes: {stats.get('mistakes', 0)}\n"

    if skills:
        report += "\n🎯 Top Skills:\n"
        for s in skills[:5]:
            report += f"  - {s['skill_name']}: {s['proficiency']:.0%} ({s['times_used']}x)\n"

    return report