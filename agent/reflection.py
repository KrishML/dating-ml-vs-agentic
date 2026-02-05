"""
Post-decision reflection: extract patterns and learnings.

After a decision is made, the agent reflects on:
- What factors were most decisive?
- What patterns emerge across multiple decisions?
- How should future decisions be informed by this one?
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DecisionPattern:
    """A learned pattern that influences future decisions."""
    pattern: str
    frequency: int  # How many times observed?
    weight: float  # How influential is it? (0-1)


class ReflectionEngine:
    """
    Extract learnings from each decision for future improvement.
    
    In a full system, these patterns would update:
    - Memory for semantic search
    - Planner priorities
    - Decision weights
    - Bias detection
    """
    
    def __init__(self):
        self.patterns: list[DecisionPattern] = []
    
    def reflect(self, state_dict: dict) -> dict:
        """
        After decision, extract what led to it.
        
        Args:
            state_dict: The final AgentState after decision
        
        Returns:
            Reflection summary (mainly for logging/debugging)
        """
        decision = state_dict.get("decision")
        bio_analysis = state_dict.get("bio_analysis", {})
        photo_analysis = state_dict.get("photo_analysis", {})
        safety_flags = state_dict.get("safety_flags", [])
        
        reflection = {
            "decision": decision,
            "key_factors": [],
        }
        
        # What factors influenced the decision?
        if bio_analysis and bio_analysis.get("values"):
            reflection["key_factors"].append(f"values: {', '.join(bio_analysis['values'])}")
        
        if photo_analysis and photo_analysis.get("authenticity") == "high":
            reflection["key_factors"].append("high photo authenticity")
        
        if safety_flags:
            reflection["key_factors"].append(f"red flags: {', '.join(safety_flags)}")
        
        # Update patterns (simplified for demo)
        if decision == "RIGHT" and bio_analysis.get("values"):
            pattern_str = f"VALUES_{' '.join(bio_analysis['values'][:2])}_LEADS_TO_RIGHT"
            self._update_pattern(pattern_str, positive=True)
        
        elif decision == "LEFT" and safety_flags:
            pattern_str = f"RED_FLAGS_{' '.join(safety_flags[:1])}_LEADS_TO_LEFT"
            self._update_pattern(pattern_str, positive=True)
        
        return reflection
    
    def _update_pattern(self, pattern_str: str, positive: bool = True):
        """Track a pattern."""
        # Simple frequency counting
        existing = next((p for p in self.patterns if p.pattern == pattern_str), None)
        if existing:
            existing.frequency += 1
        else:
            self.patterns.append(DecisionPattern(pattern=pattern_str, frequency=1, weight=0.5))
    
    def get_top_patterns(self, n: int = 5) -> list[DecisionPattern]:
        """Get most frequent/influential patterns."""
        return sorted(self.patterns, key=lambda p: p.frequency, reverse=True)[:n]


class MemoryUpdater:
    """
    Update memory systems based on reflection.
    
    In production, would:
    - Store vectors in FAISS
    - Update embedding indices
    - Trigger retraining signals
    """
    
    @staticmethod
    def update_from_reflection(reflection: dict, memory) -> None:
        """
        Use reflection to update memory systems.
        
        Args:
            reflection: Output from ReflectionEngine.reflect()
            memory: Memory object to update
        """
        # Record decision rationale to long-term memory
        key_factors = ", ".join(reflection.get("key_factors", []))
        # memory.long_term.record(...)  # Implementation depends on memory API
