import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import Optional


def normalize_scores(scores: list[float]) -> list[float]:
    if not scores:
        return []
    arr = np.array(scores)
    min_val = arr.min()
    max_val = arr.max()
    if max_val == min_val:
        return [1.0] * len(scores)
    normalized = (arr - min_val) / (max_val - min_val)
    return normalized.tolist()


def compute_confidence(score: float, rating_count: int, min_ratings: int = 5) -> float:
    bayesian_factor = min_ratings / (min_ratings + rating_count)
    global_avg = 3.5
    confidence = (score * (1 - bayesian_factor)) + (global_avg * bayesian_factor)
    return round(min(max(confidence / 5.0, 0.0), 1.0), 3)


def compute_similarity_pct(score: float, max_score: float = 1.0) -> float:
    return round(min(score / max_score * 100, 100.0), 1) if max_score > 0 else 0.0


def generate_reason(algorithm: str, context: dict) -> str:
    reasons = {
        "popularity": "Trending and popular among all users",
        "content_based": f"Similar to your preference for {context.get('genre', 'this genre')}",
        "collaborative": "Users with similar taste also enjoyed this",
        "matrix_factorization": "Based on your latent preferences",
        "hybrid": f"Recommended combining your taste ({context.get('genre', 'genre')} preference) and community trends",
    }
    return reasons.get(algorithm, "Recommended for you")


def create_interaction_weight(interaction_type: str, duration: int = 0) -> float:
    weights = {
        "view": 1.0,
        "click": 1.5,
        "like": 2.0,
        "add_to_cart": 2.5,
        "purchase": 3.0,
        "rate": 2.0,
        "share": 2.0,
        "bookmark": 2.0,
        "watch": 1.5,
        "complete": 3.0,
    }
    base = weights.get(interaction_type, 1.0)
    if duration > 300:
        base *= 1.5
    elif duration > 60:
        base *= 1.2
    return round(base, 2)
