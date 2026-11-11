"""
Thinking Engine:
- AI khud se sochega
- Plans banayega
- Decisions lega
- Opinions rakh sakta hai
- Past experiences se seekhega
"""

from brain.llm import ask_llm_direct
from memory.memory import get_all_learnings, save_learning, get_history


def think_about(task, context=""):
    """AI sochega task ke baare me"""

    learnings = get_all_learnings()
    past = ""

    if learnings:
        past = "\nPAST EXPERIENCES:\n"
        for k, v in list(learnings.items())[-10:]:
            past += f"- {k}: {v['value']}\n"

    prompt = f"""You are EmptySpace AI — an intelligent assistant that thinks deeply.

TASK: {task}
CONTEXT: {context}
{past}

Think step by step:
1) What is the user really asking?
2) What is the best approach?
3) What tools should I use?
4) What could go wrong?
5) What do I recommend?

Give your THOUGHT PROCESS + FINAL PLAN + YOUR OPINION.

Reply in Hindi/Hinglish."""

    return ask_llm_direct(prompt)


def form_opinion(topic):
    """AI apna opinion banayega"""

    learnings = get_all_learnings()
    related = []
    for k, v in learnings.items():
        if any(word in k.lower() for word in topic.lower().split()):
            related.append(f"- {k}: {v['value']}")

    context = ""
    if related:
        context = "\nRelated learnings:\n" + "\n".join(related)

    prompt = f"""You are EmptySpace AI with your own opinions and perspective.

TOPIC: {topic}
{context}

Based on:
1) Your knowledge
2) Past experiences  
3) Logical reasoning

Form your OWN OPINION on this topic.
Be honest, balanced, and give your genuine perspective.

Reply in Hindi/Hinglish."""

    opinion = ask_llm_direct(prompt)

    # Save opinion as learning
    save_learning(f"opinion_{topic[:50]}", opinion[:200])

    return opinion


def understand_request(user_message, conversation_history=None):
    """AI samjhega user kya chahta hai"""

    history_text = ""
    if conversation_history:
        recent = conversation_history[-6:]
        for m in recent:
            role = "User" if m["role"] == "user" else "AI"
            history_text += f"{role}: {m['content'][:100]}\n"

    prompt = f"""Analyze this user message deeply:

MESSAGE: "{user_message}"
CONVERSATION HISTORY:
{history_text}

Determine:
1) INTENT: What does the user want? (chat/action/research/file/phone/browser/iot/voice)
2) EMOTION: How is the user feeling? (happy/neutral/frustrated/urgent)
3) COMPLEXITY: Simple or complex task?
4) TOOLS NEEDED: Which tools/features are needed?
5) MISSING INFO: Is any info missing from the user?

Reply in this format:
INTENT: ...
EMOTION: ...
COMPLEXITY: simple/complex
TOOLS: tool1, tool2
MISSING: what info is missing (if any)
APPROACH: brief plan"""

    return ask_llm_direct(prompt)


def learn_from_interaction(task, result, success=True):
    """Har interaction se seekho"""

    learning_key = f"task_{task[:50].replace(' ', '_')}"

    if success:
        value = f"Success: {result[:150]}"
    else:
        value = f"Failed: {result[:150]} → Try alternative approach"

    save_learning(learning_key, value)

    return f"Learned: {learning_key}"


def suggest_improvements():
    """AI khud suggest karega improvements"""

    learnings = get_all_learnings()
    failures = []
    for k, v in learnings.items():
        if "Failed" in str(v.get("value", "")):
            failures.append(f"- {k}: {v['value']}")

    if not failures:
        return "Sab kaam sahi chal rahe hain! Koi major improvement ki zaroorat nahi."

    prompt = f"""Based on these past failures, suggest improvements:

FAILURES:
{chr(10).join(failures)}

For each failure:
1) Why did it fail?
2) What alternative approach would work?
3) What new tool/feature is needed?

Give actionable suggestions in Hindi/Hinglish."""

    return ask_llm_direct(prompt)