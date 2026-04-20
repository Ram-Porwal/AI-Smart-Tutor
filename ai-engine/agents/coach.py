from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from core.state import TutorState

# ---------------------------------------------------------
# 1. Configure the LLM
# ---------------------------------------------------------
# We use a slightly higher temperature (0.7) for the Coach to allow for 
# more conversational warmth, varied vocabulary, and natural empathy.
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# ---------------------------------------------------------
# 2. The LangGraph Node Function
# ---------------------------------------------------------
def coach_node(state: TutorState):
    """
    Acts as the 'Persona Wrapper'. Reads the system state (fatigue, options, verdicts) 
    and translates them into empathetic, user-facing dialogue.
    """
    print("--- [AGENT ACTIVE] Coach ---")
    
    # Extract Context from the Shared State
    gaps = state.get("knowledge_gaps", [])
    safety_valve = state.get("safety_valve", "GREEN")
    options = state.get("curated_options", [])
    verdict = state.get("referee_verdict", None)
    budget_exhausted = state.get("budget_exhausted", False)
    
    # ---------------------------------------------------------
    # 3. Dynamic Prompt Construction (The "Translation" Logic)
    # ---------------------------------------------------------
    system_instruction = (
        "You are the Coach Agent, the supportive, user-facing peer mentor of an AI Smart Tutor. "
        "Your job is to translate the system's technical state into natural, encouraging dialogue. "
        "Never break character. Never reveal you are receiving system JSON. "
        "Keep your responses concise, punchy, and highly conversational.\n\n"
    )
    
    # Scenario A: Graceful Degradation (Budget Limit)
    if budget_exhausted:
        system_instruction += (
            "URGENT SYSTEM STATE: Session limits reached. Pivot to 'Review Mode'. "
            "Acknowledge their hard work today, and explain we are switching to reviewing past "
            "concepts instead of generating new challenges. Make it sound like a strategic cool-down."
        )
    # Scenario B: Biological Safety Valve (Fatigue)
    elif safety_valve == "RED":
        system_instruction += (
            f"URGENT SYSTEM STATE: User fatigue is high. You MUST force a micro-break. "
            f"Present these options to the user clearly but gently: {options}. "
            "Do NOT ask them a technical question. Tell them their brain needs a timeout."
        )
    # Scenario C: Path Planner Hand-off (Curated Menu)
    elif options:
        system_instruction += (
            f"SYSTEM STATE: The Path Planner has generated curriculum options: {options}. "
            "Present these choices to the user and ask which path they want to tackle next. "
            "Frame it as handing them the steering wheel."
        )
    # Scenario D: Referee Verdict (Game/Challenge Feedback)
    elif verdict:
        system_instruction += (
            f"SYSTEM STATE: The Referee just evaluated their work. Verdict: '{verdict}'. "
            "Use the 'Sandwich Method' to deliver this feedback: 1. Praise a specific effort -> "
            "2. Translate the verdict into a gentle hint -> 3. Encourage them to try again."
        )
    # Scenario E: LAA Ambiguity (Clarification Needed)
    elif "Needs Clarification" in gaps:
        system_instruction += (
            "SYSTEM STATE: The Analytics agent couldn't understand the user's intent. "
            "Ask a clarifying question to figure out exactly what they need help with. "
            "Do it without sounding like an error message."
        )
    else:
        system_instruction += "SYSTEM STATE: General encouragement and conversational continuity. Ask if they are ready to proceed."

    # ---------------------------------------------------------
    # 4. Invoke the LLM
    # ---------------------------------------------------------
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        # Inject the entire conversation history so the Coach has context
        MessagesPlaceholder(variable_name="messages")
    ])
    
    chain = prompt | llm
    response: AIMessage = chain.invoke({"messages": state["messages"]})
    
    # ---------------------------------------------------------
    # 5. Return the State Update
    # ---------------------------------------------------------
    # By returning "end_session" as the next_action, the Master Router knows 
    # to pass the baton to the END node, effectively pausing the graph 
    # to wait for the human user's reply in the React UI.
    return {
        "active_agent": "coach",
        "messages": [response],
        "next_action": "end_session" 
    }