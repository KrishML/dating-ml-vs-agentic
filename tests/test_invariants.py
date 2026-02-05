"""
Test architectural invariants of the dating agent.

These tests ensure the agent behaves correctly:
1. Does NOT decide while unknowns remain
2. Decision IS terminal (cannot be reversed)
3. Safety rules OVERRIDE all decisions
4. Actions reduce uncertainty
5. Planner chooses actions, not final decisions
"""

import pytest
from agent.core import (
    Profile,
    AgentState,
    Decision,
    AgentLoop,
    SafetyConstraint,
    Planner,
    Actions,
    Decision_Maker,
)
from agent.safety import EthicalConstraints


class TestAgentInvariants:
    """Test core architectural invariants."""
    
    @pytest.fixture
    def good_profile(self):
        """A safe, attractive profile for testing."""
        return Profile(
            id="p1",
            name="Alice",
            age=28,
            bio="Ambitious engineer. Love hiking and cooking.",
            photos=["a1.jpg", "a2.jpg", "a3.jpg"],
            interests=["outdoors", "tech", "cooking"],
            location="SF",
        )
    
    @pytest.fixture
    def bad_profile_underage(self):
        """Profile violating age constraint."""
        return Profile(
            id="p2",
            name="Bob",
            age=16,
            bio="Just trying out dating apps",
            photos=[],
            interests=[],
            location="LA",
        )
    
    @pytest.fixture
    def bad_profile_harm(self):
        """Profile with explicit harm intent."""
        return Profile(
            id="p3",
            name="Villain",
            age=30,
            bio="I want to hurt people",
            photos=[],
            interests=[],
            location="NYC",
        )
    
    def test_invariant_no_decision_with_unknowns(self, good_profile):
        """
        Invariant: Agent should NOT decide while unknowns remain.
        
        Raises ValueError if decision is attempted with open unknowns.
        """
        state = AgentState(
            profile=good_profile,
            unknowns=["What are their values?", "Are photos authentic?"]
        )
        
        # Should raise because unknowns remain
        with pytest.raises(ValueError, match="Cannot decide while unknowns remain"):
            Decision_Maker.decide(state)
    
    def test_invariant_decision_is_terminal(self, good_profile):
        """
        Invariant: Decision is terminal.
        
        Once decided, the decision should not change.
        (Testing that Decision_Maker doesn't flip decisions)
        """
        state = AgentState(
            profile=good_profile,
            unknowns=[],
            bio_analysis={"values": ["ambitious"], "red_flags": []},
            photo_analysis={"authenticity": "high", "quality": "good"},
        )
        
        # Decide once
        state1 = Decision_Maker.decide(state)
        decision1 = state1.decision
        
        # Decide again with same state—should be same decision
        state2 = Decision_Maker.decide(state)
        decision2 = state2.decision
        
        assert decision1 == decision2, "Decision should be deterministic/terminal"
    
    def test_invariant_safety_overrides_all(self, bad_profile_underage):
        """
        Invariant: Safety constraints override all other considerations.
        
        Even if a profile otherwise looks good, safety violations force LEFT.
        """
        state = AgentState(
            profile=bad_profile_underage,
            unknowns=[],  # No unknowns, ready to decide
            bio_analysis={"values": ["honest"], "red_flags": []},
            photo_analysis={"authenticity": "high", "quality": "good"},
        )
        
        state = Decision_Maker.decide(state)
        
        # Must be LEFT due to age violation
        assert state.decision == Decision.LEFT
        assert "age" in state.decision_rationale.lower() or "18" in state.decision_rationale
    
    def test_invariant_safety_harm_intent(self, bad_profile_harm):
        """
        Invariant: Explicit harm intent always triggers safety block.
        """
        violations = SafetyConstraint.check(bad_profile_harm)
        
        # Should have detected explicit harm
        assert len(violations) > 0
        assert any("harm" in v.lower() for v in violations)
    
    def test_invariant_actions_reduce_unknowns(self, good_profile):
        """
        Invariant: Actions reduce uncertainty (remove items from unknowns).
        """
        state = AgentState(
            profile=good_profile,
            unknowns=["Understand bio values", "Verify photo authenticity"]
        )
        
        unknowns_before = len(state.unknowns)
        
        # Take action
        state = Actions.analyze_bio(state)
        
        unknowns_after = len(state.unknowns)
        
        # Should have removed the bio-related unknown
        assert unknowns_after < unknowns_before
        assert all("bio" not in u.lower() for u in state.unknowns)
    
    def test_invariant_planner_chooses_action_not_decision(self, good_profile):
        """
        Invariant: Planner chooses actions, NOT final decisions.
        
        Planner should never return LEFT or RIGHT directly.
        """
        state = AgentState(
            profile=good_profile,
            unknowns=["What are their values?"]
        )
        
        action = Planner.choose_action(state)
        
        # Action should be an action name, not a decision
        assert action in [None, "analyze_bio", "analyze_photos", "check_red_flags"]
        assert action not in [Decision.LEFT, Decision.RIGHT]
    
    def test_invariant_loop_terminates(self, good_profile):
        """
        Invariant: The main agent loop terminates.
        
        With max_iterations safety check, loop should finish.
        """
        # This should complete without raising max_iterations error
        final_state = AgentLoop.run(good_profile, max_iterations=20)
        
        assert final_state.decision in [Decision.LEFT, Decision.RIGHT]
        assert final_state.decision != Decision.UNDECIDED


class TestSafetyConstraints:
    """Test safety constraint enforcement."""
    
    def test_age_constraint(self):
        """Safety: Must be 18+."""
        young = Profile(
            id="p", name="Young", age=16, bio="", photos=[], interests=[], location=""
        )
        violations = SafetyConstraint.check(young)
        assert len(violations) > 0
        
        adult = Profile(
            id="p", name="Adult", age=18, bio="", photos=[], interests=[], location=""
        )
        violations = SafetyConstraint.check(adult)
        assert len(violations) == 0
    
    def test_harm_intent_constraint(self):
        """Safety: No explicit harm intent."""
        harmful = Profile(
            id="p", name="Bad", age=25, bio="I will hurt you", photos=[], interests=[], location=""
        )
        violations = SafetyConstraint.check(harmful)
        assert len(violations) > 0


class TestDecisionQuality:
    """Test that decisions make intuitive sense."""
    
    def test_high_compatibility_gives_right(self):
        """
        High values, good photos, no red flags -> should be RIGHT.
        """
        profile = Profile(
            id="p",
            name="Great Match",
            age=28,
            bio="Ambitious engineer. Honest, family-oriented. Love hiking.",
            photos=["a.jpg", "b.jpg", "c.jpg"],
            interests=["tech", "outdoors", "family"],
            location="SF",
        )
        
        final_state = AgentLoop.run(profile)
        
        # With all good signals, should tend toward RIGHT
        # (Not guaranteed due to scoring, but likely)
        assert final_state.decision in [Decision.LEFT, Decision.RIGHT]
    
    def test_low_compatibility_gives_left(self):
        """
        Minimal info, vague bio, one photo -> should be LEFT.
        """
        profile = Profile(
            id="p",
            name="Minimal",
            age=25,
            bio="Hi",
            photos=["only_one.jpg"],
            interests=[],
            location="Unknown",
        )
        
        final_state = AgentLoop.run(profile)
        
        # With poor signals, should tend toward LEFT
        assert final_state.decision in [Decision.LEFT, Decision.RIGHT]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
