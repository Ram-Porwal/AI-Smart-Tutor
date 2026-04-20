from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from core.state import TutorState

# ---------------------------------------------------------
# 1. Define the Structured Output Schema
# ---------------------------------------------------------
class AnalyticsOutput(BaseModel):
    """Schema for the Learner Analytics Agent's diagnostic output."""
    knowledge_level: Literal["Beginner", "Intermediate", "Advanced", "Unknown"] = Field(
        description="Assess the user's current understanding of the topic."
    )
    knowledge_gaps: List[str] = Field(
        description="A list of 1-3 specific conceptual gaps identified in the user's input. Leave empty if none.",
        default_factory=list
    )
    is_ambiguous: bool = Field(
        description="True if the user's input is too vague to diagnose (e.g., 'I don't get it' or 'Help')."
    )

# ---------------------------------------------------------
# 2. Configure the LLM and Prompt
# ---------------------------------------------------------
# Using a fast, high-reasoning model for routing and extraction
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm = llm.with_structured_output(AnalyticsOutput)

system_prompt = """You are the Learner Analytics Agent (LAA), the diagnostic core of an AI Smart Tutor.
Your ONLY job is to analyze the user's latest input in the context of the conversation history.

Do NOT attempt to teach, explain, or answer the user's question. 
Do NOT output conversational text.

Your goals:
1. Identify if the user's statement contains a specific knowledge gap (e.g., "Misunderstands array indexing").
2. Determine their approximate knowledge level based on their vocabulary and logic.
3. Flag 'is_ambiguous = True' if the input is too generic to diagnose (e.g., "I'm lost", "What?", "Play a game").

Be objective and precise."""

analytics_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("placeholder", "{messages}")
])

# Create the LangChain chain
analytics_chain = analytics_prompt | structured_llm

# ---------------------------------------------------------
# 3. The LangGraph Node Function
# ---------------------------------------------------------
def learner_analytics_node(state: TutorState):
    """
    Evaluates the conversation history, extracts pedagogical state,
    and decides where the baton goes next.
    """
    print("--- [AGENT ACTIVE] Learner Analytics ---")
    
    # 1. Invoke the chain to get structured data
    diagnosis: AnalyticsOutput = analytics_chain.invoke({"messages": state["messages"]})
    
    # 2. Determine the Routing Instruction (Baton Pass)
    # If the input is ambiguous or non-educational, route to the Coach for clarification
    if diagnosis.is_ambiguous:
        next_action = "deliver_feedback"
        # We append a temporary gap so the Coach knows *why* it was called
        gaps = ["Needs Clarification"] 
    # If a gap is clearly identified, route to the Path Planner
    elif len(diagnosis.knowledge_gaps) > 0:
        next_action = "plan_path"
        gaps = diagnosis.knowledge_gaps
    # Default fallback: Ask the Coach to engage
    else:
        next_action = "deliver_feedback"
        gaps = state.get("knowledge_gaps", [])

    # 3. Return the State Update
    return {
        "active_agent": "analytics",
        "knowledge_level": diagnosis.knowledge_level,
        "knowledge_gaps": gaps,
        "next_action": next_action
    }