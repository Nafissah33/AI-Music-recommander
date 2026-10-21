# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Challenge 1 ("Add Advanced Song Features") in two parts, done across two separate turns: (1) introduce 5+ complex attributes to `data/songs.csv` not in the baseline data, and (2) update the scoring logic in `src/recommender.py` so scoring actually accounts for the new attributes — not just add them as unused columns.

**Prompts used:**

- "Introduce 5 or more complex attributes to your dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags." (this added the columns, but — caught later — never touched the scoring code)
- "Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes." (this closed the gap)

**What did the agent generate or change?**

- `data/songs.csv`: added 5 columns — `popularity` (0-100), `release_decade`, `explicit` (bool), `instrumentalness` (0-1), `secondary_moods` (semicolon-separated tags) — across all 18 songs.
- `src/recommender.py`: wired 3 of the 5 new attributes into `_score_components` as two new preference rules plus a content filter:
  - **Popularity preference** — rewards high or low `popularity` depending on a new `prefers_popular` field (mainstream vs. discovery), mirroring the existing `likes_acoustic` pattern.
  - **Instrumentalness preference** — same shape, via a new `prefers_instrumental` field (vocal vs. instrumental).
  - **Explicit content filter** — a flat `EXPLICIT_PENALTY` applied when a song is `explicit=True` and the user's `allow_explicit=False`.
  - Extended `Song`, `UserProfile`, `STRATEGIES`, `load_songs`, `score_song`, and `Recommender._score` to carry these through both the dict-based and dataclass-based scoring paths.
- `release_decade` and `secondary_moods` were deliberately left unused — they need more design work (a "favorite decade" concept, and multi-value partial-credit matching) that didn't fit cleanly into the existing additive-points recipe without more thought. Documented as still-open in the model card's Future Work section.

**What did you verify or fix manually?**

- Ran `pytest` after every change (stayed at 2/2 passing throughout).
- Caught a real bias the agent introduced on the first pass: it defaulted `prefers_popular`/`prefers_instrumental` to `False` when absent from a `user_prefs` dict, which silently scored every *old* profile (that never mentions these fields) as if the user had explicitly chosen "discovery" and "vocal" — a repeat of the exact binary-preference flaw already documented for `acousticness`. Asked for a fix: changed the defaults to `None` ("no preference stated"), which skips the score contribution and reason string entirely instead of picking a side. Verified by re-running the same old-style profile before and after — before the fix it scored 6.95 with two new (unwanted) reason lines; after, it scored 5.78, identical to the original 4-rule recipe with zero new lines.
- Verified the explicit-content penalty directly against `City Pulse` (the one `explicit=True` song in the catalog) with `allow_explicit=False` — confirmed the `-2.0` penalty applied and was visible in the reasons list.

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
