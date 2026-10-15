# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

The **Strategy pattern** — swappable ranking algorithms (`genre_first`, `mood_first`, `energy_focused`, `balanced`) that can be selected at runtime without changing the scoring/ranking code itself.

**How did AI help you brainstorm or implement it?**

I asked the AI assistant to help build 2+ switchable ranking modes ("Genre-First," "Mood-First," "Energy-Focused") and to brainstorm a design pattern that would keep the code modular rather than duplicating the scoring function for each mode. It proposed implementing Strategy the idiomatic Python way — not with an abstract base class and subclasses per strategy (the classic Java-style version), but as a dictionary of named weight presets (`STRATEGIES: Dict[str, Dict[str, float]]`) passed as a parameter into the existing scoring function. This kept the change small: it reused the `_score_components` function that was already parameterized with hardcoded weight constants from an earlier experiment (the Weight Shift sensitivity test), and just turned those constants into a `weights` dict argument instead. I verified the result by running `pytest` (still passing) and printing a strategy-comparison demo in `main.py` that runs the same user profile through all four strategies — confirming each one produces a genuinely different ranking, not just a cosmetic change.

**How does the pattern appear in your final code?**

- `STRATEGIES` dict and `_score_components(..., weights=...)` in [src/recommender.py](src/recommender.py) — the "strategy" is the `weights` dict (genre/mood/energy/acoustic multipliers), and the "context" that uses it is `_score_components`.
- `Recommender.__init__(self, songs, strategy: str = "balanced")` — the OOP path selects a strategy at construction time.
- `score_song` / `recommend_songs` accept an optional `weights` parameter so the functional path can switch strategies per call.
- `src/main.py` sets `ACTIVE_STRATEGY` as the mode switch, and includes a demo that runs one profile through all four strategies side by side.
