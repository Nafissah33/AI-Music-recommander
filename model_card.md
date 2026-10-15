# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

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

**What surprised me:**

- The **case-sensitivity trap** was the most concerning result: typing `"Pop"`/`"Happy"` instead of `"pop"`/`"happy"` silently zeroed out both the genre and mood rules for every song, with no error. The top result (City Pulse, hip hop) isn't even a pop song — it only won on energy+acoustic by default, and the system gave no indication that two of its four rules had silently stopped working.
- The **conflicting-preferences** profile (wanting metal energy *and* a relaxed mood *and* acoustic sound) resolved by just ignoring the two lower-weighted rules — Iron Fury won despite failing both mood and acoustic, which exposes that genre+energy (max 4.0 combined) will always dominate mood+acoustic (max 2.0 combined) whenever preferences contradict each other.
- The **out-of-range `target_energy`** values (1.5 and -0.5) didn't crash, but the negative case let the energy component go below zero, breaking the "up to +2.0" ceiling documented in the Algorithm Recipe — there's no input validation clamping `target_energy` to its intended `[0, 1]` range.
- A profile missing the `likes_acoustic` key raised an unhandled `KeyError` — there's no validation or friendly error message for malformed `user_prefs` dicts.

These are documented further in the Limitations and Bias section below.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
