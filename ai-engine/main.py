import os
import json
import asyncio
from dotenv import load_dotenv

# This must happen BEFORE importing core.graph
# Use override=True to prioritize the .env file over system variables
load_dotenv(override=True) 

# Optional Debug: Verify the key is loaded (don't share the actual key!)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ ERROR: GROQ_API_KEY not found in environment!")
else:
    print(f"✅ SUCCESS: GROQ API Key loaded (starts with {api_key[:4]}).")

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.graph import tutor_app 

app = FastAPI(title="AI_Smart_Tutor", version="1.0.0")

# 1. Enable CORS so the Node Gateway can connect without security blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    thread_id: str
    message: str

@app.post("/stream_chat")
async def stream_chat(request: ChatRequest):
    async def event_generator():
        config = {"configurable": {"thread_id": request.thread_id}}
        user_input = {"messages": [("user", request.message)]}
        last_announced_agent = None 

        try:
            # We use stream to capture node-by-node updates
            for event in tutor_app.stream(user_input, config=config):
                for node_name, state_update in event.items():
                    
                    # A. Emit Agent Handoff (The "Baton Pass")
                    if node_name != last_announced_agent:
                        yield f"{json.dumps({'type': 'agent_handoff', 'active_agent': node_name})}\n"
                        last_announced_agent = node_name
                        print(f"DEBUG: [Handoff] -> {node_name}")

                    # B. Extract Content from the Coach
                    if node_name == "coach" and "messages" in state_update:
                        latest_msg = state_update["messages"][-1]
                        
                        # --- ROBUST PARSER ---
                        # Handles both ("ai", "text") tuples and AIMessage objects
                        content = ""
                        if isinstance(latest_msg, tuple):
                            content = latest_msg[1]
                        elif hasattr(latest_msg, "content"):
                            content = latest_msg.content

                        if content:
                            print(f"DEBUG: [Streaming] Sending tokens from {node_name}...")
                            words = content.split(" ")
                            for word in words:
                                # We send JSON strings separated by newlines (NDJSON)
                                yield f"{json.dumps({'type': 'content_token', 'chunk': word + ' '})}\n"
                                await asyncio.sleep(0.03) # Artificial delay for typewriter feel
        
        except Exception as e:
            print(f"❌ GRAPH ERROR: {str(e)}")
            yield f"{json.dumps({'type': 'system_error', 'message': str(e)})}\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.get("/health")
def health_check():
    return {"status": "LangGraph Engine is online"}