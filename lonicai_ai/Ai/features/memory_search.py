from pathlib import Path
import pickle

import torch


# ==========================================
# MEMORY LOCATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

MEMORY_FILE = BASE_DIR / "memory.pkl"


# ==========================================
# SETTINGS
# ==========================================

MAX_EXAMPLES_PER_FOOD = 30

# Strong visual match required.
MEMORY_THRESHOLD = 0.78

# Number of closest examples to inspect.
TOP_K = 8


# ==========================================
# LOAD MEMORY
# ==========================================

def load_memory():

    if not MEMORY_FILE.exists():
        return []

    try:

        with open(MEMORY_FILE, "rb") as f:
            data = pickle.load(f)

        if isinstance(data, list):
            return data

    except Exception as e:

        print(
            f"WARNING: Could not load memory: {e}"
        )

    return []


memory = load_memory()


# ==========================================
# SAVE MEMORY
# ==========================================

def save_memory():

    global memory

    with open(MEMORY_FILE, "wb") as f:
        pickle.dump(memory, f)

    print(
        f"Memory saved: {len(memory)} samples"
    )


# ==========================================
# NORMALIZE EMBEDDING
# ==========================================

def normalize_embedding(embedding):

    if not isinstance(
        embedding,
        torch.Tensor,
    ):

        embedding = torch.tensor(
            embedding
        )

    embedding = (
        embedding
        .detach()
        .cpu()
        .float()
    )

    norm = embedding.norm(
        dim=-1,
        keepdim=True,
    )

    if torch.all(norm == 0):
        return embedding

    return embedding / norm


# ==========================================
# ADD MEMORY
# ==========================================

def add_memory(
    embedding,
    label,
    rejected_prediction=None,
):

    global memory

    label = str(label).strip()

    if not label:

        raise ValueError(
            "Cannot save memory without a label."
        )

    embedding = normalize_embedding(
        embedding
    )

    # --------------------------------------
    # CREATE MEMORY ITEM
    # --------------------------------------

    item = {
        "embedding": embedding,
        "label": label,
    }

    # --------------------------------------
    # REMEMBER WHAT CLIP GOT WRONG
    # --------------------------------------

    if rejected_prediction:

        rejected_prediction = str(
            rejected_prediction
        ).strip()

        if rejected_prediction:

            item["rejected_prediction"] = (
                rejected_prediction
            )

    memory.append(item)

    # --------------------------------------
    # LIMIT EXAMPLES PER FOOD
    # --------------------------------------

    food_items = [
        x
        for x in memory
        if x.get("label") == label
    ]

    if len(food_items) > MAX_EXAMPLES_PER_FOOD:

        memory = [
            x
            for x in memory
            if x.get("label") != label
        ]

        memory.extend(
            food_items[-MAX_EXAMPLES_PER_FOOD:]
        )

    # --------------------------------------
    # SAVE
    # --------------------------------------

    save_memory()

    print()
    print("==========================================")
    print("MEMORY LEARNED")
    print("==========================================")
    print(f"Correct food: {label}")

    if rejected_prediction:

        print(
            f"Previous prediction: "
            f"{rejected_prediction}"
        )

    print(
        f"Examples for {label}: "
        f"{sum(1 for x in memory if x.get('label') == label)}"
    )

    print(
        f"Total memory samples: {len(memory)}"
    )

    print("Embedding: saved")
    print("==========================================")
    print()

    return {
        "success": True,
        "label": label,
        "rejected_prediction": (
            rejected_prediction
        ),
        "memory_size": len(memory),
    }


# ==========================================
# SEARCH MEMORY
# ==========================================

def search_memory(
    image_embedding,
    threshold=MEMORY_THRESHOLD,
):

    if not memory:
        return None

    image_embedding = normalize_embedding(
        image_embedding
    )

    candidates = []

    # ======================================
    # COMPARE IMAGE AGAINST LEARNED IMAGES
    # ======================================

    for item in memory:

        if "embedding" not in item:
            continue

        if "label" not in item:
            continue

        stored_embedding = normalize_embedding(
            item["embedding"]
        )

        similarity = (
            image_embedding
            @ stored_embedding.T
        ).item()

        candidates.append(
            {
                "label": item["label"],
                "score": similarity,
                "rejected_prediction": item.get(
                    "rejected_prediction"
                ),
            }
        )

    if not candidates:
        return None

    # ======================================
    # SORT BY VISUAL SIMILARITY
    # ======================================

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    top_matches = candidates[:TOP_K]

    # ======================================
    # GROUP BY CORRECT FOOD
    # ======================================

    label_scores = {}

    for match in top_matches:

        label = match["label"]

        if label not in label_scores:

            label_scores[label] = []

        label_scores[label].append(
            match
        )

    # ======================================
    # SCORE EACH FOOD
    # ======================================

    ranked_labels = []

    for label, matches in label_scores.items():

        matches.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        scores = [
            x["score"]
            for x in matches
        ]

        # ----------------------------------
        # WEIGHT STRONGEST MATCHES
        # ----------------------------------

        if len(scores) == 1:

            group_score = scores[0]

        elif len(scores) == 2:

            group_score = (
                scores[0] * 0.70
                + scores[1] * 0.30
            )

        else:

            group_score = (
                scores[0] * 0.60
                + scores[1] * 0.25
                + scores[2] * 0.15
            )

        ranked_labels.append(
            {
                "label": label,
                "score": group_score,
                "matches": len(matches),
                "best_match": scores[0],
                "matches_data": matches,
            }
        )

    # ======================================
    # BEST FOOD
    # ======================================

    ranked_labels.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    best = ranked_labels[0]

    # ======================================
    # THRESHOLD
    # ======================================

    if best["score"] < threshold:

        return None

    # ======================================
    # FIND ORIGINAL WRONG PREDICTION
    # ======================================

    rejected_predictions = []

    for match in best["matches_data"]:

        rejected = match.get(
            "rejected_prediction"
        )

        if rejected:
            rejected_predictions.append(
                rejected
            )

    # ======================================
    # RETURN LEARNED RESULT
    # ======================================

    return {
        "food": best["label"],

        "confidence": round(
            best["score"] * 100,
            2,
        ),

        "matches": best["matches"],

        "best_match": round(
            best["best_match"] * 100,
            2,
        ),

        "learned": True,

        "rejected_predictions": (
            list(
                dict.fromkeys(
                    rejected_predictions
                )
            )
        ),
    }