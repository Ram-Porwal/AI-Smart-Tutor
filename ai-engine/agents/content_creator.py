from typing import Any, Dict, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from core.state import TutorState

# ---------------------------------------------------------
# 1. Define the Structured Game Schema (For React)
# ---------------------------------------------------------
class GameData(BaseModel):
    """Schema for the React GameCanvas component."""
    game_type: Literal["LogicPuzzle", "CodeDebugger", "ConceptMatch"] = Field(
        description="Dictates which React component will render the game."
    )
    instructions: str = Field(
        description="The user-facing prompt (e.g., 'Find the infinite loop in this snippet')."
    )
    game_logic: Dict[str, Any] = Field(
        description="The core data: initial variables, snippets, and the hidden 'answer key' for the Referee."
    )

# ---------------------------------------------------------
# 2. Define the External Tools (RAG / Search)
# ---------------------------------------------------------
@tool
def fetch_tech_trivia(topic: str) -> str:
    """
    Use this tool to search Tavily or Exa for recent technology news, 
    fun facts, or historical context to provide a mental break.
    """
    # In a production environment, you would instantiate your TavilyClient here.
    # e.g., return tavily_client.search(topic, search_depth="advanced")
    return f"[Simulated Search Result] Recent data indicates a massive shift in how {topic} is handled in modern architectures..."

# ---------------------------------------------------------
# 3. Configure the LLM
# ---------------------------------------------------------
# We use a high-creativity model here since it's writing games and synthesizing news.
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# ---------------------------------------------------------
# 4. The LangGraph Node Function
# ---------------------------------------------------------
def content_creator_node(state: TutorState):
    """
    The Engine of Engagement. Acts in two modes:
    1. Interactive Mode: Generates JSON schemas for React games.
    2. Rest Mode: Uses external search tools to generate trivia micro-breaks.
    """
    print("--- [AGENT ACTIVE] Content Creator ---")
    
    # We assume the frontend passed back a 'selected_path_id' after the Coach's menu
    selected_path = state.get("selected_path_id", "default_challenge")
    knowledge_gaps = state.get("knowledge_gaps", ["Core Computer Science Fundamentals"])
    topic = knowledge_gaps[0]
    
    # ---------------------------------------------------------
    # MODE A: The Micro-Break (Tool Calling)
    # ---------------------------------------------------------
    if "micro_break" in selected_path or "trivia" in selected_path:
        print(f"--- [MODE] Generating RAG Micro-Break for: {topic} ---")
        
        llm_with_tools = llm.bind_tools([fetch_tech_trivia])
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Tech Scout. Use your search tool to find a quick, fascinating piece of real-world trivia about {topic}. Keep it to 2 engaging sentences. Your goal is to give the user a mental break."),
            ("user", "Fetch a break for me.")
        ])
        
        chain = prompt | llm_with_tools
        
        # The LLM decides to call the tool, executes it, and synthesizes the final message.
        # (In a complex LangGraph, you'd route to a dedicated ToolNode here, 
        # but LangChain abstracts simple tool execution nicely if configured).
        response = chain.invoke({"topic": topic})
        
        return {
            "active_agent": "content_creator",
            "messages": [response],
            "next_action": "deliver_feedback" # Pass back to Coach to deliver the fun fact
        }
        
    # ---------------------------------------------------------
    # MODE B: The Interactive Game (Structured Output)
    # ---------------------------------------------------------
    else:
        print(f"--- [MODE] Generating Interactive JSON Game for: {topic} ---")
        
        structured_llm = llm.with_structured_output(GameData)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the Lead Game Designer. Create a challenging, interactive puzzle to test the user's understanding of {topic}. Ensure the 'game_logic' dictionary contains a clear, verifiable answer key."),
            ("user", "Generate the game payload.")
        ])
        
        chain = prompt | structured_llm
        game_data: GameData = chain.invoke({"topic": topic})
        
        # Package the state exactly how the React UI and Referee expect it
        game_state = {
            "game_type": game_data.game_type,
            "instructions": game_data.instructions,
            "game_logic": game_data.game_logic,
            "current_progress": {}, # Empty object for the React UI to update dynamically
            "is_completed": False
        }
        
        return {
            "active_agent": "content_creator",
            "game_state": game_state,
            "next_action": "deliver_feedback" # The Coach will say: "I've set up a sandbox for you..."
        }