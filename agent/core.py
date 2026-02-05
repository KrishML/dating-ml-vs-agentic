"""
Pure Python agent loop for dating swipe decision-making.

This is the source of truth for agentic behavior:
- State is explicit (dataclass)
- Unknowns are tracked as facts to resolve
- Planner chooses next action, not the final decision
- Actions reduce uncertainty and update state
- Decision happens only when justified by reduced unknowns
- Safety rules override all other considerations
"""

from dataclasses import dataclass, field
from typing import Literal, Optional
from enum import Enum


class Decision(str, Enum):
    """Final decision states."""
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UNDECIDED = "UNDECIDED"


@dataclass
class Profile:
    """A dating profile to evaluate."""
    id: str
    name: str
    age: int
    bio: str
    photos: list[str]  # list of photo URLs or descriptions
    interests: list[str]
    location: str


@dataclass
class AgentState:
    """Explicit agent state for swipe decision.
    
    This is the SINGLE SOURCE OF TRUTH for what the agent knows.
    """
    profile: Profile
    
    # Unknowns: unresolved decision-relevant facts
    unknowns: list[str] = field(default_factory=list)
    
    # Observations gathered
    bio_analysis: Optional[dict] = None  # e.g., {"values": [...], "red_flags": [...]}
    photo_analysis: Optional[dict] = None  # e.g., {"quality": "...", "authenticity": "..."}
    safety_flags: list[str] = field(default_factory=list)  # Violations of constraints
    
    # Action history (for reflection)
    actions_taken: list[str] = field(default_factory=list)
    
    # Final decision
    decision: Decision = Decision.UNDECIDED
    decision_rationale: str = ""


class SafetyConstraint:
    """Safety rules that override all other considerations.
    
    These are first-class and must be checked before any decision.
    """
    
    CONSTRAINTS = {
        "no_minors": "Profile must be 18+",
        "no_catfish_indicators": "Photos must show consistent identity",
        "no_explicit_harm_intent": "Bio/photos must not indicate harm",
    }
    
    @staticmethod
    def check(state: AgentState) -> list[str]:
        """Check all safety constraints. Returns list of violations."""
        violations = []
        
        # Safety 1: Age constraint
        if state.profile.age < 18:
            violations.append("no_minors")
        
        # Safety 2: Catfish detection (if photos are analyzed)
        if state.photo_analysis:
            if state.photo_analysis.get("authenticity") == "low":
                violations.append("no_catfish_indicators")
        
        # Safety 3: Explicit harm (simple keyword check for demo)
        harm_keywords = ["kill", "hurt", "abuse", "harassment"]
        bio_lower = state.profile.bio.lower()
        if any(keyword in bio_lower for keyword in harm_keywords):
            violations.append("no_explicit_harm_intent")
        
        return violations


class Planner:
    """LLM-based planner (or rule-based in this demo).
    
    Role: Choose the NEXT ACTION to reduce uncertainty.
    NOT to decide LEFT or RIGHT directly.
    """
    
    @staticmethod
    def choose_action(state: AgentState) -> Optional[str]:
        """
        Given current state, what action reduces uncertainty most?
        
        Returns: action name, or None if ready to decide.
        """
        # If we have unresolved unknowns, plan an action
        if state.unknowns:
            unknown = state.unknowns[0]  # Simple priority: take first unknown
            
            if "photo" in unknown.lower():
                return "analyze_photos"
            elif "bio" in unknown.lower() or "values" in unknown.lower():
                return "analyze_bio"
            elif "red_flag" in unknown.lower():
                return "check_red_flags"
            else:
                return "analyze_bio"  # default
        
        # No unknowns remain: ready to decide
        return None


class Actions:
    """Investigative actions that reduce uncertainty."""
    
    @staticmethod
    def analyze_photos(state: AgentState) -> AgentState:
        """
        Investigate: Do photos match profile authenticity standards?
        
        In production, this would call a vision model or ML classifier.
        For demo, we simulate based on simple heuristics.
        """
        # Simulate photo analysis
        state.photo_analysis = {
            "authenticity": "high" if len(state.profile.photos) >= 2 else "low",
            "quality": "good" if len(state.profile.photos) > 0 else "poor",
            "diversity": "varied" if len(state.profile.photos) >= 3 else "limited",
        }
        
        state.actions_taken.append("analyze_photos")
        
        # Remove this unknown if it was tracked
        state.unknowns = [u for u in state.unknowns if "photo" not in u.lower()]
        
        return state
    
    @staticmethod
    def analyze_bio(state: AgentState) -> AgentState:
        """
        Investigate: What values, interests, and red flags appear in bio?
        
        In production, this would call an LLM to extract semantic meaning.
        For demo, we do simple keyword extraction.
        """
        bio_lower = state.profile.bio.lower()
        
        # Extract values (simple keyword matching)
        value_keywords = {
            "honest": ["honest", "authentic", "genuine"],
            "ambitious": ["goal", "career", "passion", "startup"],
            "adventurous": ["travel", "hiking", "adventure", "explore"],
            "family_oriented": ["family", "kids", "home", "tradition"],
        }
        
        detected_values = []
        for value, keywords in value_keywords.items():
            if any(kw in bio_lower for kw in keywords):
                detected_values.append(value)
        
        # Extract red flags (simple heuristic)
        red_flag_keywords = ["ex", "drama", "toxic", "angry", "control"]
        detected_flags = [kw for kw in red_flag_keywords if kw in bio_lower]
        
        state.bio_analysis = {
            "values": detected_values,
            "red_flags": detected_flags,
            "length": len(state.profile.bio),
        }
        
        state.actions_taken.append("analyze_bio")
        state.unknowns = [u for u in state.unknowns if "bio" not in u.lower() and "values" not in u.lower()]
        
        return state
    
    @staticmethod
    def check_red_flags(state: AgentState) -> AgentState:
        """
        Investigate: Are there behavioral or content red flags?
        
        Safety-adjacent but separate from hard constraints.
        These inform the decision but don't block it.
        """
        red_flags = []
        
        # Check for concerning patterns
        if state.bio_analysis:
            if state.bio_analysis.get("red_flags"):
                red_flags.extend(state.bio_analysis["red_flags"])
        
        # Age gap concerns (demo heuristic)
        age_now = 30  # Assume user is 30
        if abs(state.profile.age - age_now) > 10:
            red_flags.append("significant_age_gap")
        
        state.safety_flags = red_flags
        state.actions_taken.append("check_red_flags")
        state.unknowns = [u for u in state.unknowns if "red_flag" not in u.lower()]
        
        return state


class Decision_Maker:
    """Terminal decision logic: LEFT or RIGHT.
    
    This happens ONLY when:
    1. All safety constraints pass
    2. All critical unknowns are resolved
    3. Sufficient evidence supports the choice
    """
    
    @staticmethod
    def decide(state: AgentState) -> AgentState:
        """
        Make a terminal decision given current state.
        
        Returns updated state with decision and rationale.
        Raises ValueError if decision is premature.
        """
        # HARD CONSTRAINT: Check safety first
        violations = SafetyConstraint.check(state)
        if violations:
            state.decision = Decision.LEFT
            state.decision_rationale = f"Safety violation(s): {', '.join(violations)}"
            return state
        
        # Check if unknowns remain
        if state.unknowns:
            raise ValueError(
                f"Cannot decide while unknowns remain: {state.unknowns}. "
                f"Continue with planning loop first."
            )
        
        # Score-based decision (simple heuristic)
        score = 0
        
        # Values alignment (+ 2 for each detected value)
        if state.bio_analysis and state.bio_analysis.get("values"):
            score += len(state.bio_analysis["values"]) * 2
        
        # Red flags penalty (- 3 each)
        if state.safety_flags:
            score -= len(state.safety_flags) * 3
        
        # Age proximity bonus (+ 1 for each year closer to 30)
        age_gap = abs(state.profile.age - 30)
        score += max(0, 10 - age_gap)
        
        # Photo quality bonus
        if state.photo_analysis:
            if state.photo_analysis.get("quality") == "good":
                score += 2
            if state.photo_analysis.get("authenticity") == "high":
                score += 2
        
        # Decide: threshold at 5
        if score >= 5:
            state.decision = Decision.RIGHT
            state.decision_rationale = f"Positive match (score: {score})"
        else:
            state.decision = Decision.LEFT
            state.decision_rationale = f"Low compatibility (score: {score})"
        
        return state


class AgentLoop:
    """Main agent loop orchestration.
    
    Explicit control flow:
    1. Initialize state with unknowns
    2. While unknowns remain:
       a. Planner chooses action
       b. Action reduces uncertainty
    3. Safety check
    4. Decide LEFT or RIGHT
    5. Reflect (store learning)
    """
    
    @staticmethod
    def run(profile: Profile, max_iterations: int = 10) -> AgentState:
        """
        Run the full agent loop until decision.
        
        Args:
            profile: The profile to evaluate
            max_iterations: Safety limit to prevent infinite loops
        
        Returns:
            Final AgentState with decision
        
        Raises:
            ValueError: If max iterations exceeded (logic error)
        """
        # Initialize state with unknowns
        state = AgentState(
            profile=profile,
            unknowns=[
                "Understand bio values and red flags",
                "Verify photo authenticity",
                "Check for behavioral red flags",
            ]
        )
        
        # Planning loop: reduce uncertainty
        iterations = 0
        while state.unknowns and iterations < max_iterations:
            iterations += 1
            
            # Planner chooses next action
            action = Planner.choose_action(state)
            if action is None:
                break  # No more actions needed
            
            # Execute action
            if action == "analyze_photos":
                state = Actions.analyze_photos(state)
            elif action == "analyze_bio":
                state = Actions.analyze_bio(state)
            elif action == "check_red_flags":
                state = Actions.check_red_flags(state)
        
        if iterations >= max_iterations:
            raise ValueError(
                f"Agent loop exceeded max iterations ({max_iterations}). "
                f"Possible infinite loop or logic error."
            )
        
        # Terminal decision
        state = Decision_Maker.decide(state)
        
        # Reflection: store learning
        state = Reflection.reflect(state)
        
        return state


class Reflection:
    """Post-decision reflection: extract learnings for future decisions.
    
    Not used in this simple demo, but essential for real agents.
    """
    
    @staticmethod
    def reflect(state: AgentState) -> AgentState:
        """
        After decision, extract patterns for improvement.
        
        In a full system, this would write to vector memory
        or update model weights.
        """
        # For now, just a placeholder
        # In production: "I decided LEFT because X; next time check Y earlier"
        return state
