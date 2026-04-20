# AI Smart Tutor: Agentic Learning Platform 🚀

A professional, multi-agent educational platform built to provide personalized tutoring through autonomous AI workflows. This project demonstrates a full-stack implementation of **LangGraph**, **FastAPI**, and **WebSockets** to create a seamless, real-time learning experience.

## 🏗️ System Architecture
The platform is built on a three-tier "Cyber-Minimalist" architecture:

1.  **Frontend (React):** A responsive UI featuring a "Persona-Shift" chat interface and real-time agent status tracking.
2.  **Gateway (Node.js/Socket.io):** A high-performance broker that manages WebSocket connections and streams data between the UI and the AI Engine.
3.  **AI Engine (Python/LangGraph):** The core intelligence layer using an agentic state machine to coordinate between specialized nodes:
    * **Learner Analytics:** Analyzes user input and tracks knowledge gaps.
    * **Coach:** Generates empathetic, technically deep responses using Llama 3.3.
    * **Persistence Layer:** Uses SQLite to maintain conversation state across sessions.

## 🛠️ Tech Stack
* **LLM:** Llama 3.3-70b (via Groq LPU)
* **Orchestration:** LangGraph & LangChain
* **Backend:** FastAPI (Python) & Node.js (Express)
* **Frontend:** React.js & Tailwind CSS
* **Database:** SQLite (Checkpointer)

## 🚀 Getting Started

### Prerequisites
* Node.js (v18+)
* Python 3.10+
* Groq API Key

### Installation & Setup
To run the full stack, you must launch three separate terminals:

#### 1. AI Engine (Terminal 1)
```bash
cd ai-engine
.\venv\Scripts\activate
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