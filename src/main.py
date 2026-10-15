"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from tabulate import tabulate

try:
    from src.recommender import load_songs, recommend_songs, STRATEGIES
except ImportError:
    from recommender import load_songs, recommend_songs, STRATEGIES


# Change this to switch ranking modes: "balanced", "genre_first", "mood_first", or "energy_focused"
ACTIVE_STRATEGY = "balanced"


# Distinct user preference dictionaries for trying out different personas
USER_PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "intense",
        "target_energy": 0.9,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.9,
        "likes_acoustic": False,
    },
}


def print_recommendations(user_prefs: dict, songs: list, k: int = 5, weights: dict = None) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=k, weights=weights)

    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = "\n".join(f"- {reason}" for reason in explanation.split("; "))
        rows.append([rank, song["title"], song["artist"], f"{score:.2f}", reasons])

    print(tabulate(rows, headers=["#", "Title", "Artist", "Score", "Reasons"], tablefmt="fancy_grid"))


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    active_weights = STRATEGIES[ACTIVE_STRATEGY]
    for name, user_prefs in USER_PROFILES.items():
        print(f"\n\nTop Recommendations — {name}  [strategy: {ACTIVE_STRATEGY}]")
        print("=" * 40)
        print_recommendations(user_prefs, songs, k=5, weights=active_weights)

    # Demo: run one profile through every ranking strategy to show how mode-switching changes results
    demo_profile = USER_PROFILES["High-Energy Pop"]
    print("\n\nStrategy comparison for 'High-Energy Pop'")
    print("=" * 40)
    for strategy_name, weights in STRATEGIES.items():
        print(f"\n--- {strategy_name} ---")
        top3 = recommend_songs(demo_profile, songs, k=3, weights=weights)
        for rank, (song, score, _) in enumerate(top3, start=1):
            print(f"  {rank}. {song['title']:20} score={score:.2f}")


if __name__ == "__main__":
    main()
