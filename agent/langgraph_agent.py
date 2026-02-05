"""
LangGraph implementation of the dating agent.

This is a FORMALIZATION of the core.py agent loop, not a redesign.
- Same state structure
- Same action sequence
- Same safety constraints
- LangGraph makes the loop explicit and visualizable

Requires: pip install langgraph langchain
"""

from typing import Optional, Literal
from core import (
    Profile,
    AgentState,
    Decision,
    SafetyConstraint,
)
from planner import Planner, Action
from actions import BioAnalyzer, PhotoAnalyzer, RedFlagDetector
from reflection import ReflectionEngine

try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.state import CompiledGraph
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: LangGraph not installed. Use: pip install langgraph")


def create_agent_graph() -> Optional["CompiledGraph"]:
    """
    Build the LangGraph state machine for the dating agent.
    
    Nodes:
    - plan: Planner chooses next action
    - analyze_bio: Action to understand values
    - analyze_photos: Action to verify authenticity
    - check_red_flags: Action to detect behavioral red flags
    - decide: Terminal decision (LEFT or RIGHT)
    
    Edges form a loop: plan -> action -> plan -> ... -> decide
    """
    if not LANGGRAPH_AVAILABLE:
        return None
    
    workflow = StateGraph(AgentState)
    
    # === NODES ===
    
    def node_plan(state: AgentState) -> AgentState:
        """Planner node: choose next action."""
        action = Planner.choose_action(state)
        
        # Also used as signal to exit loop
        state._next_action = action
        return state
    
    def node_analyze_bio(state: AgentState) -> AgentState:
        """Action node: analyze profile bio."""
        analysis = BioAnalyzer.analyze(state.profile.bio)
        state.bio_analysis = analysis
        state.actions_taken.append("analyze_bio")
        
        # Remove from unknowns
        state.unknowns = [u for u in state.unknowns if "bio" not in u.lower()]
        
        return state
    
    def node_analyze_photos(state: AgentState) -> AgentState:
        """Action node: analyze photos."""
        analysis = PhotoAnalyzer.analyze(state.profile.photos)
        state.photo_analysis = analysis
        state.actions_taken.append("analyze_photos")
        
        # Remove from unknowns
        state.unknowns = [u for u in state.unknowns if "photo" not in u.lower()]
        
        return state
    
    def node_check_red_flags(state: AgentState) -> AgentState:
        """Action node: check for red flags."""
        flags = RedFlagDetector.check(state.profile)
        state.safety_flags = flags
        state.actions_taken.append("check_red_flags")
        
        # Remove from unknowns
        state.unknowns = [u for u in state.unknowns if "red" not in u.lower()]
        
        return state
    
    def node_decide(state: AgentState) -> AgentState:
        """Terminal decision node."""
        # Check safety constraints
        violations = SafetyConstraint.check(state)
        if violations:
            state.decision = Decision.LEFT
            state.decision_rationale = f"Safety violation(s): {', '.join(violations)}"
            return state
        
        # Simple scoring (same as core.py)
        score = 0
        
        if state.bio_analysis and state.bio_analysis.get("values"):
            score += len(state.bio_analysis["values"]) * 2
        
        if state.safety_flags:
            score -= len(state.safety_flags) * 3
        
        age_gap = abs(state.profile.age - 30)
        score += max(0, 10 - age_gap)
        
        if state.photo_analysis:
            if state.photo_analysis.get("quality") == "good":
                score += 2
            if state.photo_analysis.get("authenticity") == "high":
                score += 2
        
        # Decide
        if score >= 5:
            state.decision = Decision.RIGHT
            state.decision_rationale = f"Positive match (score: {score})"
        else:
            state.decision = Decision.LEFT
            state.decision_rationale = f"Low compatibility (score: {score})"
        
        return state
    
    # Add nodes
    workflow.add_node("plan", node_plan)
    workflow.add_node("analyze_bio", node_analyze_bio)
    workflow.add_node("analyze_photos", node_analyze_photos)
    workflow.add_node("check_red_flags", node_check_red_flags)
    workflow.add_node("decide", node_decide)
    
    # === EDGES ===
    
    # Conditional edge from plan: routes to action or decision
    def route_after_plan(state: AgentState) -> str:
        """Decide what to do next after planning."""
        action = getattr(state, "_next_action", None)
        
        if action == "analyze_bio":
            return "analyze_bio"
        elif action == "analyze_photos":
            return "analyze_photos"
        elif action == "check_red_flags":
            return "check_red_flags"
        else:
            return "decide"
    
    # All actions loop back to plan
    workflow.add_conditional_edges("plan", route_after_plan)
    workflow.add_edge("analyze_bio", "plan")
    workflow.add_edge("analyze_photos", "plan")
    workflow.add_edge("check_red_flags", "plan")
    workflow.add_edge("decide", END)
    
    # Start point
    workflow.set_entry_point("plan")
    
    # Compile
    return workflow.compile()


def run_langgraph_agent(profile: Profile) -> AgentState:
    """
    Run the LangGraph agent.
    
    Args:
        profile: Profile to evaluate
    
    Returns:
        Final AgentState with decision
    """
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("LangGraph not installed. Use: pip install langgraph")
    
    graph = create_agent_graph()
    if graph is None:
        raise ImportError("Failed to create LangGraph")
    
    # Initialize state
    state = AgentState(
        profile=profile,
        unknowns=[
            "Understand bio values and red flags",
            "Verify photo authenticity",
            "Check for behavioral red flags",
        ]
    )
    
    # Run
    final_state = graph.invoke({"profile": profile, "unknowns": state.unknowns})
    
    return final_state


if __name__ == "__main__":
    # Demo
    from core import Profile
    
    test_profile = Profile(
        id="p123",
        name="Alice",
        age=28,
        bio="Love hiking and trying new restaurants. Ambitious in my career.",
        photos=["photo1.jpg", "photo2.jpg", "photo3.jpg"],
        interests=["outdoors", "cooking", "travel"],
        location="San Francisco",
    )
    
    print("Running LangGraph agent...")
    try:
        result = run_langgraph_agent(test_profile)
        print(f"Decision: {result.decision}")
        print(f"Rationale: {result.decision_rationale}")
    except ImportError as e:
        print(f"Cannot run demo: {e}")
