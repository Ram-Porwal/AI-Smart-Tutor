# AI Smart Tutor: Agentic Learning Platform 🚀

A professional, multi-agent educational platform built to provide personalized tutoring through autonomous AI workflows. This project demonstrates a full-stack implementation of **LangGraph**, **FastAPI**, and **WebSockets**.

## 🏗️ System Architecture
The platform is built on a three-tier "Cyber-Minimalist" architecture:
1.  **Frontend (React):** Responsive UI with real-time agent status tracking.
2.  **Gateway (Node.js/Socket.io):** Broker managing WebSocket streams between UI and AI Engine.
3.  **AI Engine (Python/LangGraph):** Agentic state machine coordinating between specialized nodes (Analytics, Coach, Referee).

## 🛠️ Tech Stack
* **LLM:** Llama 3.3-70b (via Groq LPU)
* **Orchestration:** LangGraph & LangChain
* **Backend:** FastAPI (Python) & Node.js (Express)
* **Frontend:** React.js & Tailwind CSS
* **Database:** SQLite (Checkpointer for persistence)

## 🔑 Environment Setup
Before running the application, you must configure your API credentials.

1.  **Get a Groq API Key:** Visit the [Groq Console](https://console.groq.com/keys) and generate a key starting with `gsk_`.
2.  **Create an Environment File:** Inside the `ai-engine/` directory, create a file named `.env`.
####3.  **Add Your Key:** Paste your key into the file exactly as shown:
    ```text
    GROQ_API_KEY=gsk_your_actual_key_here
    ```
    *Note: Do not use quotes or spaces around the key.*

## 🚀 Getting Started

### Installation
Launch three separate terminals to run the full stack:

#### 1. AI Engine (Terminal 1)
```bash
cd AI-Smart-Tutor
cd ai-engine
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 2. API Gateway (Terminal 2)
```bash
cd gateway
npm install
node src/server.js
```

#### 3. Frontend UI (Terminal 3)
```bash
cd frontend
npm install
npm start
```