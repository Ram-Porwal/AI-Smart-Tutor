import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
# CRITICAL FIX: You need to import your state definition!
from core.state import TutorState 
from database.checkpointer import get_checkpointer

# Ensure environment variables are loaded exactly where they are needed
load_dotenv(override=True)

# Initialize the Groq Brain (Llama 3.3 is a beast for this!)
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY")
)

# ---------------------------------------------------------
# 1. Agent Nodes
# ---------------------------------------------------------

def learner_analytics_node(state: TutorState):
    print("--- DEBUG: Analytics is running ---")
    return {
        "active_agent": "analytics",
        "next_action": "deliver_feedback" 
    }

# (Other stubs remain as they were...)
def path_planner_node(state: TutorState):
    return {"active_agent": "path_planner", "next_action": "generate_content"}

def content_creator_node(state: TutorState):
    return {"active_agent": "content_creator", "next_action": "verify_answer"}

def referee_node(state: TutorState):
    return {"active_agent": "referee", "next_action": "deliver_feedback"}

def coach_node(state: TutorState):
    print("--- DEBUG: Coach is generating a real AI response ---")
    
    history = state.get("messages", [])
    
    # Customizing for your identity at Ganpat University
    system_message = SystemMessage(content=(
        "You are an encouraging AI Smart Tutor Coach. "
        "Your student is Ram Porwal, a 3rd-year B.Tech student. "
        "Provide clear, concise technical explanations."
    ))

    response = llm.invoke([system_message] + history)
    
    return {
        "active_agent": "coach", 
        "next_action": "end_session",
        "messages": [response] 
    }

# ---------------------------------------------------------
# 2. The Decentralized Router
# ---------------------------------------------------------
def master_router(state: TutorState) -> str:
    action = state.get("next_action")
    
    # This helps you see the "baton pass" in the terminal
    print(f"--- DEBUG: Routing action '{action}' ---")
    
    routes = {
        "plan_path": "path_planner",
        "generate_content": "content_creator",
        "verify_answer": "referee",
        "deliver_feedback": "coach",
        "analyze_input": "learner_analytics",
        "end_session": END
    }
    
    return routes.get(action, "coach")

# ---------------------------------------------------------
# 3. Compiling the Graph
# ---------------------------------------------------------
def build_graph():
    workflow = StateGraph(TutorState)

    # Add Nodes
    workflow.add_node("learner_analytics", learner_analytics_node)
    workflow.add_node("path_planner", path_planner_node)
    workflow.add_node("content_creator", content_creator_node)
    workflow.add_node("referee", referee_node)
    workflow.add_node("coach", coach_node)

    # Add Conditional Edges (The "Brain" of the workflow)
    workflow.add_conditional_edges("learner_analytics", master_router)
    workflow.add_conditional_edges("path_planner", master_router)
    workflow.add_conditional_edges("content_creator", master_router)
    workflow.add_conditional_edges("referee", master_router)
    workflow.add_conditional_edges("coach", master_router)

    workflow.set_entry_point("learner_analytics")

    memory_saver, _ = get_checkpointer()
    app = workflow.compile(checkpointer=memory_saver)
    
    return app

tutor_app = build_graph()