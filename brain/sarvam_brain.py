from sarvamai import SarvamAI
from config.settings import SARVAM_API_KEY, SARVAM_LLM_MODEL

_client = None

def get_sarvam():
    global _client
    if _client is None:
        _client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
    return _client


def sarvam_chat(messages):
    """Sarvam AI se chat karo"""
    try:
        client = get_sarvam()

        response = client.chat.completions.create(
            model=SARVAM_LLM_MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Sarvam AI Error: {e}"


def sarvam_ask(prompt, history=None):
    """Simple prompt → response"""
    messages = []
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    return sarvam_chat(messages)