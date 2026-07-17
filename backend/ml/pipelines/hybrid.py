import pandas as pd
import numpy as np
from typing import Optional, Dict
from ml.pipelines.popularity import PopularityRecommender
from ml.pipelines.content_based import ContentBasedRecommender
from ml.pipelines.collaborative import CollaborativeRecommender
from ml.pipelines.matrix_factorization import MatrixFactorizationRecommender


class HybridRecommender:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.name = "hybrid"
        self.is_trained = False
        self.popularity = PopularityRecommender()
        self.content_based = ContentBasedRecommender()
        self.collaborative = CollaborativeRecommender()
        self.matrix_factorization = MatrixFactorizationRecommender()
        self.weights = weights or {
            "popularity": 0.15,
            "content_based": 0.30,
            "collaborative": 0.30,
            "matrix_factorization": 0.25,
        }

    def train(self, items_df: pd.DataFrame, ratings_df: pd.DataFrame, interactions_df: Optional[pd.DataFrame] = None):
        print("Training Popularity model...")
        self.popularity.train(items_df, interactions_df)

        print("Training Content-Based model...")
        self.content_based.train(items_df, ratings_df)

        print("Training Collaborative Filtering model...")
        self.collaborative.train(ratings_df, items_df, interactions_df)

        print("Training Matrix Factorization model...")
        self.matrix_factorization.train(ratings_df, items_df)

        self.is_trained = True
        print("Hybrid model training complete!")

    def recommend(self, user_id: int, limit: int = 20, exclude_ids: Optional[list[int]] = None) -> list[dict]:
        if not self.is_trained:
            return []

        n_candidates = limit * 3

        recs_pop = self.popularity.recommend(user_id, n_candidates, exclude_ids)
        recs_cb = self.content_based.recommend(user_id, n_candidates, exclude_ids)
        recs_cf = self.collaborative.recommend(user_id, n_candidates, exclude_ids)
        recs_mf = self.matrix_factorization.recommend(user_id, n_candidates, exclude_ids)

        all_recs = {
            "popularity": {r["item_id"]: r for r in recs_pop},
            "content_based": {r["item_id"]: r for r in recs_cb},
            "collaborative": {r["item_id"]: r for r in recs_cf},
            "matrix_factorization": {r["item_id"]: r for r in recs_mf},
        }

        all_item_ids = set()
        for algo_recs in all_recs.values():
            all_item_ids.update(algo_recs.keys())

        item_final_scores = {}
        for item_id in all_item_ids:
            weighted_score = 0
            weight_sum = 0
            present_algos = []

            for algo_name, algo_weight in self.weights.items():
                if item_id in all_recs.get(algo_name, {}):
                    score = all_recs[algo_name][item_id]["score"]
                    weighted_score += score * algo_weight
                    weight_sum += algo_weight
                    present_algos.append(algo_name)

            if weight_sum > 0:
                final_score = weighted_score / weight_sum
            else:
                final_score = 0

            reasons = []
            for algo in present_algos:
                if algo == "content_based":
                    reasons.append("matches your taste")
                elif algo == "collaborative":
                    reasons.append("liked by similar users")
                elif algo == "popularity":
                    reasons.append("trending now")
                elif algo == "matrix_factorization":
                    reasons.append("based on your preferences")

            best_recs = {}
            for algo in present_algos:
                if item_id in all_recs.get(algo, {}):
                    best_recs = all_recs[algo][item_id]
                    break

            genre = best_recs.get("genres", "various")
            reason = f"Recommended because it {' and '.join(reasons)}" if reasons else "Recommended for you"

            item_final_scores[item_id] = {
                "item_id": int(item_id),
                "title": best_recs.get("title", ""),
                "image_url": best_recs.get("image_url"),
                "category": best_recs.get("category"),
                "genres": best_recs.get("genres"),
                "avg_rating": best_recs.get("avg_rating", 0),
                "score": round(final_score, 4),
                "confidence": round(min(final_score * 0.9, 0.95), 3),
                "reason": reason,
                "similarity_pct": round(min(final_score * 100, 99.9), 1),
                "algorithm": "hybrid",
                "contributing_algorithms": present_algos,
            }

        sorted_items = sorted(item_final_scores.values(), key=lambda x: x["score"], reverse=True)[:limit]
        return sorted_items

    def get_all_user_recommendations(self, user_id: int, limit: int = 10, exclude_ids: Optional[list[int]] = None) -> dict:
        return {
            "popularity": self.popularity.recommend(user_id, limit, exclude_ids),
            "content_based": self.content_based.recommend(user_id, limit, exclude_ids),
            "collaborative": self.collaborative.recommend(user_id, limit, exclude_ids),
            "matrix_factorization": self.matrix_factorization.recommend(user_id, limit, exclude_ids),
            "hybrid": self.recommend(user_id, limit, exclude_ids),
        }
