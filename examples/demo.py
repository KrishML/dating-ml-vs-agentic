"""
Demo: Run the dating agent on a sample profile.

One command to see the agent in action:
    python -m examples.demo
"""

import sys
from pathlib import Path

# Add parent to path so we can import agent module
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.core import Profile, AgentLoop
from agent.memory import Memory


def print_section(title):
    """Pretty print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_agent_basic():
    """Run agent on a single profile."""
    print_section("DEMO: Dating Agent Decision Loop")
    
    # Sample profile
    alice = Profile(
        id="alice_123",
        name="Alice",
        age=28,
        bio=(
            "Software engineer at a startup. I'm passionate about building "
            "products that solve real problems. In my free time, I love hiking, "
            "cooking, and trying new restaurants with friends. Looking for someone "
            "genuine and ambitious."
        ),
        photos=["profile1.jpg", "profile2.jpg", "profile3.jpg", "profile4.jpg"],
        interests=["tech", "outdoors", "cooking", "travel"],
        location="San Francisco, CA",
    )
    
    print(f"Evaluating profile: {alice.name}, {alice.age}")
    print(f"Bio: {alice.bio[:80]}...")
    print(f"Photos: {len(alice.photos)} provided")
    print(f"Location: {alice.location}")
    
    # Run agent
    print_section("Agent Loop: Reducing Uncertainty")
    final_state = AgentLoop.run(alice)
    
    # Results
    print_section("Decision Results")
    print(f"Decision: {final_state.decision.value}")
    print(f"Rationale: {final_state.decision_rationale}")
    
    print("\nAnalysis Details:")
    if final_state.bio_analysis:
        print(f"  - Detected Values: {final_state.bio_analysis.get('values', [])}")
        print(f"  - Red Flags: {final_state.bio_analysis.get('red_flags', [])}")
    
    if final_state.photo_analysis:
        print(f"  - Photo Authenticity: {final_state.photo_analysis.get('authenticity')}")
        print(f"  - Photo Quality: {final_state.photo_analysis.get('quality')}")
    
    if final_state.safety_flags:
        print(f"  - Behavioral Red Flags: {final_state.safety_flags}")
    else:
        print(f"  - Behavioral Red Flags: None")
    
    print(f"\nActions Taken: {final_state.actions_taken}")
    print(f"Total Actions: {len(final_state.actions_taken)}")


def demo_agent_safety_constraint():
    """Show safety constraints in action."""
    print_section("DEMO: Safety Constraints Override All")
    
    # Profile that violates safety
    underage = Profile(
        id="underage_001",
        name="Jordan",
        age=16,
        bio="Just trying dating apps",
        photos=[],
        interests=[],
        location="NYC",
    )
    
    print(f"Evaluating profile: {underage.name}, {underage.age}")
    
    final_state = AgentLoop.run(underage)
    
    print(f"\nDecision: {final_state.decision.value}")
    print(f"Rationale: {final_state.decision_rationale}")
    print("\nKey Point: Safety constraint (age >= 18) blocks any RIGHT decision,")
    print("regardless of other factors. This constraint is NON-NEGOTIABLE.")


def demo_agent_multiple_profiles():
    """Run agent on multiple profiles with memory."""
    print_section("DEMO: Multiple Decisions with Memory")
    
    memory = Memory()
    
    profiles = [
        Profile(
            id="p1",
            name="Charlie",
            age=30,
            bio="Adventurous traveler. Love international cuisine.",
            photos=["c1.jpg", "c2.jpg"],
            interests=["travel", "food", "languages"],
            location="Brooklyn, NY",
        ),
        Profile(
            id="p2",
            name="Diana",
            age=26,
            bio="Artist and dog lover. Quiet nights preferred.",
            photos=["d1.jpg", "d2.jpg", "d3.jpg"],
            interests=["art", "animals", "meditation"],
            location="Portland, OR",
        ),
        Profile(
            id="p3",
            name="Eve",
            age=32,
            bio="Ambitious executive. Work hard, play hard.",
            photos=["e1.jpg"],
            interests=["business", "fitness", "cars"],
            location="Los Angeles, CA",
        ),
    ]
    
    for profile in profiles:
        print(f"\n--- Processing {profile.name} ({profile.age}) from {profile.location} ---")
        
        final_state = AgentLoop.run(profile)
        
        decision = final_state.decision.value
        print(f"Decision: {decision} | Rationale: {final_state.decision_rationale}")
        
        # Record in memory
        memory.record_decision(
            profile.id,
            decision,
            final_state.decision_rationale
        )
    
    # Memory stats
    print_section("Memory Statistics")
    stats = memory.long_term.get_decision_stats()
    print(f"Total decisions: {stats['total']}")
    print(f"Right swipes: {stats['right_swipes']} ({stats['right_percentage']}%)")
    print(f"Left swipes: {stats['left_swipes']}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("DATING AGENT DEMO: ML vs Agentic AI")
    print("="*60)
    
    demo_agent_basic()
    demo_agent_safety_constraint()
    demo_agent_multiple_profiles()
    
    print_section("Demo Complete")
    print("The agent:")
    print("1. Tracks unknowns explicitly")
    print("2. Plans actions to reduce uncertainty")
    print("3. Executes actions (analyze bio, photos, red flags)")
    print("4. Enforces safety constraints (no compromises)")
    print("5. Makes terminal decisions (LEFT or RIGHT)")
    print("6. Stores learnings in memory")


if __name__ == "__main__":
    main()
