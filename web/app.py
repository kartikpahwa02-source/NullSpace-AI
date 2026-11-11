import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from agents.agent_engine import run_agent, confirm_action, reject_action
from brain.llm import check_nkj_status

app = FastAPI(title="NKJ EmptyNSpace AI")

# Serve static files if exists
if os.path.exists(os.path.join(os.path.dirname(__file__), 'static')):
    app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), 'static')), name="static")


class ChatRequest(BaseModel):
    message: str
    conv_id: str = "default"


class ActionRequest(BaseModel):
    conv_id: str = "default"


@app.get("/", response_class=HTMLResponse)
async def home():
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return get_default_page()


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        result = run_agent(req.message, req.conv_id)
        return result
    except Exception as e:
        return {"response": f"Error: {str(e)}", "type": "error", "agents_used": []}


@app.post("/confirm")
async def confirm(req: ActionRequest):
    return confirm_action(req.conv_id)


@app.post("/reject")
async def reject(req: ActionRequest):
    return reject_action(req.conv_id)


@app.get("/status")
async def status():
    return {
        "ollama": check_nkj_status(),
        "name": "NKJ EmptyNSpace AI",
        "version": "7.0",
        "creator": "Nikhil Jatav"
    }


def get_default_page():
    return """
<!DOCTYPE html>
<html>
<head>
<title>NKJ EmptyNSpace AI</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#050A14;--card:#0F1D32;--accent:#38BDF8;--text:#F0F6FC;--muted:#7B8CA8;--border:rgba(56,189,248,.1);--gradient:linear-gradient(135deg,#38BDF8,#818CF8)}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}

nav{padding:16px 24px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--border);backdrop-filter:blur(20px);position:sticky;top:0;z-index:100;background:rgba(5,10,20,.9)}
.logo{font-size:1.3em;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.status{font-size:.85em;display:flex;align-items:center;gap:6px}
.online{color:#34D399}.offline{color:#F87171}
.dot{width:8px;height:8px;border-radius:50%;animation:pulse 2s infinite}
.dot-on{background:#34D399}.dot-off{background:#F87171}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

.container{max-width:800px;margin:0 auto;padding:20px;display:flex;flex-direction:column;height:calc(100vh - 60px)}
.chat-area{flex:1;overflow-y:auto;padding:20px 0;scroll-behavior:smooth}

.msg{margin:12px 0;padding:14px 18px;border-radius:16px;max-width:85%;animation:msgIn .4s ease;font-size:.95em;line-height:1.6;word-wrap:break-word}
@keyframes msgIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.bot{background:var(--card);border:1px solid var(--border);border-bottom-left-radius:4px}
.user{background:var(--gradient);margin-left:auto;border-bottom-right-radius:4px;color:white}
.agent-tag{font-size:.7em;color:var(--accent);margin-top:8px;opacity:.7}
.typing{color:var(--muted);font-style:italic}

.welcome{text-align:center;padding:60px 20px}
.welcome h1{font-size:2.2em;font-weight:800;margin-bottom:12px}
.welcome h1 span{background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.welcome p{color:var(--muted);font-size:1em;margin-bottom:32px}
.chips{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.chip{padding:8px 16px;background:rgba(56,189,248,.08);border:1px solid rgba(56,189,248,.15);border-radius:100px;color:var(--accent);font-size:.85em;cursor:pointer;transition:all .3s}
.chip:hover{background:rgba(56,189,248,.15);transform:translateY(-2px)}

.input-area{display:flex;gap:10px;padding:16px 0;border-top:1px solid var(--border)}
.input-area input{flex:1;padding:14px 20px;border:1px solid var(--border);border-radius:14px;background:var(--card);color:white;font-size:.95em;font-family:inherit;outline:none;transition:border .3s}
.input-area input:focus{border-color:var(--accent)}
.input-area button{padding:14px 24px;background:var(--gradient);border:none;border-radius:14px;color:white;font-weight:700;cursor:pointer;font-size:.95em;transition:all .3s}
.input-area button:hover{transform:scale(1.02);box-shadow:0 4px 20px rgba(56,189,248,.3)}

.info-bar{display:flex;gap:16px;justify-content:center;padding:8px 0;font-size:.75em;color:var(--muted)}
</style>
</head>
<body>

<nav>
<div class="logo">⚡ NKJ EmptyNSpace</div>
<div class="status" id="statusBar"><span class="dot dot-off"></span><span class="offline">Checking...</span></div>
</nav>

<div class="container">
<div class="chat-area" id="chat">
<div class="welcome">
<h1>Welcome to <span>NKJ EmptyNSpace</span></h1>
<p>Autonomous AI by Nikhil Jatav • Powered by NKJ Law</p>
<div class="chips">
<div class="chip" onclick="ask('Hello!')">👋 Hello</div>
<div class="chip" onclick="ask('What is NKJ Law?')">🧠 NKJ Law</div>
<div class="chip" onclick="ask('Who created you?')">👤 Creator</div>
<div class="chip" onclick="ask('What can you do?')">🛠️ Capabilities</div>
<div class="chip" onclick="ask('Search latest AI news')">🔍 AI News</div>
<div class="chip" onclick="ask('Write Python code for fibonacci')">💻 Code</div>
</div>
</div>
</div>

<div class="info-bar">
<span>🧠 NKJ Engine Active</span>
<span id="queryCount">📊 Queries: 0</span>
</div>

<div class="input-area">
<input type="text" id="input" placeholder="Ask NKJ EmptyNSpace anything..." onkeypress="if(event.key==='Enter')send()">
<button onclick="send()">Send →</button>
</div>
</div>

<script>
let queries = 0;

// Check status
async function checkStatus() {
    try {
        const r = await fetch('/status');
        const data = await r.json();
        const bar = document.getElementById('statusBar');
        if (data.ollama) {
            bar.innerHTML = '<span class="dot dot-on"></span><span class="online">Online • NKJ Law Active</span>';
        } else {
            bar.innerHTML = '<span class="dot dot-off"></span><span class="offline">Ollama Offline</span>';
        }
    } catch(e) {
        document.getElementById('statusBar').innerHTML = '<span class="dot dot-off"></span><span class="offline">Error</span>';
    }
}
checkStatus();
setInterval(checkStatus, 10000);

function ask(text) {
    document.getElementById('input').value = text;
    send();
}

async function send() {
    const input = document.getElementById('input');
    const chat = document.getElementById('chat');
    const msg = input.value.trim();
    if (!msg) return;

    const welcome = chat.querySelector('.welcome');
    if (welcome) welcome.remove();

    chat.innerHTML += '<div class="msg user">' + escapeHtml(msg) + '</div>';
    input.value = '';

    const typingId = 'typing_' + Date.now();
    chat.innerHTML += '<div class="msg bot typing" id="' + typingId + '">⏳ Thinking...</div>';
    chat.scrollTop = chat.scrollHeight;

    queries++;
    document.getElementById('queryCount').textContent = '📊 Queries: ' + queries;

    try {
        const startTime = Date.now();
        const res = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg})
        });
        const data = await res.json();
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

        const el = document.getElementById(typingId);
        if (el) el.remove();

        const agents = data.agents_used ? data.agents_used.join(', ') : 'NKJ_AI';
        const tag = '<div class="agent-tag">🤖 ' + agents + ' • ' + elapsed + 's</div>';

        chat.innerHTML += '<div class="msg bot">' + escapeHtml(data.response) + tag + '</div>';
    } catch(e) {
        const el = document.getElementById(typingId);
        if (el) el.remove();
        chat.innerHTML += '<div class="msg bot">❌ Connection error. Is Ollama running?</div>';
    }

    chat.scrollTop = chat.scrollHeight;
    input.focus();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
</script>

</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    print("\n⚡ NKJ EmptyNSpace AI")
    print("🌐 Open: http://localhost:8000\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)