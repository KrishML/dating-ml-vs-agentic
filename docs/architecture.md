# Architecture: Dating Swipe Decision Agent

## Overview

This project demonstrates an **agentic AI system**—not a chatbot, not a recommender model, but an explicit agent with **state, planner, actions, memory, and decision logic**.

The agent decides whether to swipe LEFT or RIGHT on dating profiles while:
- ✅ Tracking unknowns explicitly
- ✅ Planning actions to reduce uncertainty
- ✅ Enforcing safety constraints as first-class citizens
- ✅ Making terminal decisions based on evidence
- ✅ Reflecting and learning from decisions

## Agentic vs ML: Key Differences

### Traditional ML Pipeline
```
Profile Input → Feature Extraction → Model Prediction → Decision (LEFT/RIGHT)
  │                                        │
  └─────── Black Box (Hard to Explain) ────┘
```

**Problems:**
- No transparency about what uncertainties remain
- Cannot reason under incomplete information
- Safety rules buried in training data, not enforced in code
- Decisions cannot be justified or audited

### Agentic AI Loop (This Project)
```
┌─────────────────────────────────────────────────┐
│                    Agent State                  │
│  - Profile (name, age, bio, photos)            │
│  - Unknowns (unresolved questions)             │
│  - Observations (gathered facts)               │
│  - Decision (LEFT/RIGHT/UNDECIDED)             │
└─────────────────────────────────────────────────┘
              ↑                          ↓
              │                          │
          REFLECT              PLANNER (What to investigate next?)
              │                          │
              │         ┌───────────────┴────────────────┐
              │         ↓                                ↓
              │   ACTION: Analyze Bio              ACTION: Analyze Photos
              │   - Extract values                 - Check authenticity
              │   - Detect red flags               - Assess quality
              │         │                                ↓
              │         └──────────────┬─────────────────┘
              │                        ↓
              │               ACTION: Check Red Flags
              │               - Behavioral concerns
              │               - Safety validation
              │                        │
              │                        ↓
              │           All Unknowns Resolved?
              │           - NO: Loop back to PLANNER
              │           - YES: Proceed to DECISION
              │                        │
              └────────────────────────↓
                          DECISION MAKER
                    - Check safety constraints
                    - Score compatibility
                    - Make LEFT/RIGHT decision
                    - Store in memory
```

**Advantages:**
- Explicit reasoning about uncertainty
- Safety constraints are non-negotiable
- Every decision is auditable and explainable
- Can handle partial information
- Learns from patterns over time

---

## Project Structure

```
dating-agent/
├── agent/                      # Core agent implementation
│   ├── __init__.py
│   ├── core.py                 # ⭐ Pure Python agent loop (source of truth)
│   ├── planner.py              # Action selection logic
│   ├── actions.py              # Bio/photo/red-flag analyzers
│   ├── memory.py               # Short-term & long-term memory
│   ├── safety.py               # Safety constraints & ethics
│   ├── reflection.py           # Post-decision learning
│   └── langgraph_agent.py      # LangGraph formalization
│
├── examples/
│   └── demo.py                 # One-command demo
│
├── tests/
│   ├── __init__.py
│   └── test_invariants.py      # Architectural invariant tests
│
├── docs/
│   └── architecture.md         # This file
│
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── requirements.txt
```

---

## Core Components

### 1. **State** (`agent/core.py`)

The agent's complete knowledge about the current decision:

```python
@dataclass
class AgentState:
    profile: Profile                          # What we're evaluating
    unknowns: list[str]                       # Open questions
    bio_analysis: Optional[dict]              # Observations from bio
    photo_analysis: Optional[dict]            # Observations from photos
    safety_flags: list[str]                   # Red flag detections
    actions_taken: list[str]                  # History for debugging
    decision: Decision                        # UNDECIDED / LEFT / RIGHT
    decision_rationale: str                   # Why we decided
```

**Key Principle:** State is explicit and immutable. Every update creates a new state snapshot.

### 2. **Planner** (`agent/planner.py`)

Chooses the NEXT ACTION to reduce uncertainty.

```python
class Planner:
    @staticmethod
    def get_next_action(state: dict) -> Action:
        """Given unknowns, which action resolves most uncertainty?"""
        unknowns = state["unknowns"]
        
        if not unknowns:
            return Action.COMPLETE
        
        # Priority-based selection
        for priority_unknown in PRIORITY_ORDER:
            for unknown in unknowns:
                if priority_unknown in unknown.lower():
                    return UNKNOWN_TO_ACTION[priority_unknown]
        
        return Action.ANALYZE_BIO  # Default
```

**Key Principle:** Planner never decides LEFT/RIGHT. It ONLY chooses actions.

### 3. **Actions** (`agent/actions.py`)

Investigative operations that reduce uncertainty:

#### `BioAnalyzer`
- Extracts values from text (ambitious, adventurous, family-oriented, etc.)
- Detects red-flag language (toxic, drama, control, etc.)

#### `PhotoAnalyzer`
- Assesses authenticity (single photo = low, 4+ = high)
- Evaluates quality and diversity

#### `RedFlagDetector`
- Age gap concerns
- Vague bios
- Single photo (catfish risk)

**Key Principle:** Each action updates state and removes resolved unknowns.

### 4. **Safety Constraints** (`agent/safety.py`)

Hard rules that BLOCK any RIGHT decision:

```python
HARD_CONSTRAINTS = {
    "age_minimum": lambda profile: profile.age >= 18,
    "no_catfish": lambda profile: True,  # Requires vision model
    "no_harm_intent": lambda profile: not has_harm_keywords(profile.bio),
}
```

**Key Principle:** Safety is not a heuristic or a weight in a scoring function. It is code that executes BEFORE decision.

### 5. **Memory** (`agent/memory.py`)

Two-tier memory system:

- **Short-term:** Current decision context (cleared after swipe)
- **Long-term:** All past decisions, searchable by similarity

```python
class Memory:
    def record_decision(self, profile_id, decision, rationale):
        """Store in long-term memory for pattern learning"""
    
    def search_similar(self, query, top_k=5):
        """Find similar past decisions (e.g., 'ambitious profile')"""
```

### 6. **Reflection** (`agent/reflection.py`)

Post-decision analysis:

```python
reflection = {
    "decision": "RIGHT",
    "key_factors": ["values: ambitious, honest", "high photo authenticity"],
}
```

Patterns are stored for future action prioritization.

---

## Agent Loop

The main control flow in `AgentLoop.run()`:

```python
def run(profile: Profile, max_iterations: int = 10) -> AgentState:
    # 1. Initialize state with unknowns
    state = AgentState(
        profile=profile,
        unknowns=[
            "Understand bio values and red flags",
            "Verify photo authenticity",
            "Check for behavioral red flags",
        ]
    )
    
    # 2. Plan-act loop: reduce uncertainty
    while state.unknowns and iterations < max_iterations:
        action = Planner.choose_action(state)
        if action is None:
            break
        
        # Execute action
        if action == "analyze_bio":
            state = Actions.analyze_bio(state)
        elif action == "analyze_photos":
            state = Actions.analyze_photos(state)
        # ... etc
    
    # 3. Safety check + decision
    state = Decision_Maker.decide(state)
    
    # 4. Reflect
    state = Reflection.reflect(state)
    
    return state
```

---

## Invariants (Tested in `tests/test_invariants.py`)

### Invariant 1: No Decision with Unknowns
```python
def test_invariant_no_decision_with_unknowns():
    state = AgentState(unknowns=["What are their values?"])
    with pytest.raises(ValueError):
        Decision_Maker.decide(state)  # Must fail
```

### Invariant 2: Safety Overrides All
```python
def test_invariant_safety_overrides():
    bad_profile = Profile(age=16, ...)  # Age < 18
    state = AgentState(profile=bad_profile)
    state = Decision_Maker.decide(state)
    assert state.decision == Decision.LEFT  # Always LEFT
```

### Invariant 3: Decisions are Terminal
```python
decision1 = Decision_Maker.decide(state)
decision2 = Decision_Maker.decide(state)
assert decision1.decision == decision2.decision  # Idempotent
```

### Invariant 4: Actions Reduce Unknowns
```python
assert len(state.unknowns) < len(state_before.unknowns)
```

### Invariant 5: Planner Never Decides
```python
action = Planner.get_next_action(state)
assert action not in [Decision.LEFT, Decision.RIGHT]
```

---

## LangGraph Formalization

[langgraph_agent.py](../agent/langgraph_agent.py) implements the SAME agent using LangGraph:

```
graph = StateGraph(AgentState)

graph.add_node("plan", node_plan)
graph.add_node("analyze_bio", node_analyze_bio)
graph.add_node("analyze_photos", node_analyze_photos)
graph.add_node("check_red_flags", node_check_red_flags)
graph.add_node("decide", node_decide)

graph.add_edge("plan", "analyze_bio")  # Conditional routing
graph.add_edge("analyze_bio", "plan")
# ... etc
```

**Purpose:** LangGraph makes the control flow visualizable and serializable. It's a FORMALIZATION, not a redesign.

**Key Point:** Both `core.py` (pure Python) and `langgraph_agent.py` implement the same logic. They should produce identical decisions for identical inputs.

---

## Safety & Ethics

Safety is architecture-first:

### Hard Constraints (Non-Negotiable)
- Age >= 18
- No catfish indicators
- No explicit harm intent

### Soft Constraints (Informative)
- Age gap concerns (10+ years)
- Red-flag language patterns

### Bias Detection
- Monitor decision ratios across demographic groups
- Flag systematic skew

See [agent/safety.py](../agent/safety.py) for implementation.

---

## Example: Decision Trace

```
Profile: Alice, 28, SF
Bio: "Engineer. Love hiking, cooking. Ambitious."
Photos: 4 provided

AGENT LOOP:
┌─────────────────────────────────┐
│ State: UNDECIDED, 3 unknowns    │
└─────────────────────────────────┘
         ↓
    Planner: "Analyze bio"
         ↓
    Action: extract_values() → ["ambitious", "adventurous"]
    Unknown resolved: ✓ "understand_values"
         ↓
┌─────────────────────────────────┐
│ State: UNDECIDED, 2 unknowns    │
│ bio_analysis: {values: [...]}   │
└─────────────────────────────────┘
         ↓
    Planner: "Analyze photos"
         ↓
    Action: check_authenticity() → "high" (4 photos)
    Unknown resolved: ✓ "verify_authenticity"
         ↓
┌─────────────────────────────────┐
│ State: UNDECIDED, 1 unknown     │
│ photo_analysis: {authenticity...}
└─────────────────────────────────┘
         ↓
    Planner: "Check red flags"
         ↓
    Action: detect_red_flags() → []
    Unknown resolved: ✓ "behavioral_concerns"
         ↓
┌─────────────────────────────────┐
│ State: UNDECIDED, 0 unknowns    │
│ All observations gathered       │
└─────────────────────────────────┘
         ↓
    Safety Check: ✓ All constraints pass
         ↓
    Decision Scoring:
    - Values: +2 × 2 = +4
    - Red flags: 0 × -3 = 0
    - Age gap: 30-28 = 2 → +8
    - Photo quality: +2 +2 = +4
    Total Score: 18 (threshold: 5)
         ↓
    Decision: RIGHT
    Rationale: "Positive match (score: 18)"
         ↓
    Reflection: Store pattern "AMBITIOUS_ADVENTUROUS_LEADS_RIGHT"
```

---

## Running the Project

### Installation
```bash
pip install -r requirements.txt
```

### Run Demo
```bash
python -m examples.demo
```

### Run Tests
```bash
pytest tests/test_invariants.py -v
```

---

## Design Principles

1. **Explicit over Implicit**
   - State is a dataclass, not buried in module globals
   - Control flow is Python, not prompts

2. **Safety First**
   - Constraints are first-class code, not heuristics
   - Safety checks happen BEFORE decisions

3. **Uncertainty is Real**
   - Unknowns are tracked explicitly
   - No decision happens while uncertainty remains

4. **Actions > Decisions**
   - Planner chooses actions, not final answers
   - Decisions emerge from sufficient evidence

5. **Auditable & Debuggable**
   - Every decision has a rationale
   - Action history is recorded
   - Tests validate invariants

---

## Future Enhancements

- [ ] LLM-based planner (GPT-4 action selection)
- [ ] Vector embeddings for memory search (FAISS + sentence-transformers)
- [ ] Bias detection and mitigation
- [ ] Multi-user comparison (cross-swipe matching)
- [ ] Learning from matches (update weights based on feedback)
- [ ] Web UI for interactive swiping

---

## References

- **State Machines:** The agent is a finite state machine with explicit transitions
- **Planning:** Analogous to STRIPS planning (state → goals → actions)
- **Safety:** Inspired by AI safety constraints (Anthropic, DeepMind)
- **Reflection:** Self-improvement via experience replay

---

## License

[LICENSE](../LICENSE)

