# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify or YouTube typically combine two approaches: **collaborative filtering**, which predicts what you'll like based on patterns across other users (people who liked what you liked also liked this), and **content-based filtering**, which predicts based on the attributes of songs you already like (similar genre, energy, mood). Collaborative filtering needs a large history of many users' likes, skips, and playlists to work, which this classroom simulation doesn't have — so this version is a **content-based recommender**: it scores each song purely against one user's stated taste profile. It rewards exact matches on `genre` and `mood`, and for numeric features like `energy` it rewards *closeness* to the user's target value rather than simply "higher is better," since a user who wants energy 0.8 shouldn't be penalized less for a 0.3 song than for a 0.75 song being "too close." Genre is weighted more heavily than mood, since genre tends to be a harder, more stable preference boundary for most listeners, while mood shifts with context. The system computes a weighted score for every song in the catalog, then ranks and returns the top `k` matches along with a plain-language explanation of why each one scored the way it did.

**`Song` features:**

- `genre` — categorical (pop, lofi, rock, jazz, ambient, synthwave, indie pop)
- `mood` — categorical (happy, chill, intense, relaxed, moody, focused)
- `energy` — numeric, 0–1
- `tempo_bpm` — numeric, beats per minute
- `valence` — numeric, 0–1 (musical positivity)
- `danceability` — numeric, 0–1
- `acousticness` — numeric, 0–1
- plus `id`, `title`, `artist` for identification/display only (not used in scoring)

**`UserProfile` features:**

- `favorite_genre` — matched against `Song.genre`
- `favorite_mood` — matched against `Song.mood`
- `target_energy` — matched against `Song.energy` by closeness, not by "higher is better"
- `likes_acoustic` — boolean, matched against `Song.acousticness`

**Algorithm Recipe (finalized):**

| Rule | Points | Formula |
|---|---|---|
| Genre match | +2.0 | `2.0` if `song.genre == user.favorite_genre`, else `0` |
| Mood match | +1.0 | `1.0` if `song.mood == user.favorite_mood`, else `0` |
| Energy similarity | up to +2.0 | `2.0 * (1 - abs(song.energy - user.target_energy))` |
| Acousticness preference | up to +1.0 | `1.0 * song.acousticness` if `user.likes_acoustic`, else `1.0 * (1 - song.acousticness)` |

**Total score** = sum of all four components (max possible: 6.0). Every song in the catalog is scored this way, then sorted descending and sliced to the top `k` to produce the final recommendation list.

**Potential biases to expect:**

- This system might over-prioritize genre, ignoring great songs that match the user's mood but not their exact favorite genre — genre is worth 2x mood, so a song can lose 2 full points for missing genre even if it nails everything else.
- Because genre and mood are exact-match only (no partial credit for "adjacent" genres/moods like indie pop vs. pop, or energetic vs. happy), the recipe can treat two very different non-matching songs identically, understating how different they really are to a real listener.
- Genres and moods that are underrepresented in the catalog (many appear on only one song) have effectively zero chance of scoring well unless they happen to be the user's exact favorite — the system can't discover "close enough" alternatives in thin categories.

You can include a simple diagram or bullet list if helpful.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

User profile: `favorite_genre=pop, favorite_mood=happy, target_energy=0.8, likes_acoustic=False`

```
Loaded songs: 18

Top Recommendations
========================================

1. Sunrise City (by Neon Echo) — Score: 5.78
     - genre 'pop' matches your favorite genre (+2.0)
     - mood 'happy' matches your favorite mood (+1.0)
     - energy 0.82 is close to your target 0.80 (+1.96)
     - non-acoustic sound (0.18) matches your preference (+0.82)

2. Gym Hero (by Max Pulse) — Score: 4.69
     - genre 'pop' matches your favorite genre (+2.0)
     - energy 0.93 is close to your target 0.80 (+1.74)
     - non-acoustic sound (0.05) matches your preference (+0.95)

3. Rooftop Lights (by Indigo Parade) — Score: 3.57
     - mood 'happy' matches your favorite mood (+1.0)
     - energy 0.76 is close to your target 0.80 (+1.92)
     - non-acoustic sound (0.35) matches your preference (+0.65)

4. City Pulse (by Trap Line) — Score: 2.88
     - energy 0.78 is close to your target 0.80 (+1.96)
     - non-acoustic sound (0.08) matches your preference (+0.92)

5. Neon Sunrise (by Pulse Grid) — Score: 2.80
     - energy 0.88 is close to your target 0.80 (+1.84)
     - non-acoustic sound (0.04) matches your preference (+0.96)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



