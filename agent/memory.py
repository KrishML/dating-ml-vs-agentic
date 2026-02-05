"""
Memory abstraction for the dating agent.

Supports:
- Short-term state: current decision context
- Vector memory: semantic similarity search over past profiles
- Interaction log: action history for reflection
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class MemoryEntry:
    """A single remembered interaction."""
    profile_id: str
    decision: str  # "LEFT" or "RIGHT"
    rationale: str
    timestamp: datetime
    learned_pattern: Optional[str] = None  # e.g., "prefer_ambitious_over_photos"


class ShortTermMemory:
    """
    Current decision context.
    
    Scoped to a single swipe decision.
    Cleared when decision is made.
    """
    
    def __init__(self):
        self.observations = []
        self.unknowns = []
        self.evidence = {}
    
    def add_observation(self, key: str, value: str):
        """Record an observation (e.g., "values" -> ["ambitious", "honest"])"""
        self.evidence[key] = value
    
    def add_unknown(self, question: str):
        """Track an unresolved question."""
        if question not in self.unknowns:
            self.unknowns.append(question)
    
    def resolve_unknown(self, question: str):
        """Mark a question as resolved."""
        self.unknowns = [u for u in self.unknowns if u != question]
    
    def clear(self):
        """Clear state after decision."""
        self.observations = []
        self.unknowns = []
        self.evidence = {}


class VectorMemory:
    """
    Long-term memory with semantic search.
    
    In production, this would use embeddings (e.g., sentence-transformers)
    and a vector DB (e.g., FAISS, Pinecone).
    
    For this demo, it's a simple list.
    """
    
    def __init__(self):
        self.entries: List[MemoryEntry] = []
    
    def record(self, profile_id: str, decision: str, rationale: str, learned_pattern: Optional[str] = None):
        """Record a decision for future reference."""
        entry = MemoryEntry(
            profile_id=profile_id,
            decision=decision,
            rationale=rationale,
            timestamp=datetime.now(),
            learned_pattern=learned_pattern,
        )
        self.entries.append(entry)
    
    def search_similar(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        """
        Find similar past decisions.
        
        In production, would use embedding similarity.
        For now, simple keyword matching.
        """
        query_lower = query.lower()
        matches = [
            e for e in self.entries
            if query_lower in e.rationale.lower() or query_lower in (e.learned_pattern or "").lower()
        ]
        return matches[:top_k]
    
    def get_decision_stats(self) -> dict:
        """Get statistics on past decisions."""
        if not self.entries:
            return {"total": 0, "right_swipes": 0, "left_swipes": 0}
        
        right_count = sum(1 for e in self.entries if e.decision == "RIGHT")
        left_count = len(self.entries) - right_count
        
        return {
            "total": len(self.entries),
            "right_swipes": right_count,
            "left_swipes": left_count,
            "right_percentage": round(right_count / len(self.entries) * 100, 1),
        }


class Memory:
    """
    Unified memory interface combining short-term and long-term.
    """
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = VectorMemory()
    
    def record_decision(self, profile_id: str, decision: str, rationale: str):
        """Record a decision to long-term memory."""
        self.long_term.record(profile_id, decision, rationale)
    
    def reset_for_new_decision(self):
        """Clear short-term memory for next decision."""
        self.short_term.clear()
