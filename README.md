# 🦊 GitLab GenAI Chatbot

> A Retrieval-Augmented Generation (RAG) chatbot that gives instant, cited answers from the [GitLab Handbook](https://handbook.gitlab.com/) and [Direction](https://about.gitlab.com/direction/) pages — powered by a local LLM, async web crawler, and Chroma Cloud vector database.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Cloud-orange)
![Ollama](https://img.shields.io/badge/Ollama-Llama3%208B-black?logo=ollama)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
  - [4. Set Up Ollama (Local LLM)](#4-set-up-ollama-local-llm)
  - [5. Run the Application](#5-run-the-application)
- [First-Time Ingestion](#-first-time-ingestion)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

This chatbot makes it easy for GitLab employees and aspiring employees to query GitLab's massive public documentation without having to manually navigate hundreds of pages. Ask a question in plain English and get a grounded, cited answer in seconds.

The system is built on a **RAG (Retrieval-Augmented Generation)** pipeline:

1. GitLab documentation is crawled asynchronously and stored as vector embeddings in **Chroma Cloud**
2. When a user asks a question, the most semantically relevant chunks are retrieved
3. A **locally running LLM** (Llama3 via Ollama) generates an answer using only the retrieved context — no hallucination
4. The answer is returned with **source links**, **page previews**, and **LLM-generated follow-up questions**

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Semantic Search** | Retrieves the most relevant documentation chunks using cosine similarity |
| 💬 **Multi-turn Conversations** | Per-session memory preserves context across follow-up questions |
| 📎 **Source Citations** | Every answer includes direct links to the original GitLab pages |
| 💡 **Suggested Questions** | LLM dynamically generates 3 contextually relevant follow-up prompts |
| 🛡️ **Guardrails** | The model is instructed to refuse questions not covered by retrieved context |
| ⚡ **Async Crawler** | Concurrent 5-worker async crawler ingests documentation 10x faster than sync |
| 🧠 **Semantic Chunking** | HTML-structure-aware chunking preserves paragraph and section context |
| 🖥️ **React UI** | ChatGPT-style interface with sidebar, history, and mobile responsiveness |
| 🔄 **Auto Ingestion** | Database populates automatically on first run — no manual steps needed |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        React Frontend                        │
│          (Vite + React 19 · Port 5173)                      │
│   Sidebar │ ChatWindow │ Message │ Suggestion Chips          │
└─────────────────────┬───────────────────────────────────────┘
                      │  POST /chat  (session-id header + text body)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend  (Port 7860)               │
│                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐  │
│  │ ChatMemory  │    │ RAG Service  │    │ ResponseBuilder│  │
│  │ (sessions)  │◄──►│ (orchestrate)│───►│ sources+preview│  │
│  └─────────────┘    └──────┬───────┘    └────────────────┘  │
│                            │                                  │
│          ┌─────────────────┼──────────────────┐              │
│          ▼                 ▼                  ▼              │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │  Retrieval   │  │PromptBuilder│  │   LLM Service    │    │
│  │  Service     │  │(context+hist│  │  (Ollama REST)   │    │
│  └──────┬───────┘  └─────────────┘  └──────────────────┘    │
│         │                                     │              │
│  ┌──────▼───────┐                   ┌─────────▼──────────┐  │
│  │  Embedding   │                   │   Ollama (local)   │  │
│  │  Service     │                   │   Llama3 8B        │  │
│  │(MiniLM-L6-v2)│                   └────────────────────┘  │
│  └──────┬───────┘                                           │
└─────────┼───────────────────────────────────────────────────┘
          │  vector search
          ▼
┌─────────────────────────────────────────────────────────────┐
│              Chroma Cloud (Vector Database)                  │
│         all-MiniLM-L6-v2 · cosine · 384-dim · "docs"        │
└─────────────────────────────────────────────────────────────┘
          ▲
          │  ingest on first startup
┌─────────┴───────────────────────────────────────────────────┐
│              Async Crawler  (ingestion/crawler.py)           │
│  aiohttp · 5 workers · semantic HTML chunking · batch flush  │
│  Sources: handbook.gitlab.com  +  about.gitlab.com/direction │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** — async Python web framework
- **[Uvicorn](https://www.uvicorn.org/)** — ASGI server
- **[Chroma Cloud](https://trychroma.com/)** — managed vector database
- **[sentence-transformers](https://www.sbert.net/)** — `all-MiniLM-L6-v2` for 384-dim embeddings
- **[aiohttp](https://docs.aiohttp.org/)** — async HTTP client for concurrent crawling
- **[BeautifulSoup4](https://beautiful-soup-4.readthedocs.io/)** — HTML parsing and semantic chunking
- **[Ollama](https://ollama.ai/)** — local LLM runtime
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** — environment variable loading

### Frontend
- **[React 19](https://react.dev/)** — UI framework
- **[Vite 8](https://vite.dev/)** — development server and bundler

### Model
- **[Llama3 8B](https://ollama.ai/library/llama3)** — local LLM for answer generation and suggestion creation

---

## ✅ Prerequisites

Make sure the following are installed before you begin:

| Tool | Minimum Version | Check Command | Install |
|---|---|---|---|
| Python | 3.10 | `python --version` | [python.org](https://www.python.org/downloads/) |
| Node.js | 18 | `node --version` | [nodejs.org](https://nodejs.org/) |
| npm | 8 | `npm --version` | Bundled with Node.js |
| Ollama | Latest | `ollama --version` | [ollama.ai](https://ollama.ai/) |
| Git | Any | `git --version` | [git-scm.com](https://git-scm.com/) |

You also need a **free [Chroma Cloud](https://trychroma.com/) account**. After signing up, create a database and note down your:
- API Key
- Tenant ID
- Database Name

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vishalmulimani007/genAI_chatbot.git
cd genAI_chatbot
```

---

### 2. Backend Setup

Navigate into the backend directory and set up a Python virtual environment:

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# macOS / Linux:
source venv/bin/activate

# Windows (Command Prompt):
venv\Scripts\activate.bat

# Windows (PowerShell):
venv\Scripts\Activate.ps1
```

> ✅ Your terminal prompt should now show `(venv)` at the start.

Install all Python dependencies:

```bash
pip install -r requirements.txt
```

> ⏳ This will take a few minutes on first run — it downloads PyTorch and sentence-transformers.

Verify the install:

```bash
python -c "import fastapi, chromadb, sentence_transformers, aiohttp; print('All imports OK')"
```

---

### 3. Configure Environment Variables

Inside the `backend/` directory, create a `.env` file with your Chroma Cloud credentials:

```bash
# backend/.env
CHROMA_API_KEY=your_chroma_cloud_api_key
CHROMA_TENANT=your_chroma_cloud_tenant_id
CHROMA_DATABASE=your_chroma_cloud_database_name
```

> ⚠️ **Never commit this file.** It is already listed in `.gitignore`.

**Where to find your Chroma credentials:**
1. Sign in at [trychroma.com](https://trychroma.com)
2. Create or open a database
3. Go to **Settings** → your API Key, Tenant ID, and Database name are displayed there

---

### 4. Set Up Ollama (Local LLM)

**Step 1 — Start the Ollama service** (keep this terminal open):

```bash
ollama serve
```

You should see: `Ollama is running on http://127.0.0.1:11434`

**Step 2 — Pull the Llama3 model** (~4.7 GB download, one time only):

```bash
ollama pull llama3:8b
```

**Step 3 — Verify it works:**

```bash
ollama run llama3:8b "Say hello in one sentence"
```

You should get a short response. Type `/bye` to exit.

---

### 5. Run the Application

You need **three terminals** running simultaneously:

#### Terminal 1 — Ollama LLM
```bash
ollama serve
```

#### Terminal 2 — FastAPI Backend
```bash
cd backend
source venv/bin/activate   # Windows: venv\Scripts\activate.bat
python main.py
```

#### Terminal 3 — React Frontend
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser. 🎉

---

## 🕷️ First-Time Ingestion

On the **very first startup**, the backend automatically detects that the Chroma database is empty and starts the async crawler. You will see output like this:

```
Connected to Chroma Cloud
Using collection: docs
Vector DB empty → Running crawler ingestion...
🔄 Crawling: https://handbook.gitlab.com/
🔄 Crawling: https://handbook.gitlab.com/handbook/values/
📦 14 chunks extracted
🚀 Stored 32 chunks
...
✅ Crawling finished
✅ Ingestion completed successfully.
INFO:     Uvicorn running on http://0.0.0.0:7860
```

> ⏳ **This takes 10–30 minutes** depending on your internet speed. It is a one-time process — all subsequent startups skip ingestion and boot in seconds.

On subsequent startups:
```
Connected to Chroma Cloud
Using collection: docs
✅ Vector DB already populated (N documents)
INFO:     Uvicorn running on http://0.0.0.0:7860
```

---

## 💬 Usage

1. Open **http://localhost:5173**
2. Click **+ New Chat** in the sidebar
3. Type your question and press **Enter** or click the send button
4. The bot replies with:
   - ✅ A grounded answer from GitLab documentation
   - 🔗 Source links to the original pages
   - 💡 3 suggested follow-up questions (click any chip to ask)
5. Continue the conversation — the bot remembers context within each session
6. Click **+ New Chat** to start a fresh session, or click any previous chat in the sidebar to switch back to it

**Example questions to try:**
- _"What are GitLab's core values?"_
- _"How does GitLab approach remote work?"_
- _"What is GitLab's hiring process for engineers?"_
- _"What is GitLab's product direction for AI features?"_

---

## 📁 Project Structure

```
.
├── backend/
│   ├── main.py                    # App entry point; auto-triggers ingestion
│   ├── config.json                # All tunable parameters (model, retrieval, etc.)
│   ├── config_loader.py           # Typed config reader
│   ├── .env                       # 🔒 Secrets — NEVER commit this
│   ├── requirements.txt           # Python dependencies
│   ├── inspect_chroma.py          # Dev utility: inspect Chroma collection
│   │
│   ├── api/
│   │   └── routes.py              # POST /chat · GET /health
│   │
│   ├── database/
│   │   └── chroma_client.py       # Chroma Cloud client (connect, query, insert)
│   │
│   ├── ingestion/
│   │   └── crawler.py             # Async crawler + semantic chunker + batch embedder
│   │
│   ├── services/
│   │   ├── rag_service.py         # 6-step RAG pipeline orchestrator
│   │   ├── retrieval_service.py   # Embed query → vector search → score filter
│   │   ├── embedding_service.py   # SentenceTransformer wrapper
│   │   ├── llm_service.py         # Ollama REST API integration
│   │   ├── chat_memory.py         # Per-session in-memory conversation history
│   │   └── query_rewriter.py      # Optional LLM query rewriter (unused)
│   │
│   ├── prompt/
│   │   └── prompt_builder.py      # Builds LLM prompt with context + history + guardrails
│   │
│   └── models/
│       └── response_builder.py    # Structures final API response
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Root component + all state + localStorage
│   │   ├── App.css                # Global styles
│   │   ├── main.jsx               # React entry point
│   │   └── components/
│   │       ├── ChatWindow.jsx     # Message list, input bar, API calls
│   │       ├── Message.jsx        # Single message bubble (sources + chips)
│   │       └── Sidebar.jsx        # Chat session list panel
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## 📡 API Reference

### `GET /health`

Health check endpoint. Use this to verify the backend is running.

**Response:**
```json
{ "status": "ok" }
```

---

### `POST /chat`

Processes a user question through the full RAG pipeline.

**Headers:**

| Header | Type | Required | Description |
|---|---|---|---|
| `Content-Type` | string | ✅ | Must be `text/plain` |
| `session-id` | string | ✅ | Unique chat session ID (e.g. `chat_1234567890`) |

**Body:**

Raw text string — the user's question. No JSON wrapping.

```
What are GitLab's core values?
```

**Success Response `200`:**

```json
{
  "answer": "GitLab's core values are summarised by the acronym CREDIT...",
  "sources": [
    {
      "title": "Values",
      "url": "https://handbook.gitlab.com/handbook/values/"
    }
  ],
  "preview": [
    "GitLab has six core values: Collaboration, Results, Efficiency..."
  ],
  "suggested_questions": [
    "How does GitLab measure results?",
    "What does psychological safety mean at GitLab?",
    "How do GitLab values apply to remote work?"
  ]
}
```

**Error Responses:**

| Status | Cause |
|---|---|
| `400` | Missing or empty `session-id` header, or empty question body |
| `500` | Internal error during retrieval, LLM generation, or response building |

---

## ⚙️ Configuration

All parameters are in `backend/config.json`. No code changes needed for basic tuning.

```jsonc
{
  "server": {
    "host": "0.0.0.0",
    "port": 7860
  },
  "embeddings": {
    "model": "all-MiniLM-L6-v2",   // Change to swap embedding model
    "device": "cpu"                  // Use "cuda" if you have a GPU
  },
  "vector_db": {
    "collection_name": "docs",
    "distance_metric": "cosine",
    "embedding_dimension": 384       // Must match the embedding model
  },
  "retrieval": {
    "top_k": 5                       // Chunks retrieved per query
  },
  "llm": {
    "model": "llama3:8b",            // Change to any pulled Ollama model
    "base_url": "http://localhost:11434",
    "temperature": 0.2               // Lower = more deterministic answers
  },
  "rag": {
    "max_context_chunks": 5,
    "enable_guardrails": true,
    "enable_citations": true,
    "enable_page_preview": true,
    "enable_suggested_questions": true
  }
}
```

**Swapping the LLM model:**

```bash
# Pull a different model
ollama pull mistral          # Faster, good quality
ollama pull llama3:70b       # Best quality, needs ~40 GB RAM
ollama pull phi3             # Very fast, smaller context window
```

Then update `llm.model` in `config.json` and restart the backend.

---

## 🔧 Troubleshooting

### Quick health checks

Run these in order before digging deeper:

```bash
# 1. Is Ollama running?
curl http://localhost:11434
# Expected: "Ollama is running"

# 2. Is the backend running?
curl http://localhost:7860/health
# Expected: {"status":"ok"}

# 3. Does a full chat request work?
curl -X POST http://localhost:7860/chat \
  -H "Content-Type: text/plain" \
  -H "session-id: test-001" \
  -d "What are GitLab company values?"
# Expected: JSON with answer, sources, preview, suggested_questions
```

### Inspect the vector database

```bash
cd backend
source venv/bin/activate
python inspect_chroma.py
```

This prints the first 10 records from Chroma. If you see 0 records, ingestion has not completed yet.

---

### Common errors

<details>
<summary><strong>ValueError: CHROMA_API_KEY environment variable not set</strong></summary>

The `.env` file is missing or not in the `backend/` directory.

**Fix:** Create `backend/.env` with all three Chroma variables. Always run `python main.py` from _inside_ the `backend/` directory.

</details>

<details>
<summary><strong>Connection refused on port 11434</strong></summary>

Ollama is not running.

**Fix:** Open a new terminal and run `ollama serve`. Keep that terminal open throughout your session.

</details>

<details>
<summary><strong>RuntimeError: LLM generation failed — model not found</strong></summary>

The Llama3 model has not been downloaded yet.

**Fix:** Run `ollama pull llama3:8b` and wait for the download to complete (~4.7 GB).

</details>

<details>
<summary><strong>ReadTimeout when calling Ollama</strong></summary>

Inference is taking longer than the 120-second timeout (common on slow CPUs).

**Fix:** In `services/llm_service.py`, increase `timeout=120` to `timeout=300`. Or switch to a faster model like `phi3` in `config.json`.

</details>

<details>
<summary><strong>ModuleNotFoundError: No module named 'aiohttp'</strong></summary>

The virtual environment is not activated, or dependencies were not installed.

**Fix:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

</details>

<details>
<summary><strong>FileNotFoundError: config.json not found</strong></summary>

The server was launched from the wrong directory.

**Fix:** Always run `python main.py` from _inside_ the `backend/` directory, not from the repo root.

</details>

<details>
<summary><strong>Empty answers — "I couldn't find relevant information"</strong></summary>

The Chroma collection is empty or the query returned no results above the similarity threshold.

**Fix:** Run `python inspect_chroma.py` to check the collection. If count is 0, let the server run ingestion on next startup.

</details>

<details>
<summary><strong>CORS error in browser console</strong></summary>

The backend is not running, or it crashed on startup.

**Fix:** Check that the backend terminal shows `Uvicorn running on http://0.0.0.0:7860`. CORS is already configured for all origins in `main.py`.

</details>

### Re-running ingestion

If you need to re-crawl GitLab docs (e.g., after a major handbook update), delete the collection first:

```python
# Run from inside backend/ with venv active
from dotenv import load_dotenv
load_dotenv()
from database.chroma_client import ChromaClient
import chromadb, os

client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE")
)
client.delete_collection("docs")
print("Collection deleted — restart the server to re-ingest")
```

Then restart the backend. It will auto-trigger the crawler.

---

## 🤝 Contributing

Contributions are welcome! Here is how to get started:

1. **Fork** the repository and clone your fork
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes, following the existing code structure
4. Test your changes end to end using the curl health checks above
5. Commit with a clear message:
   ```bash
   git commit -m "feat: add streaming responses to /chat endpoint"
   ```
6. Push to your fork and open a **Pull Request**

### Commit message conventions

| Prefix | Use for |
|---|---|
| `feat:` | New features |
| `fix:` | Bug fixes |
| `docs:` | Documentation changes |
| `refactor:` | Code restructuring without behaviour change |
| `chore:` | Dependency updates, config changes |

### Ideas for contributions

- [ ] Replace in-memory `ChatMemory` with Redis for persistent sessions
- [ ] Add `/ingest` API endpoint to trigger re-crawling without clearing the DB
- [ ] Implement streaming responses (SSE) to reduce perceived latency
- [ ] Wire up the existing `QueryRewriter` class to improve ambiguous queries
- [ ] Add Docker Compose for one-command startup
- [ ] Add topic-specific metadata detection in `build_metadata()`
- [ ] Implement incremental crawling (only re-crawl changed pages)

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built for the GitLab GenAI Chatbot Project · Powered by [Ollama](https://ollama.ai) · [Chroma](https://trychroma.com) · [FastAPI](https://fastapi.tiangolo.com)

</div>
