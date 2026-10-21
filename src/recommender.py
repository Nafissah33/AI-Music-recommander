import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: float = 50.0
    instrumentalness: float = 0.0
    explicit: bool = False

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    prefers_popular: Optional[bool] = None
    prefers_instrumental: Optional[bool] = None
    allow_explicit: bool = True

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py

    Implements the Strategy pattern: pass a `strategy` name (see STRATEGIES
    below) to switch ranking modes without changing this class's code.
    """
    def __init__(self, songs: List[Song], strategy: str = "balanced"):
        self.songs = songs
        self.weights = STRATEGIES[strategy]

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Scores one song against a user profile using the active ranking strategy."""
        return _score_components(
            genre=song.genre,
            mood=song.mood,
            energy=song.energy,
            acousticness=song.acousticness,
            favorite_genre=user.favorite_genre,
            favorite_mood=user.favorite_mood,
            target_energy=user.target_energy,
            likes_acoustic=user.likes_acoustic,
            popularity=song.popularity,
            instrumentalness=song.instrumentalness,
            explicit=song.explicit,
            prefers_popular=user.prefers_popular,
            prefers_instrumental=user.prefers_instrumental,
            allow_explicit=user.allow_explicit,
            weights=self.weights,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Scores every song, then ranks (with a diversity penalty) and returns the top k matches."""
        scored = [(song, *self._score(user, song)) for song in self.songs]
        scored.sort(key=lambda item: item[1], reverse=True)

        diverse = _select_diverse_top_k(
            scored, k, get_artist=lambda s: s.artist, get_genre=lambda s: s.genre
        )
        return [song for song, _, _ in diverse]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of why a song scored the way it did."""
        _, reasons = self._score(user, song)
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file into a list of dicts with numeric/boolean fields converted."""
    numeric_fields = (
        "energy", "tempo_bpm", "valence", "danceability", "acousticness",
        "popularity", "instrumentalness",
    )

    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            for field in numeric_fields:
                row[field] = float(row[field])
            row["explicit"] = row["explicit"] == "True"
            songs.append(row)

    return songs

# Ranking strategies (Strategy pattern): each is an interchangeable set of weights
# for the same scoring algorithm shape. "balanced" is the finalized Algorithm Recipe
# documented in README.md / model_card.md; the others are alternate ranking modes.
STRATEGIES: Dict[str, Dict[str, float]] = {
    "balanced":       {"genre": 2.0, "mood": 1.0, "energy": 2.0, "acoustic": 1.0, "popularity": 1.0, "instrumental": 1.0},
    "genre_first":    {"genre": 4.0, "mood": 1.0, "energy": 1.0, "acoustic": 1.0, "popularity": 1.0, "instrumental": 1.0},
    "mood_first":     {"genre": 1.0, "mood": 4.0, "energy": 1.0, "acoustic": 1.0, "popularity": 1.0, "instrumental": 1.0},
    "energy_focused": {"genre": 1.0, "mood": 1.0, "energy": 4.0, "acoustic": 1.0, "popularity": 1.0, "instrumental": 1.0},
}
EXPLICIT_PENALTY = 2.0
DEFAULT_STRATEGY = "balanced"

def _score_components(
    genre: str,
    mood: str,
    energy: float,
    acousticness: float,
    favorite_genre: str,
    favorite_mood: str,
    target_energy: float,
    likes_acoustic: bool,
    popularity: float = 50.0,
    instrumentalness: float = 0.0,
    explicit: bool = False,
    prefers_popular: Optional[bool] = None,
    prefers_instrumental: Optional[bool] = None,
    allow_explicit: bool = True,
    weights: Optional[Dict[str, float]] = None,
) -> Tuple[float, List[str]]:
    """Applies a ranking strategy's weights (genre/mood/energy/acoustic/popularity/instrumentalness match) shared by both scoring paths."""
    weights = weights or STRATEGIES[DEFAULT_STRATEGY]
    reasons = []
    score = 0.0

    if genre == favorite_genre:
        score += weights["genre"]
        reasons.append(f"genre '{genre}' matches your favorite genre (+{weights['genre']:.1f})")

    if mood == favorite_mood:
        score += weights["mood"]
        reasons.append(f"mood '{mood}' matches your favorite mood (+{weights['mood']:.1f})")

    energy_points = weights["energy"] * (1 - abs(energy - target_energy))
    score += energy_points
    reasons.append(
        f"energy {energy:.2f} is close to your target {target_energy:.2f} (+{energy_points:.2f})"
    )

    if likes_acoustic:
        acoustic_points = weights["acoustic"] * acousticness
        reasons.append(f"acoustic sound ({acousticness:.2f}) matches your preference (+{acoustic_points:.2f})")
    else:
        acoustic_points = weights["acoustic"] * (1 - acousticness)
        reasons.append(f"non-acoustic sound ({acousticness:.2f}) matches your preference (+{acoustic_points:.2f})")
    score += acoustic_points

    # prefers_popular/prefers_instrumental are tri-state (True/False/None) on purpose:
    # None means "no preference stated," and contributes nothing, rather than
    # silently defaulting every unset profile toward one extreme (the same binary-
    # preference bias we found earlier with acousticness/likes_acoustic).
    if prefers_popular is not None:
        popularity_weight = weights.get("popularity", 1.0)
        popularity_ratio = popularity / 100
        if prefers_popular:
            popularity_points = popularity_weight * popularity_ratio
            reasons.append(f"popularity {popularity:.0f}/100 matches your mainstream preference (+{popularity_points:.2f})")
        else:
            popularity_points = popularity_weight * (1 - popularity_ratio)
            reasons.append(f"popularity {popularity:.0f}/100 matches your discovery preference (+{popularity_points:.2f})")
        score += popularity_points

    if prefers_instrumental is not None:
        instrumental_weight = weights.get("instrumental", 1.0)
        if prefers_instrumental:
            instrumental_points = instrumental_weight * instrumentalness
            reasons.append(f"instrumentalness {instrumentalness:.2f} matches your instrumental preference (+{instrumental_points:.2f})")
        else:
            instrumental_points = instrumental_weight * (1 - instrumentalness)
            reasons.append(f"instrumentalness {instrumentalness:.2f} matches your vocal preference (+{instrumental_points:.2f})")
        score += instrumental_points

    if explicit and not allow_explicit:
        score -= EXPLICIT_PENALTY
        reasons.append(f"explicit content penalty since you don't allow explicit songs (-{EXPLICIT_PENALTY:.1f})")

    return score, reasons

# Diversity Penalty: discourages the Ranking Rule from stacking the top-k with
# repeats of the same artist/genre. Lives entirely in ranking, not in score_song,
# since a single song's score can't know what else has already been picked.
ARTIST_PENALTY = 1.5
GENRE_PENALTY = 0.5

def _select_diverse_top_k(
    candidates: List[Tuple[object, float, List[str]]],
    k: int,
    get_artist,
    get_genre,
) -> List[Tuple[object, float, List[str]]]:
    """
    Greedily picks k songs one at a time. Before each pick, every remaining
    candidate's score is reduced by ARTIST_PENALTY for each already-selected
    song sharing its artist, and GENRE_PENALTY for each sharing its genre —
    recomputed every step, so repeats are penalized more each time they recur.
    """
    remaining = list(candidates)
    selected = []
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}

    while remaining and len(selected) < k:
        best_index = None
        best_adjusted_score = None
        best_penalty_note = None

        for i, (song, base_score, reasons) in enumerate(remaining):
            artist_repeats = artist_counts.get(get_artist(song), 0)
            genre_repeats = genre_counts.get(get_genre(song), 0)
            penalty = ARTIST_PENALTY * artist_repeats + GENRE_PENALTY * genre_repeats
            adjusted_score = base_score - penalty

            if best_adjusted_score is None or adjusted_score > best_adjusted_score:
                best_index = i
                best_adjusted_score = adjusted_score
                best_penalty_note = (
                    f"diversity penalty -{penalty:.1f} ({artist_repeats} same artist, {genre_repeats} same genre already picked)"
                    if penalty > 0 else None
                )

        song, base_score, reasons = remaining.pop(best_index)
        final_reasons = reasons + [best_penalty_note] if best_penalty_note else reasons
        selected.append((song, best_adjusted_score, final_reasons))

        artist_counts[get_artist(song)] = artist_counts.get(get_artist(song), 0) + 1
        genre_counts[get_genre(song)] = genre_counts.get(get_genre(song), 0) + 1

    return selected

def score_song(user_prefs: Dict, song: Dict, weights: Optional[Dict[str, float]] = None) -> Tuple[float, List[str]]:
    """Scores a single song dict against a user_prefs dict, returning (score, reasons)."""
    return _score_components(
        genre=song["genre"],
        mood=song["mood"],
        energy=song["energy"],
        acousticness=song["acousticness"],
        favorite_genre=user_prefs["favorite_genre"],
        favorite_mood=user_prefs["favorite_mood"],
        target_energy=user_prefs["target_energy"],
        likes_acoustic=user_prefs["likes_acoustic"],
        # New attributes (Challenge 1) are optional extensions: default gracefully
        # via .get() instead of requiring every existing user_prefs dict to be updated.
        popularity=song.get("popularity", 50.0),
        instrumentalness=song.get("instrumentalness", 0.0),
        explicit=song.get("explicit", False),
        prefers_popular=user_prefs.get("prefers_popular"),
        prefers_instrumental=user_prefs.get("prefers_instrumental"),
        allow_explicit=user_prefs.get("allow_explicit", True),
        weights=weights,
    )

def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5, weights: Optional[Dict[str, float]] = None
) -> List[Tuple[Dict, float, str]]:
    """Scores every song under the given ranking strategy, then ranks (with a diversity penalty) and returns the top k."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights=weights)
        scored.append((song, score, reasons))

    scored.sort(key=lambda item: item[1], reverse=True)

    diverse = _select_diverse_top_k(
        scored, k, get_artist=lambda s: s["artist"], get_genre=lambda s: s["genre"]
    )
    return [(song, final_score, "; ".join(reasons)) for song, final_score, reasons in diverse]
