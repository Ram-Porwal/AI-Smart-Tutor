from typing import TypedDict, List, Annotated, Optional, Any
import operator
from langchain_core.messages import BaseMessage

class TutorState(TypedDict):
    # LangGraph standard: appends new messages rather than overwriting
    messages: Annotated[List[BaseMessage], operator.add]
    
    # 1. Routing & Persona Identity
    active_agent: str           # Tracks who holds the baton (e.g., "coach", "path_planner")
    next_action: str            # The routing instruction for the conditional edges
    
    # 2. Pedagogical Context
    knowledge_level: str        # e.g., "Beginner", "Intermediate"
    knowledge_gaps: List[str]   # Identified areas of struggle (e.g., ["Recursion Base Cases"])
    
    # 3. Game & Verification Logic
    game_state: Optional[dict[str, Any]]  # Holds the dynamic JSON for React (rules, progress)
    referee_verdict: Optional[str]        # E.g., "PASS", "FAIL", "CONCEPTUAL_BLOCK"
    
    # 4. Biological Safety Valve & Guardrails
    session_duration_mins: int
    fatigue_score: float        # Calculated based on time, errors, and latency
    safety_valve: str           # "GREEN", "YELLOW" (Warning), "RED" (Micro-Break Forced)
    
    # 5. Financial/System Status
    budget_exhausted: bool      # Triggers Graceful Degradation / Review Mode
    
    curated_options: Optional[List[dict]]  # Holds the Path Planner's menu for the UI
    
    selected_path_id: str