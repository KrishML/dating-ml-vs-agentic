# Getting Started

## Installation

```bash
cd /Users/krish-mac/VSCode-Projects/dating-ml-vs-agentic
pip install -r requirements.txt
```

## Run the Demo (One Command)

```bash
python -m examples.demo
```

Expected output: Three demos showing the agent in action:
1. Basic profile evaluation with decision tracing
2. Safety constraints in action (blocking underage profiles)
3. Multiple profiles with memory statistics

## Run the Tests

```bash
pytest tests/test_invariants.py -v
```

Tests verify:
- ✅ No decision while unknowns remain
- ✅ Safety constraints override all decisions
- ✅ Decisions are terminal and idempotent
- ✅ Actions reduce uncertainty
- ✅ Planner chooses actions, not decisions

## Project Highlights

### The Agent Loop (Pure Python)
See [agent/core.py](agent/core.py)

- **Explicit State:** AgentState dataclass tracks everything
- **Unknowns:** List of unresolved decision-relevant facts
- **Planner:** Chooses next action based on remaining unknowns
- **Actions:** Investigate bio, photos, red flags
- **Safety:** Hard constraints checked before decision
- **Decision:** LEFT/RIGHT only when justified
- **Reflection:** Extract learnings for future improvements

### Architecture Diagram
See [docs/architecture.md](docs/architecture.md)

Shows:
- The agentic loop vs traditional ML
- State flow through plan-act-decide cycle
- Safety constraints as first-class citizens
- Complete decision trace example

### LangGraph Formalization
See [agent/langgraph_agent.py](agent/langgraph_agent.py)

- Mirrors core.py logic exactly
- Uses LangGraph nodes and conditional edges
- Same decisions as pure Python implementation
- Makes control flow visualizable

### Architectural Invariants (Tested)
See [tests/test_invariants.py](tests/test_invariants.py)

1. **No decision with unknowns** - Must fail if uncertainties remain
2. **Safety overrides** - Hard constraints block RIGHT decisions
3. **Terminal decisions** - Decisions are idempotent
4. **Actions reduce unknowns** - Each action makes progress
5. **Planner abstraction** - Never chooses final decision

## Key Design Decisions

### Why NOT a Chatbot?
- Control flow is explicit Python, not hidden in prompts
- Decisions are deterministic and debuggable
- Safety is architecture-enforced, not prompt-engineered

### Why NOT a Recommender Model?
- Transparency: Every decision has a rationale
- Safety: Hard constraints, not soft regularization
- Explainability: Unknowns and actions are logged

### Why Agentic?
- Explicit uncertainty tracking
- Action-based planning (reduce unknowns)
- Terminal decisions from evidence
- Memory and reflection for learning

## File Guide

| File | Purpose |
|------|---------|
| [agent/core.py](agent/core.py) | **SOURCE OF TRUTH** - Pure Python agent loop |
| [agent/planner.py](agent/planner.py) | Action selection based on unknowns |
| [agent/actions.py](agent/actions.py) | Bio/photo/red-flag analyzers |
| [agent/safety.py](agent/safety.py) | Hard & soft safety constraints |
| [agent/memory.py](agent/memory.py) | Short-term & long-term memory |
| [agent/reflection.py](agent/reflection.py) | Post-decision pattern extraction |
| [agent/langgraph_agent.py](agent/langgraph_agent.py) | LangGraph formalization (same logic) |
| [examples/demo.py](examples/demo.py) | Executable demonstrations |
| [tests/test_invariants.py](tests/test_invariants.py) | Architectural invariant tests |
| [docs/architecture.md](docs/architecture.md) | Complete architecture documentation |

## Next Steps

### To Extend the Agent:
1. **Better Analyzers:** Integrate real vision models, NLP embeddings
2. **LLM Planner:** Use GPT-4 for intelligent action selection
3. **Vector Memory:** Add FAISS + sentence-transformers for similarity search
4. **Bias Detection:** Monitor decision ratios across demographics
5. **Learning:** Update decision weights based on user feedback

### To Deploy:
1. Add API layer (FastAPI)
2. Add persistent storage (PostgreSQL + FAISS)
3. Add logging and monitoring
4. Add user preference learning
5. Add A/B testing framework

### To Understand Deeply:
1. Read [docs/architecture.md](docs/architecture.md)
2. Walk through [agent/core.py](agent/core.py) line-by-line
3. Trace a decision manually with [examples/demo.py](examples/demo.py)
4. Run and modify [tests/test_invariants.py](tests/test_invariants.py)
5. Compare core.py with langgraph_agent.py

## Questions?

The project is designed to be educational and readable. Every class, method, and design decision has clear comments explaining the WHY.

Start with core.py, then read architecture.md to understand the full system.
