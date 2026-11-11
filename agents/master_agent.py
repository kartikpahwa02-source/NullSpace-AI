import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from brain.llm import chat, check_nkj_status

conversations = {}

def run_agent(user_message, conv_id="default"):
    if not check_nkj_status():
        return {"response": "NKJ AI offline.", "type": "error", "agents_used": []}
    if conv_id not in conversations:
        conversations[conv_id] = []
    history = conversations[conv_id]
    messages = [{"role": "system", "content": "You are NKJ AI by Nikhil."}]
    messages.extend(history[-10:])
    messages.append({"role": "user", "content": user_message})
    response = chat(messages)
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": response})
    agent = "NKJ_AI"
    lower = user_message.lower()
    if any(kw in lower for kw in ['open','browse','search']): agent = "BrowserAgent"
    elif any(kw in lower for kw in ['code','python']): agent = "CodeAgent"
    elif any(kw in lower for kw in ['call','phone']): agent = "PhoneAgent"
    return {"response": response, "type": "message", "agents_used": [agent]}

def confirm_action(conv_id="default"):
    return {"response": "Confirmed!", "type": "message"}

def reject_action(conv_id="default"):
    return {"response": "Cancelled.", "type": "message"}