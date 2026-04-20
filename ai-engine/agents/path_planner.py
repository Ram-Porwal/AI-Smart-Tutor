from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from core.state import TutorState

# ---------------------------------------------------------
# 1. Define the Structured Output Schemas
# ---------------------------------------------------------
class LearningPath(BaseModel):
    """Schema for a single option in the Curated Choice menu."""
    path_id: str = Field(description="Unique ID for the frontend routing, e.g., 'strategy_sandbox', 'micro_break_zen'")
    label: str = Field(description="User-facing title, e.g., 'Let me practice in a safe sandbox' or 'Take a 2-minute breather'")
    icon: str = Field(description="A single emoji representing the path for the React UI")
    target_agent: Literal["content_creator", "coach"] = Field(
        description="Which specialized agent should receive the baton if the user selects this option."
    )

class PlannerOutput(BaseModel):
    """Schema for the Path Planner's total architectural output."""
    safety_valve_status: Literal["GREEN", "YELLOW", "RED"] = Field(
        description="GREEN: Normal logic. YELLOW: Scaffolded/Easy. RED: Forced micro-break or review."
    )
    options: List[LearningPath] = Field(
        description="Exactly 2 to 3 curated learning paths for the user to choose from."
    )
    internal_rationale: str = Field(
        description="A brief sentence explaining why these options were chosen based on the user's fatigue and gaps."
    )

# ---------------------------------------------------------
# 2. Configure the LLM and Prompt
# ---------------------------------------------------------
# Using gpt-4o here because generating creative, context-aware curriculum options 
# requires higher reasoning than simple classification.
llm = ChatOpenAI(model="gpt-4o", temperature=0.4)
structured_planner = llm.with_structured_output(PlannerOutput)

system_prompt = """You are the Path Planner Agent, the 'Architect' of an AI Smart Tutor.
Your job is to generate a 'Curated Menu' of 2-3 learning paths based on the user's knowledge gaps and their current fatigue level.

Do NOT teach the concept. Your output is STRICTLY a menu of options for the user to choose from.

### The Biological Safety Valve Logic:
You will be provided with a 'Fatigue Score' (0.0 to 1.0).
- If Fatigue < 0.4 (GREEN): Offer high-engagement tasks (Deep Dives, Interactive Games, Code Debugging).
- If Fatigue >= 0.4 and < 0.8 (YELLOW): Offer low-friction tasks (Scaffolded Walkthroughs, Simple Analogies).
- If Fatigue >= 0.8 (RED): YOU MUST FORCE A REST STATE. Offer ONLY Micro-Breaks (e.g., 'Zen Pause', 'Tech Trivia') or a 'Review Mode' pivot.

### Target Agents:
- 'content_creator': Generates games, trivia, and deep instructional content.
- 'coach': Handles micro-breaks, empathy, and review mode summaries.

Make the 'label' for each path sound encouraging and human-centric."""

planner_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "Knowledge Gaps to address: {gaps}\nCurrent Fatigue Score: {fatigue}\nSession Duration: {duration} mins")
])

# Create the LangChain chain
planner_chain = planner_prompt | structured_planner

# ---------------------------------------------------------
# 3. The LangGraph Node Function
# ---------------------------------------------------------
def path_planner_node(state: TutorState):
    """
    Evaluates gaps and fatigue, generates curated options, 
    and passes the baton to the Coach to present them to the user.
    """
    print("--- [AGENT ACTIVE] Path Planner ---")
    
    # 1. Extract context (default to 0 if not yet set in the session)
    gaps = state.get("knowledge_gaps", ["General Review"])
    fatigue = state.get("fatigue_score", 0.0)
    duration = state.get("session_duration_mins", 0)
    
    # 2. Invoke the Architect's logic
    plan: PlannerOutput = planner_chain.invoke({
        "gaps": ", ".join(gaps),
        "fatigue": fatigue,
        "duration": duration
    })
    
    print(f"--- [SAFETY VALVE] Status: {plan.safety_valve_status} ---")
    print(f"--- [PLANNER RATIONALE] {plan.internal_rationale} ---")
    
    # 3. Update the state for the Coach and the UI
    # We pass the baton to the Coach so it can "announce" these choices gracefully
    return {
        "active_agent": "path_planner",
        "safety_valve": plan.safety_valve_status,
        # In a real LangGraph setup, you'd add 'curated_options' to your TutorState TypedDict
        "curated_options": [opt.model_dump() for opt in plan.options], 
        "next_action": "deliver_feedback" 
    }