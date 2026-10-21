# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

It checks how close a song's "vibe" is to what you say you like.

---

## 2. Intended Use  

**Goal:** VibeMatch suggests songs based on one person's stated taste. It is not trying to guess your taste from your listening history. You tell it what you like, and it finds songs that match.

**Who it's for:** This is a classroom project, not a real app. It's meant to show how a simple recommender works, step by step.

**What it assumes:** It assumes you have one clear, steady taste. It picks one favorite genre, one favorite mood, one target energy level, and one acoustic preference. It does not handle people whose taste changes by mood or situation.

**Intended use:** Learning how content-based recommenders work. Testing how scoring rules affect rankings. Exploring bias and edge cases in a small, controlled catalog.

**Not intended for:** Real listeners or a real streaming product. Large catalogs (it was only tested with 18 songs). Users with mixed, changing, or multiple tastes at once. Any use where a wrong or unfair recommendation would actually matter.

---

## 3. How the Model Works  

Every song gets points, one rule at a time:

1. **Genre match:** if the song's genre is your favorite genre, it gets 2 points.
2. **Mood match:** if the song's mood is your favorite mood, it gets 1 point.
3. **Energy match:** the closer the song's energy is to the energy you asked for, the more points it gets — up to 2 points for a perfect match.
4. **Acoustic match:** if you said you like acoustic songs, acoustic songs get up to 1 extra point. If you said you don't, non-acoustic songs get that point instead.

All four point values are added into one final score. Every song in the catalog gets scored this way, not just a few. Then the songs are sorted from highest score to lowest, and the top matches are shown with the reasons behind each score.

Changes from the starter logic: the starter file only had empty placeholder functions. I built the whole scoring rule from scratch, and I chose "closeness" for energy instead of just "higher is better," so a song doesn't win just because it's loud — it wins because it's close to what you asked for.

---

## 4. Data  

The catalog has **18 songs** in `data/songs.csv`. Each song has a genre, a mood, and five number features: energy, tempo, valence, danceability, and acousticness.

There are 15 different genres and 14 different moods across those 18 songs — pop, lofi, rock, jazz, ambient, synthwave, indie pop, hip hop, classical, folk, r&b, metal, country, house, and reggae. Most genres and moods only show up on one song each.

I started with 10 songs and added 8 more, picking genres and moods that weren't there yet, so the catalog would cover more kinds of music.

Because the catalog is so small and so spread out, a user whose favorite genre only has one song in the whole catalog can never get more than one real match — there's no "second choice" in that genre for the system to offer.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

One weakness I found while testing the Chill Lofi persona (`favorite_genre=lofi, favorite_mood=chill, target_energy=0.35, likes_acoustic=True`) is that the recommender over-concentrates on a single artist instead of spreading recommendations across different voices. Two of the five results — "Midnight Coding" and "Focus Flow" — are both by the same artist, LoRoom, meaning 40% of that user's top-5 list came from one act simply because LoRoom happens to make several lofi/chill-adjacent tracks in the catalog. This happens because the Ranking Rule only sorts by score and slices the top k; nothing in `recommend_songs` checks for repeated artists or caps how many songs from one artist can appear. In a larger real-world catalog, this is exactly how filter bubbles form — a user who likes one artist's style gets buried in more of that same artist instead of discovering similar-but-different artists. Fixing this would require adding a diversity rule to the Ranking Rule (e.g., skip or demote a song if its artist is already in the result set) rather than changing the per-song Scoring Rule at all.

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

In addition to the three "normal" personas in `src/main.py` (High-Energy Pop, Chill Lofi, Deep Intense Rock — see sample output in the README), I ran five adversarial/edge-case profiles against the scoring logic to see whether it could be tricked or produce unexpected results.

```
=== Conflicting (high-energy target + relaxed mood + likes_acoustic) ===
    profile: {'favorite_genre': 'metal', 'favorite_mood': 'relaxed', 'target_energy': 0.95, 'likes_acoustic': True}
  1. Iron Fury              (metal      angry     ) score=3.99
  2. Coffee Shop Stories    (jazz       relaxed   ) score=2.73
  3. Storm Runner           (rock       intense   ) score=2.02
  4. Gym Hero               (pop        intense   ) score=2.01
  5. Rooftop Lights         (indie pop  happy     ) score=1.97

=== Nonexistent genre (typo/unknown) ===
    profile: {'favorite_genre': 'k-pop', 'favorite_mood': 'happy', 'target_energy': 0.6, 'likes_acoustic': False}
  1. Sunrise City           (pop        happy     ) score=3.38
  2. Rooftop Lights         (indie pop  happy     ) score=3.33
  3. Slow Burn              (r&b        romantic  ) score=2.60
  4. City Pulse             (hip hop    energetic ) score=2.56
  5. Night Drive Loop       (synthwave  moody     ) score=2.48

=== Case-sensitivity trap (Pop vs pop) ===
    profile: {'favorite_genre': 'Pop', 'favorite_mood': 'Happy', 'target_energy': 0.8, 'likes_acoustic': False}
  1. City Pulse             (hip hop    energetic ) score=2.88
  2. Neon Sunrise           (house      euphoric  ) score=2.80
  3. Sunrise City           (pop        happy     ) score=2.78
  4. Gym Hero               (pop        intense   ) score=2.69
  5. Storm Runner           (rock       intense   ) score=2.68

=== Out-of-range target_energy (> 1.0) ===
    profile: {'favorite_genre': 'pop', 'favorite_mood': 'happy', 'target_energy': 1.5, 'likes_acoustic': False}
  1. Sunrise City           (pop        happy     ) score=4.46
  2. Gym Hero               (pop        intense   ) score=3.81
  3. Rooftop Lights         (indie pop  happy     ) score=2.17
  4. Iron Fury              (metal      angry     ) score=1.91
  5. Storm Runner           (rock       intense   ) score=1.72

=== Out-of-range target_energy (negative) ===
    profile: {'favorite_genre': 'pop', 'favorite_mood': 'happy', 'target_energy': -0.5, 'likes_acoustic': False}
  1. Sunrise City           (pop        happy     ) score=3.18
  2. Gym Hero               (pop        intense   ) score=2.09
  3. Rooftop Lights         (indie pop  happy     ) score=1.13
  4. Quiet Hall             (classical  peaceful  ) score=0.65
  5. Island Drift           (reggae     carefree  ) score=0.60
```

**Pairwise comparisons between profiles (plain language):**

- **High-Energy Pop vs. Chill Lofi — zero songs in common.** These two profiles want opposite things (loud/energetic/non-acoustic vs. quiet/mellow/acoustic), and the results reflect that perfectly: not a single song overlaps between their top-5 lists. That's exactly what should happen — if two people describe completely opposite tastes, the app shouldn't hand them the same playlist.

- **High-Energy Pop vs. Deep Intense Rock — 4 of 5 songs in common.** These two only disagree on genre (pop vs. rock) but both want the same "intense," high-energy feel. Because they agree on 2 of the 4 scoring rules (mood and energy), almost the same songs win for both — they just swap which one takes the #1 spot depending on which genre is asked for. This makes sense: the system is correctly picking up on "these two users actually want very similar music, just branded differently."

- **Chill Lofi vs. Deep Intense Rock — zero songs in common.** The most extreme opposite pairing we tested (quiet/acoustic vs. loud/aggressive), and again, completely different result sets. This is the clearest sign the energy and acousticness rules are doing real work — they're not just noise, they visibly separate two very different kinds of listeners.

**Why does "Gym Hero" keep showing up for people who just want "Happy Pop"?** In plain terms: the system doesn't require a song to match *everything* you asked for before it's allowed to show up — it hands out points piece by piece and adds them together. Gym Hero is officially tagged "intense," not "happy," so it technically misses the mood you asked for. But it's still a real pop song (full credit there), and it's extremely high-energy, which lands close to what an upbeat "happy pop" fan usually wants anyway. So even without the "happy" label, Gym Hero racks up enough points from genre + energy + its produced (non-acoustic) sound that it out-scores plenty of songs that are technically happier but don't fit the genre or energy as well. In short: Gym Hero is loud, polished pop — and loud, polished pop reads as "upbeat" to the scoring system even when its own mood tag says otherwise, so it keeps sneaking in by winning on 3 out of 4 criteria instead of all 4.

**What surprised me:**

- The **case-sensitivity trap** was the most concerning result: typing `"Pop"`/`"Happy"` instead of `"pop"`/`"happy"` silently zeroed out both the genre and mood rules for every song, with no error. The top result (City Pulse, hip hop) isn't even a pop song — it only won on energy+acoustic by default, and the system gave no indication that two of its four rules had silently stopped working.
- The **conflicting-preferences** profile (wanting metal energy *and* a relaxed mood *and* acoustic sound) resolved by just ignoring the two lower-weighted rules — Iron Fury won despite failing both mood and acoustic, which exposes that genre+energy (max 4.0 combined) will always dominate mood+acoustic (max 2.0 combined) whenever preferences contradict each other.
- The **out-of-range `target_energy`** values (1.5 and -0.5) didn't crash, but the negative case let the energy component go below zero, breaking the "up to +2.0" ceiling documented in the Algorithm Recipe — there's no input validation clamping `target_energy` to its intended `[0, 1]` range.
- A profile missing the `likes_acoustic` key raised an unhandled `KeyError` — there's no validation or friendly error message for malformed `user_prefs` dicts.

**Sensitivity test (Weight Shift experiment):** I temporarily changed the Algorithm Recipe weights in `src/recommender.py` — halving genre (2.0 → 1.0) and doubling energy (2.0 → 4.0) — and re-ran all three personas to see whether the rankings got *more accurate* or just *different*.

```
High-Energy Pop:    Storm Runner (rock) swapped past Sunrise City (pop) at #2/#3
Chill Lofi:         Spacewalk Thoughts (ambient) swapped past Focus Flow (lofi) at #3/#4
Deep Intense Rock:  only #5 changed; top 4 unaffected
```

In both cases where the ranking actually moved, a song from the *wrong* genre overtook a song from the *right* genre, purely because it sat slightly closer to the target energy. Since these personas are defined by their genre ("High-Energy **Pop**," "Chill **Lofi**"), that's a regression against the user's stated intent, not an improvement — the result was **different, not more accurate**. This confirmed the original 2.0/2.0 weighting was the better call: it keeps genre meaningful as a tie-breaker instead of letting energy proximity override it. I reverted the weights back to the finalized recipe (`GENRE_WEIGHT=2.0`, `ENERGY_WEIGHT=2.0`) afterward.

These are documented further in the Limitations and Bias section below.

---

## 8. Future Work  

If I kept developing this, here's what I'd change first:

1. **Add an artist diversity rule.** Right now, two songs by the same artist can both land in someone's top 5 (this happened with "LoRoom" in the Chill Lofi test). I'd cap it so only one or two songs per artist can show up at once.
2. **Give partial credit for "close" genres and moods**, instead of all-or-nothing exact matches. Right now "indie pop" gets zero credit toward a "pop" fan, even though they're clearly related.
3. **Add input validation.** A typo like "Pop" instead of "pop," or a missing preference, should give a clear error message instead of silently breaking the scoring or crashing.

---

## 9. Personal Reflection  

**Biggest learning moment:** Weight tuning isn't validated by intuition alone — it needs a controlled before/after comparison. I ran a sensitivity test swapping `GENRE_WEIGHT` from `2.0→1.0` and `ENERGY_WEIGHT` from `2.0→4.0` in `_score_components`. The hypothesis was that heavier energy-weighting would produce "more accurate" rankings. Instead, it let out-of-genre songs (e.g. Storm Runner, `genre=rock`) outrank in-genre songs (Sunrise City, `genre=pop`) for a persona explicitly defined by `favorite_genre=pop`, purely because `1 - abs(energy - target_energy)` scored marginally higher. That's a measurable regression against stated user intent, not an improvement — it taught me that a weight change needs a regression check against the *original* use case, not just a plausibility argument.

**AI tool usage — leverage vs. verification:** The main leverage was running many profile/scoring permutations fast — e.g. 5 adversarial `user_prefs` dicts against `recommend_songs` in one pass instead of manually tracing `_score_components` by hand for each. But generated code needs execution-level verification, not just a read-through. Concretely: an edit to `src/main.py`'s docstring left an **unterminated triple-quoted string literal** (`SyntaxError`) that wasn't caught until I actually ran `python -m src.main` — a visual diff review wouldn't have caught it since the error only surfaces at parse time. The same pattern showed up again with the import path itself: a fix that worked under `python -m src.main` silently failed under the IDE's Run button (`python3 src/main.py` directly), and that mismatch only surfaced because I ran it through my own actual workflow and pasted back the real traceback, not because the code "looked" wrong. Lesson: two different ways of running the same file can both look reasonable on paper and only one of them actually works — the only way to know is to run both.

**On simple algorithms "feeling" like recommendations:** `_score_components` is a weighted linear sum of four independent terms — two boolean exact-match checks (`genre == favorite_genre`, `mood == favorite_mood`) and two continuous proximity terms (`energy`, `acousticness`) — no learning, no cross-feature interaction, no historical data. Yet the top-1 result for each persona (Sunrise City for Happy Pop, Library Rain for Chill Lofi, Storm Runner for Deep Intense Rock) reads as intuitively "correct." The illusion breaks under adversarial input, though: a case-sensitivity mismatch (`"Pop"` vs `"pop"`) silently zeroed two of the four score terms with no exception raised, and the top result degraded to whatever scored highest on the two remaining terms (City Pulse, `genre=hip hop`) — a reminder that exact-match string comparison has zero fault tolerance, unlike the continuous terms which degrade gracefully. Printing the per-term "reasons" alongside the score turned out to matter more than I expected for this illusion too — seeing `genre matches (+2.0), energy close to target (+1.96)` makes plain arithmetic read as judgment, independent of whether the ranking is actually good.

**Closing the loop on an earlier finding:** The artist/genre concentration we found in testing (LoRoom taking 2 of 5 slots in the Chill Lofi results) stopped being just a documented limitation — I added a Diversity Penalty to the Ranking Rule (`_select_diverse_top_k` in `src/recommender.py`) that greedily re-ranks the top-k, penalizing repeated artists and genres as they're picked. Verified against the exact same Chill Lofi profile: LoRoom now appears once instead of twice, replaced by a different artist (River Bend) that previously never cracked the top 5. I also generalized the weight system into a Strategy pattern (`STRATEGIES` dict of named weight presets — `genre_first`, `mood_first`, `energy_focused`, `balanced`) so ranking modes can be swapped at runtime without touching `_score_components`, and switched the terminal output to a `tabulate` table so the per-song reasons stay readable instead of scrolling past in a bullet list.

**Next steps if extended:**
1. Replace exact-match genre/mood scoring with a similarity/adjacency table (or use the `secondary_moods` column already added to `songs.csv` but never wired into scoring) so related categories (`indie pop` ≈ `pop`) get partial credit instead of `0`.
2. Add input validation/clamping on `target_energy` to `[0, 1]` and schema validation on `user_prefs` — a case-typo (`"Pop"` vs `"pop"`) or a missing key still either silently degrades the scoring or raises a raw `KeyError` instead of a clear message. This was found during adversarial testing but never actually patched.
3. Represent eclectic/bimodal taste — right now `target_energy` is a single scalar, so a user who genuinely likes both very calm and very intense music can't be represented without one of their real preferences scoring poorly.
4. Add `pytest` coverage for everything built after the original two tests — `score_song`, `recommend_songs`, the Strategy pattern, and the diversity penalty have all been checked manually via terminal runs in this project, but none of them have an actual regression test guarding them going forward.
