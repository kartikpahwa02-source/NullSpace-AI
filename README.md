<div align="center">

# 🤖 EmptyNSpace AI

### Autonomous Multi-Agent AI System with Self-Learning

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/Agents-10+-purple.svg)]()
[![Facts](https://img.shields.io/badge/Facts_Learned-13K+-orange.svg)]()

An AI system that doesn't just talk — it **acts**, **learns**, and **remembers**.

Built solo by [Nikhil Jatav](https://niknote.online) on a single laptop.

[Features](#features) · [Quick Start](#quick-start) · [Architecture](#architecture) · [Results](#results) · [Other Projects](#other-projects)

</div>

---

## 🎯 What Is This?

EmptyNSpace AI is an autonomous multi-agent system that can:

- **Control hardware** — your phone (ADB), browser (Selenium), IoT devices
- **Learn autonomously** — taught itself 13,093 facts in 9 hours
- **Remember everything** — persistent SQLite knowledge base
- **Reason about knowledge** — finds connections between facts
- **Speak your language** — 8+ Indian languages supported
- **Run 10+ specialized agents** — each expert in its domain

All running on **one laptop** (RTX 3050, 4GB VRAM). No cloud. No funding.

---

## 📊 Self-Learning Results


Session Duration: 9 hours
Questions Generated: 4,932
Topics Explored: 4,352
Facts Stored: 13,093
Derived Facts: 648 (through basic reasoning)
Learning Rate: 65 facts/minute
Human Input: Zero


**Note:** This is autonomous knowledge collection, not semantic understanding. The system stores and retrieves text patterns — it does not "comprehend" in the human sense.

---

## 🤖 Agents

| Agent | What It Does | Tech |
|-------|-------------|------|
| 💬 Chat | Natural conversation | Ollama LLM |
| 💻 Code | Write, run, debug Python | Code executor |
| 📱 Phone | Calls, SMS, WhatsApp, screenshots | Android ADB |
| 🌐 Browser | Web automation, form filling | Selenium |
| 🔍 Research | Web search, Wikipedia crawling | DuckDuckGo |
| 📸 Photo | Image editing, filters, crop | Pillow |
| 🏠 SmartHome | IoT device control | Custom |
| ⚙️ Automation | PC app control, auto-typing | OS commands |
| 📁 File | File management operations | Python OS |
| 🖥️ System | System info, monitoring | Platform |
## 🧠 Brain Architecture

The system autonomously generated questions, queried a local LLM, extracted facts, and stored them permanently — with zero human input.

User Query
│
▼
┌──────────────────┐
│ Master Agent │ ← Routes to correct agent
│ (Query Router) │
└────────┬─────────┘
│
┌────┼────┐
▼ ▼ ▼
┌──────┐┌──────┐┌──────┐
│ AGI ││Smart ││Inter-│
│ Core ││Brain ││net │
│ ││(RAG) ││Learn │
└──┬───┘└──┬───┘└──┬───┘
│ │ │
▼ ▼ ▼
┌──────────────────────┐
│ SQLite Knowledge │
│ Base (13,093 facts) │
└──────────┬───────────┘
│
▼
┌──────────────────────┐
│ Reasoning Engine │
│ (Chain + Analogy) │
└──────────────────────┘


### Brain Components

| Component | File | Purpose |
|-----------|------|---------|
| AGI Core | `brain/agi_core.py` | Learn, remember, reason, reflect |
| Smart Brain | `brain/smart_brain.py` | RAG + Chain of Thought |
| Auto Learner | `brain/auto_learner.py` | Autonomous question-answer learning |
| Internet Learner | `brain/internet_learner.py` | Learn from Wikipedia, web search |
| Reasoning Engine | `brain/reasoning_engine.py` | Chain reasoning, analogy detection |
| LLM Engine | `brain/llm.py` | Ollama/Groq integration + caching |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11
- [Ollama](https://ollama.ai) installed
- NVIDIA GPU (optional, CPU works too)

### Installation


# Clone
git clone https://github.com/nikhilnikhil4331/EmptyNSpace-AI.git
cd EmptyNSpace-AI

# Install dependencies
pip install fastapi uvicorn requests beautifulsoup4 duckduckgo-search

# Download LLM model
ollama pull llama3.2:1b

# Start Ollama (in separate terminal)
ollama serve

Run (Terminal Mode)
Bash

python main.py
Run (Web Interface)
Bash

python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
# Open: http://localhost:8000
Run Auto-Learner
Bash

cd brain
python auto_learner.py
# Choose mode: Quick (10) / Medium (50) / Long (200) / Infinite



# Chat
You: Hello, who are you?
AI:  I am EmptyNSpace AI, created by Nikhil Jatav...

# Learn
You: learn Python is a programming language
AI:  ✅ Learned: Python = a programming language

# Recall
You: what is Python
AI:  Based on my knowledge: Python is a programming language...

# Brain Stats
You: brain stats
AI:  facts_known: 13,093 | reflections: 122 | skills: 5

# Internet Learning
You: wikipedia quantum computing
AI:  📚 Learned from Wikipedia: Quantum Computing (15 facts)

# Deep Learn
You: deep learn about machine learning
AI:  🧠 Sources: 2 | Facts learned: 25 | Connections: 4


EmptyNSpace-AI/
│
├── brain/                      # AI Brain
│   ├── llm.py                  # LLM engine (Ollama + caching)
│   ├── agi_core.py             # Core: learn, remember, reason
│   ├── auto_learner.py         # Autonomous self-learning
│   ├── internet_learner.py     # Web + Wikipedia learning
│   ├── reasoning_engine.py     # Chain reasoning + analogies
│   ├── smart_brain.py          # RAG + Chain of Thought
│   ├── nkj_engine.py           # Compression integration
│   ├── knowledge_base.py       # Knowledge management
│   ├── self_learner.py         # Self-improvement engine
│   ├── world_knowledge.py      # Web knowledge crawler
│   └── code_executor.py        # Code execution sandbox
│
├── agents/                     # AI Agents
│   ├── agent_engine.py         # Main agent router
│   ├── master_agent.py         # Master coordinator
│   ├── all_agents.py           # All specialized agents
│   ├── registry.py             # Agent registry
│   └── browser_agent.py        # Browser automation
│
├── tools/                      # Action Tools
│   ├── executor.py             # Tool router
│   ├── android_control.py      # Phone control (ADB)
│   ├── browser_auto.py         # Browser (Selenium)
│   ├── sarvam_voice.py         # Indian language voice
│   ├── photo_editor.py         # Image processing
│   ├── smart_home.py           # IoT control
│   ├── call_recorder.py        # Call recording
│   ├── image_search.py         # Image search
│   ├── signature_tool.py       # Digital signatures
│   └── file_downloader.py      # File transfer
│
├── web/                        # Web Interface
│   ├── app.py                  # FastAPI backend
│   └── templates/
│       └── index.html          # Frontend UI
│
├── config/                     # Configuration
│   └── settings.py             # API keys, model settings
│
├── memory/                     # Memory Management
│   └── memory.py               # Session memory
│
├── voice/                      # Voice Engine
│   └── voice_engine.py         # STT/TTS
│
├── main.py                     # Entry point (terminal)
└── requirements.txt            # Dependencies



🛠️ Tech Stack
Category	Technology
Language	Python 3.11
AI/LLM	Ollama (local), Groq API (cloud)
Backend	FastAPI
Database	SQLite
Voice	Sarvam AI (8+ Indian languages)
Phone	Android ADB
Browser	Selenium WebDriver
Image	Pillow
Search	DuckDuckGo
Frontend	HTML/CSS/JavaScript


⚠️ Limitations
Being transparent about what this system is and isn't:

Not AGI — This is autonomous knowledge collection, not general intelligence
No semantic understanding — Uses keyword matching, not meaning comprehension
Basic reasoning — Pattern matching between stored facts, not deep inference
Rule-based routing — Agent selection uses keywords, not ML classification
Hardware dependent — Phone/IoT features require specific device setup
Not peer-reviewed — All research is experimental and self-directed
Single user tested — No formal evaluation with external users


📊 Hardware
All development and testing done on:

text

Laptop:  Consumer-grade
GPU:     NVIDIA RTX 3050 (4GB VRAM)
RAM:     16 GB
Storage: SSD
OS:      Windows 11
Budget:  ₹0 (zero external funding)
Team:    Solo (1 person)


🔗 Other Projects by Nikhil Jatav
Project	Description	Link
NikNote.online	AI homework helper (live product!)	niknote.online
Power Encoding	Neural network compression research	GitHub
🤝 Contributing
Contributions welcome! Feel free to:

Open issues for bugs or suggestions
Submit pull requests
Share feedback
📄 License
MIT License — see LICENSE file.

📞 Contact
Nikhil Jatav

📧 Email: nikhiljatav200514@gmail.com
💻 GitHub: @nikhilnikhil4331
🌐 Website: niknote.online

<div align="center">
Built with ❤️ by Nikhil Jatav

Solo developer. One laptop. Zero funding. Unlimited curiosity.

⭐ Star this repo if you find it interesting!


6. Scroll down → "Commit changes" click karo
7. Message: "Update README with complete documentation"
8. "Commit changes" button!
