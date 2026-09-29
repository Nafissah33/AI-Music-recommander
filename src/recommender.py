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

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Scores one song against a user profile using the shared Algorithm Recipe."""
        return _score_components(
            genre=song.genre,
            mood=song.mood,
            energy=song.energy,
            acousticness=song.acousticness,
            favorite_genre=user.favorite_genre,
            favorite_mood=user.favorite_mood,
            target_energy=user.target_energy,
            likes_acoustic=user.likes_acoustic,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Scores every song, then ranks and returns the top k matches."""
        scored = [(song, self._score(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of why a song scored the way it did."""
        _, reasons = self._score(user, song)
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file into a list of dicts with numeric fields converted."""
    numeric_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")

    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            for field in numeric_fields:
                row[field] = float(row[field])
            songs.append(row)

    return songs

def _score_components(
    genre: str,
    mood: str,
    energy: float,
    acousticness: float,
    favorite_genre: str,
    favorite_mood: str,
    target_energy: float,
    likes_acoustic: bool,
) -> Tuple[float, List[str]]:
    """Applies the Algorithm Recipe (genre +2.0, mood +1.0, energy up to +2.0, acoustic up to +1.0) shared by both scoring paths."""
    reasons = []
    score = 0.0

    if genre == favorite_genre:
        score += 2.0
        reasons.append(f"genre '{genre}' matches your favorite genre (+2.0)")

    if mood == favorite_mood:
        score += 1.0
        reasons.append(f"mood '{mood}' matches your favorite mood (+1.0)")

    energy_points = 2.0 * (1 - abs(energy - target_energy))
    score += energy_points
    reasons.append(
        f"energy {energy:.2f} is close to your target {target_energy:.2f} (+{energy_points:.2f})"
    )

    if likes_acoustic:
        acoustic_points = 1.0 * acousticness
        reasons.append(f"acoustic sound ({acousticness:.2f}) matches your preference (+{acoustic_points:.2f})")
    else:
        acoustic_points = 1.0 * (1 - acousticness)
        reasons.append(f"non-acoustic sound ({acousticness:.2f}) matches your preference (+{acoustic_points:.2f})")
    score += acoustic_points

    return score, reasons

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
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
    )

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song, then ranks and returns the top k as (song, score, explanation) tuples."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
