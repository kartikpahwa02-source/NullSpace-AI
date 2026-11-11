"""
EmptySpace AI Self-Learning System
- User preferences seekhna
- Mistakes se seekhna
- Patterns identify karna
- Knowledge base build karna
"""

from brain.llm import ask_llm_direct
from memory.memory import (
    learn, get_learned, update_user_profile,
    get_user_profile, add_task_history
)


def learn_user_preference(user_input, context=""):
    """User ki preference samjho aur store karo"""
    existing = get_user_profile()

    prompt = f"""Analyze this user input and extract preferences.

User said: "{user_input}"
Context: {context}
Existing preferences: {existing}

Extract:
- language_preference (Hindi/English/Hinglish)
- tone_preference (formal/casual/friendly)
- interests (topics user likes)
- tools_used (what tools user uses most)
- any other preference

Reply ONLY with JSON:
{{"key": "value", "key2": "value2"}}"""

    result = ask_llm_direct(prompt)

    # Parse and store
    try:
        import json
        s = result.find("{")
        e = result.rfind("}") + 1
        if s != -1 and e > s:
            prefs = json.loads(result[s:e])
            for k, v in prefs.items():
                update_user_profile(k, v)
            return f"Preferences updated: {prefs}"
    except Exception:
        pass

    return "Learning from input..."


def learn_from_mistake(task, error, correction=""):
    """Galti se seekhna"""
    learn("mistakes", {
        "task": task,
        "error": error,
        "correction": correction,
        "lesson": f"Next time for '{task}', avoid: {error}"
    })

    prompt = f"""AI made a mistake:
Task: {task}
Error: {error}
Correction: {correction}

What should AI learn from this?
Give ONE clear lesson."""

    lesson = ask_llm_direct(prompt)
    learn("lessons", lesson)
    return lesson


def learn_successful_pattern(task, steps, result):
    """Successful pattern yaad rakho"""
    learn("successful_patterns", {
        "task": task,
        "steps": steps,
        "result": result
    })
    return "Pattern stored for future use."


def get_relevant_knowledge(query):
    """Query ke liye relevant knowledge nikalo"""
    all_learned = get_learned()

    if not all_learned:
        return "No prior knowledge found."

    # Build knowledge context
    knowledge_parts = []
    for key, entries in all_learned.items():
        for entry in entries[-3:]:  # Last 3 entries per category
            knowledge_parts.append(f"[{key}]: {entry.get('value', '')}")

    if not knowledge_parts:
        return "No prior knowledge found."

    knowledge = "\n".join(knowledge_parts[:15])

    prompt = f"""Based on your learned knowledge, answer this query:

Query: {query}

Your Knowledge:
{knowledge}

Provide relevant information from your knowledge.
If nothing relevant, say so."""

    return ask_llm_direct(prompt)


def improve_response(user_input, initial_response, feedback=""):
    """Response ko improve karo feedback se"""
    prompt = f"""Improve this AI response based on feedback.

User input: {user_input}
Initial response: {initial_response}
User feedback: {feedback}

Give improved response in Hindi/English/Hinglish."""

    improved = ask_llm_direct(prompt)

    learn("improvements", {
        "original": initial_response,
        "improved": improved,
        "feedback": feedback
    })

    return improved


def summarize_learning():
    """Ab tak kya seekha hai - summary do"""
    all_learned = get_learned()
    profile = get_user_profile()

    prompt = f"""Summarize what EmptySpace AI has learned so far:

User Profile: {profile}
Learned Data: {str(all_learned)[:3000]}

Give a brief summary of:
1) What AI knows about the user
2) Key lessons learned
3) Mistakes to avoid
4) Successful patterns

In Hindi/English/Hinglish."""

    return ask_llm_direct(prompt)