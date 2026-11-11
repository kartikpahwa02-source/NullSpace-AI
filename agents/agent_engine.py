import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from brain.llm import chat, check_nkj_status

# AGI Core
try:
    from brain.agi_core import AGI_Core
    agi = AGI_Core()
    AGI_OK = True
except Exception as e:
    agi = None
    AGI_OK = False
    print(f"AGI Core: {e}")

conversations = {}

SYSTEM = """You are NKJ EmptyNSpace AI, created by Nikhil Jatav.
You are an autonomous AI with self-learning capability.
You can learn new facts, recall knowledge, and improve over time.
Be helpful, friendly, and honest."""

def run_agent(user_message, conv_id='default'):
    if not check_nkj_status():
        # Try AGI Core offline
        if AGI_OK:
            result = agi.process(user_message)
            return {'response': result['response'], 'type': 'message', 'agents_used': ['AGI_Core']}
        return {'response': 'AI offline.', 'type': 'error', 'agents_used': []}
    
    if conv_id not in conversations:
        conversations[conv_id] = []
    history = conversations[conv_id]
    
    # Check AGI commands first
    if AGI_OK:
        lower = user_message.lower()
        
        # Direct AGI commands
        if any(w in lower for w in ['learn ', 'teach ', 'remember ', 'brain stats', 
                                     'what do you know', 'help', 'reset brain']):
            result = agi.process(user_message)
            return {'response': result['response'], 'type': 'message', 
                    'agents_used': ['AGI_Core'], 'agi_stats': {
                        'facts': result['facts_used'],
                        'score': result['reflection_score']
                    }}
    
    # Build context with AGI knowledge
    agi_context = ""
    if AGI_OK:
        thinking = agi.reasoner.think(user_message)
        if thinking['facts_used'] > 0:
            agi_context = f"\n\nYour stored knowledge:\n{thinking['context']}"
    
    messages = [{"role": "system", "content": SYSTEM + agi_context}]
    messages.extend(history[-10:])
    messages.append({"role": "user", "content": user_message})
    
    response = chat(messages)
    
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": response})
    
    # AGI: Learn from conversation
    if AGI_OK:
        agi.learner.learn_from_text(user_message, 'conversation')
        agi.learner.learn_from_text(response, 'ai_response')
        agi.reflector.reflect_on_response(user_message, response)
    
    # Detect agent
    agent = 'NKJ_AI'
    lower = user_message.lower()
    if any(kw in lower for kw in ['open','browse','search']): agent = 'BrowserAgent'
    elif any(kw in lower for kw in ['code','python']): agent = 'CodeAgent'
    elif any(kw in lower for kw in ['call','phone']): agent = 'PhoneAgent'
    
    return {'response': response, 'type': 'message', 'agents_used': [agent]}

def confirm_action(conv_id='default'):
    return {'response': 'Confirmed!', 'type': 'message'}

def reject_action(conv_id='default'):
    return {'response': 'Cancelled.', 'type': 'message'}