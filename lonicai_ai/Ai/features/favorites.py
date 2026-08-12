from pathlib import Path
import json


# ==========================================
# FAVORITES STORAGE
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[1]

FAVORITES_FILE = BASE_DIR / "favorites.json"


# ==========================================
# LOAD FAVORITES
# ==========================================

def load_favorites():
    if not FAVORITES_FILE.exists():
        return []

    try:
        with open(
            FAVORITES_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        if isinstance(data, dict):
            favorites = data.get("favorites", [])

            if isinstance(favorites, list):
                return favorites

    except Exception as e:
        print(f"WARNING: Could not load favorites: {e}")

    return []


# ==========================================
# SAVE FAVORITES
# ==========================================

def save_favorites(favorites):
    with open(
        FAVORITES_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            {
                "favorites": favorites,
            },
            f,
            indent=4,
        )


# ==========================================
# GET FAVORITES
# ==========================================

def get_favorites():
    return load_favorites()


# ==========================================
# ADD FAVORITE
# ==========================================

def add_favorite(food):
    food = str(food).strip()

    if not food:
        raise ValueError(
            "Food name cannot be empty."
        )

    favorites = load_favorites()

    # Don't save duplicates.
    if food not in favorites:
        favorites.append(food)
        favorites.sort(
            key=str.lower
        )
        save_favorites(favorites)

    return {
        "success": True,
        "food": food,
        "favorited": True,
        "favorites": favorites,
    }


# ==========================================
# REMOVE FAVORITE
# ==========================================

def remove_favorite(food):
    food = str(food).strip()

    favorites = load_favorites()

    if food in favorites:
        favorites.remove(food)
        save_favorites(favorites)

    return {
        "success": True,
        "food": food,
        "favorited": False,
        "favorites": favorites,
    }


# ==========================================
# CHECK FAVORITE
# ==========================================

def is_favorite(food):
    food = str(food).strip()

    favorites = load_favorites()

    return food in favorites