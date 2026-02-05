"""
Planner module: LLM-based or rule-based action selection.

The planner's job is to choose the NEXT ACTION to reduce uncertainty.
It does NOT decide LEFT/RIGHT directly.
"""

from typing import Optional
from enum import Enum


class Action(str, Enum):
    """Available investigative actions."""
    ANALYZE_BIO = "analyze_bio"
    ANALYZE_PHOTOS = "analyze_photos"
    CHECK_RED_FLAGS = "check_red_flags"
    SEARCH_MEMORY = "search_memory"
    COMPLETE = "complete"  # No more actions needed


class Planner:
    """
    Selects the next action to reduce decision uncertainty.
    
    Strategies:
    1. Information gain: which action removes the most uncertainty?
    2. Priority: some unknowns are more decision-critical
    3. Cost: some actions are more expensive (e.g., vision model)
    """
    
    # Priority order: which unknowns are most critical?
    PRIORITY_ORDER = [
        "photo_authenticity",  # Catfish detection is hard constraint
        "bio_values",  # Understanding values is core to compatibility
        "red_flags",  # Soft constraint but high impact
    ]
    
    @staticmethod
    def get_next_action(state_dict: dict) -> Action:
        """
        Given current state, return the next action to take.
        
        Args:
            state_dict: Agent state (usually from AgentState.__dict__)
                - unknowns: list of unresolved questions
                - bio_analysis: dict or None
                - photo_analysis: dict or None
                - safety_flags: list
        
        Returns:
            Action to take next, or COMPLETE if no more actions needed
        """
        unknowns = state_dict.get("unknowns", [])
        
        if not unknowns:
            return Action.COMPLETE
        
        # Prioritize by criticality
        for priority_unknown in Planner.PRIORITY_ORDER:
            for unknown in unknowns:
                if priority_unknown in unknown.lower():
                    return Planner._action_for_unknown(unknown)
        
        # Default: take first remaining unknown
        return Planner._action_for_unknown(unknowns[0])
    
    @staticmethod
    def _action_for_unknown(unknown: str) -> Action:
        """Map an unknown question to the action that resolves it."""
        unknown_lower = unknown.lower()
        
        if "photo" in unknown_lower or "authentic" in unknown_lower:
            return Action.ANALYZE_PHOTOS
        elif "bio" in unknown_lower or "value" in unknown_lower:
            return Action.ANALYZE_BIO
        elif "red_flag" in unknown_lower or "concern" in unknown_lower:
            return Action.CHECK_RED_FLAGS
        else:
            return Action.ANALYZE_BIO  # Default
    
    @staticmethod
    def estimate_information_gain(action: Action, state_dict: dict) -> float:
        """
        Estimate how much uncertainty this action would reduce (0-1).
        
        Could be enhanced with Bayesian uncertainty estimation.
        For now, simple heuristic.
        """
        # All actions have equal weight in this demo
        return 0.5


class ActionSelector:
    """
    More sophisticated action selection with learning over time.
    """
    
    def __init__(self):
        self.action_effectiveness = {}  # Track which actions help most
    
    def select_action(self, state_dict: dict) -> Action:
        """
        Select action considering both priority and learned effectiveness.
        """
        return Planner.get_next_action(state_dict)
