import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# NAYA:
from agents.agent_engine import run_agent, confirm_action, reject_action
from brain.llm import check_nkj_status

app = FastAPI(title="NKJ AI")

class ChatRequest(BaseModel):
    message: str
    conv_id: str = "default"

# HTML UI directly in Python
UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NKJ AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #ffffff; --bg2: #f8fafc; --bg3: #f1f5f9;
            --text: #0f172a; --text2: #475569; --text3: #94a3b8;
            --border: #e2e8f0; --accent: #6366f1; --accent2: #818cf8;
            --accent-bg: rgba(99,102,241,0.08);
            --success: #10b981; --error: #ef4444;
        }
        [data-theme="dark"] {
            --bg: #0a0a0f; --bg2: #12121a; --bg3: #1a1a24;
            --text: #f8fafc; --text2: #94a3b8; --text3: #64748b;
            --border: #1e1e2e; --accent: #818cf8; --accent2: #a5b4fc;
            --accent-bg: rgba(129,140,248,0.12);
        }
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Inter',sans-serif; background:var(--bg); color:var(--text); height:100vh; display:flex; flex-direction:column; transition: background 0.3s, color 0.3s; }
        
        .header { padding:16px 24px; border-bottom:1px solid var(--border); display:flex; align-items:center; justify-content:space-between; background:var(--bg); }
        .logo { display:flex; align-items:center; gap:12px; }
        .logo-icon { width:42px; height:42px; background:linear-gradient(135deg,var(--accent),var(--accent2)); border-radius:12px; display:flex; align-items:center; justify-content:center; color:white; font-weight:700; font-size:1.1em; }
        .logo-text { font-size:1.2em; font-weight:700; }
        .logo-text span { color:var(--accent); }
        .header-btns { display:flex; gap:8px; }
        .h-btn { width:40px; height:40px; border-radius:10px; border:1px solid var(--border); background:var(--bg); color:var(--text2); cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:1.1em; transition:all 0.2s; }
        .h-btn:hover { background:var(--bg2); color:var(--accent); }
        
        .chat-area { flex:1; overflow-y:auto; padding:24px; }
        .chat-area::-webkit-scrollbar { width:6px; }
        .chat-area::-webkit-scrollbar-thumb { background:var(--border); border-radius:10px; }
        .chat-content { max-width:800px; margin:0 auto; }
        
        .welcome { text-align:center; padding:80px 20px; }
        .welcome-icon { width:80px; height:80px; background:linear-gradient(135deg,var(--accent),var(--accent2)); border-radius:20px; display:flex; align-items:center; justify-content:center; font-size:2em; margin:0 auto 24px; animation:float 3s ease-in-out infinite; }
        @keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
        .welcome h1 { font-size:1.8em; margin-bottom:8px; }
        .welcome p { color:var(--text2); margin-bottom:32px; }
        .suggestions { display:grid; grid-template-columns:1fr 1fr; gap:12px; max-width:600px; margin:0 auto; }
        .sug { padding:16px; background:var(--bg2); border:1px solid var(--border); border-radius:14px; cursor:pointer; text-align:left; transition:all 0.2s; }
        .sug:hover { border-color:var(--accent); transform:translateY(-2px); }
        .sug-icon { font-size:1.2em; margin-bottom:8px; }
        .sug-text { font-size:0.9em; color:var(--text2); }
        
        .msg { margin-bottom:24px; animation:fadeIn 0.3s; }
        @keyframes fadeIn { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
        .msg-row { display:flex; gap:14px; }
        .msg-avatar { width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; font-weight:600; font-size:0.9em; }
        .msg.user .msg-avatar { background:linear-gradient(135deg,#3b82f6,#60a5fa); color:white; }
        .msg.ai .msg-avatar { background:linear-gradient(135deg,var(--accent),var(--accent2)); color:white; }
        .msg-body { flex:1; }
        .msg-name { font-weight:600; font-size:0.9em; margin-bottom:6px; }
        .msg-text { font-size:0.95em; line-height:1.7; background:var(--bg2); border:1px solid var(--border); padding:14px 18px; border-radius:4px 16px 16px 16px; }
        .msg.user .msg-text { background:var(--accent); color:white; border:none; border-radius:16px 4px 16px 16px; }
        .msg-actions { display:flex; gap:6px; margin-top:8px; opacity:0; transition:opacity 0.2s; }
        .msg:hover .msg-actions { opacity:1; }
        .msg-btn { padding:6px 12px; border-radius:8px; border:1px solid var(--border); background:var(--bg); color:var(--text3); font-size:0.8em; cursor:pointer; transition:all 0.2s; }
        .msg-btn:hover { color:var(--accent); border-color:var(--accent); }
        
        .typing { display:flex; align-items:center; gap:14px; padding:16px 0; }
        .typing-dots { display:flex; gap:4px; }
        .typing-dot { width:8px; height:8px; background:var(--accent); border-radius:50%; animation:bounce 1.4s ease-in-out infinite; }
        .typing-dot:nth-child(2){animation-delay:0.2s} .typing-dot:nth-child(3){animation-delay:0.4s}
        @keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-8px)} }
        
        .input-area { padding:20px 24px 28px; border-top:1px solid var(--border); background:var(--bg); }
        .input-wrap { max-width:800px; margin:0 auto; }
        .input-box { display:flex; align-items:flex-end; gap:12px; padding:14px 18px; background:var(--bg2); border:2px solid var(--border); border-radius:20px; transition:all 0.2s; }
        .input-box:focus-within { border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-bg); }
        .input-box textarea { flex:1; background:none; border:none; outline:none; color:var(--text); font-size:0.95em; font-family:inherit; resize:none; max-height:150px; line-height:1.5; }
        .input-box textarea::placeholder { color:var(--text3); }
        .send-btn { width:44px; height:44px; border-radius:12px; border:none; background:var(--accent); color:white; cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:1.2em; transition:all 0.2s; }
        .send-btn:hover { background:var(--accent2); transform:scale(1.05); }
        .send-btn:disabled { background:var(--bg3); color:var(--text3); cursor:not-allowed; transform:none; }
        
        .confirm-btns { display:flex; gap:10px; margin-top:12px; }
        .c-btn { padding:10px 20px; border-radius:10px; border:none; font-weight:600; cursor:pointer; transition:all 0.2s; }
        .c-btn.yes { background:var(--success); color:white; }
        .c-btn.no { background:var(--bg3); color:var(--text); }
        .c-btn:hover { transform:translateY(-2px); }
        
        .toast { position:fixed; bottom:100px; left:50%; transform:translateX(-50%) translateY(20px); background:var(--text); color:var(--bg); padding:12px 24px; border-radius:10px; opacity:0; transition:all 0.3s; z-index:999; }
        .toast.show { opacity:1; transform:translateX(-50%) translateY(0); }
        
        @media(max-width:768px) { .suggestions{grid-template-columns:1fr} }
    </style>
</head>
<body data-theme="light">
    <header class="header">
        <div class="logo">
            <div class="logo-icon">N</div>
            <div class="logo-text">NKJ <span>AI</span></div>
        </div>
        <div class="header-btns">
            <button class="h-btn" onclick="toggleTheme()" id="themeBtn">☀️</button>
            <button class="h-btn" onclick="newChat()">✨</button>
        </div>
    </header>

    <div class="chat-area" id="chatArea">
        <div class="chat-content" id="chatContent">
            <div class="welcome" id="welcome">
                <div class="welcome-icon">✨</div>
                <h1>NKJ AI</h1>
                <p>Your Intelligent Assistant by Nikhil</p>
                <div class="suggestions">
                    <div class="sug" onclick="ask('Open YouTube')"><div class="sug-icon">🌐</div><div class="sug-text">Open YouTube</div></div>
                    <div class="sug" onclick="ask('Write Python code for calculator')"><div class="sug-icon">💻</div><div class="sug-text">Write Python code</div></div>
                    <div class="sug" onclick="ask('What is machine learning?')"><div class="sug-icon">🧠</div><div class="sug-text">Explain ML</div></div>
                    <div class="sug" onclick="ask('Tell me a budget plan under 5k')"><div class="sug-icon">💰</div><div class="sug-text">Budget plan under 5k</div></div>
                </div>
            </div>
            <div id="messages" style="display:none"></div>
            <div class="typing" id="typing" style="display:none">
                <div class="msg-avatar" style="background:linear-gradient(135deg,var(--accent),var(--accent2));color:white">✨</div>
                <div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>
            </div>
        </div>
    </div>

    <div class="input-area">
        <div class="input-wrap">
            <div class="input-box">
                <textarea id="input" placeholder="Message NKJ AI..." rows="1" onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}" oninput="this.style.height='auto';this.style.height=Math.min(this.scrollHeight,150)+'px';document.getElementById('sendBtn').disabled=!this.value.trim()"></textarea>
                <button class="send-btn" id="sendBtn" onclick="send()" disabled>↑</button>
            </div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        let cid = localStorage.getItem("cid") || crypto.randomUUID();
        localStorage.setItem("cid", cid);
        let processing = false;

        function toggleTheme() {
            const t = document.body.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            document.body.setAttribute('data-theme', t);
            document.getElementById('themeBtn').textContent = t === 'light' ? '☀️' : '🌙';
        }

        async function send() {
            const input = document.getElementById('input');
            const msg = input.value.trim();
            if (!msg || processing) return;
            processing = true;

            document.getElementById('welcome').style.display = 'none';
            document.getElementById('messages').style.display = 'block';

            addMsg(msg, 'user');
            input.value = '';
            input.style.height = 'auto';
            document.getElementById('sendBtn').disabled = true;
            document.getElementById('typing').style.display = 'flex';
            scrollDown();

            try {
                const res = await fetch("/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({message: msg, conv_id: cid})
                });
                const data = await res.json();
                document.getElementById('typing').style.display = 'none';

                if (data.type === "confirm") {
                    addConfirm(data.response);
                } else {
                    typeMsg(data.response, data.agents_used || []);
                }
            } catch(e) {
                document.getElementById('typing').style.display = 'none';
                addMsg("Connection error. Is Ollama running?", 'ai');
            }
            processing = false;
        }

        function typeMsg(text, agents) {
            const c = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = 'msg ai';
            let badge = agents.length ? `<span style="color:var(--accent);font-size:0.8em;margin-left:8px">${agents.join(', ')}</span>` : '';
            div.innerHTML = `<div class="msg-row"><div class="msg-avatar">✨</div><div class="msg-body"><div class="msg-name">NKJ AI ${badge}</div><div class="msg-text"></div><div class="msg-actions"><button class="msg-btn" onclick="copyMsg(this)">📋 Copy</button></div></div></div>`;
            c.appendChild(div);
            const el = div.querySelector('.msg-text');
            let i = 0;
            const iv = setInterval(() => {
                if (i < text.length) { el.innerHTML += text.charAt(i); i++; scrollDown(); }
                else clearInterval(iv);
            }, 12);
        }

        function addMsg(text, sender) {
            const c = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `msg ${sender}`;
            if (sender === 'user') {
                div.innerHTML = `<div class="msg-row"><div class="msg-avatar">N</div><div class="msg-body"><div class="msg-name">You</div><div class="msg-text">${esc(text)}</div></div></div>`;
            } else {
                div.innerHTML = `<div class="msg-row"><div class="msg-avatar">✨</div><div class="msg-body"><div class="msg-name">NKJ AI</div><div class="msg-text">${text}</div></div></div>`;
            }
            c.appendChild(div);
            scrollDown();
        }

        function addConfirm(text) {
            const c = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = 'msg ai';
            div.innerHTML = `<div class="msg-row"><div class="msg-avatar">✨</div><div class="msg-body"><div class="msg-name">NKJ AI</div><div class="msg-text">${text}<div class="confirm-btns"><button class="c-btn yes" onclick="doConfirm(true,this)">✓ Yes</button><button class="c-btn no" onclick="doConfirm(false,this)">✗ No</button></div></div></div></div>`;
            c.appendChild(div);
            scrollDown();
        }

        async function doConfirm(yes, btn) {
            btn.parentElement.innerHTML = 'Processing...';
            const res = await fetch(yes ? "/confirm" : "/reject", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message: "", conv_id: cid})
            });
            const data = await res.json();
            addMsg(data.response, 'ai');
        }

        function copyMsg(btn) {
            const text = btn.closest('.msg-body').querySelector('.msg-text').innerText;
            navigator.clipboard.writeText(text);
            btn.innerHTML = '✓ Copied';
            setTimeout(() => btn.innerHTML = '📋 Copy', 2000);
        }

        function ask(text) { document.getElementById('input').value = text; send(); }
        function newChat() { document.getElementById('welcome').style.display='block'; document.getElementById('messages').style.display='none'; document.getElementById('messages').innerHTML=''; cid=crypto.randomUUID(); }
        function scrollDown() { const a = document.getElementById('chatArea'); a.scrollTop = a.scrollHeight; }
        function esc(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }
        function toast(m) { const t = document.getElementById('toast'); t.textContent = m; t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 2500); }
    </script>
</body>
</html>
"""

@app.get("/")
async def home():
    return HTMLResponse(UI_HTML)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    result = process_query(request.message, request.conv_id)
    return result

@app.post("/confirm")
async def confirm_endpoint(request: ChatRequest):
    return confirm_action(request.conv_id)

@app.post("/reject")
async def reject_endpoint(request: ChatRequest):
    return reject_action(request.conv_id)

@app.get("/health")
async def health():
    return {"status": "online", "ai": "NKJ AI", "brain": "online" if check_nkj_status() else "offline"}