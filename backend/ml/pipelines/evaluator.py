import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.metrics import precision_score, recall_score


class RecommendationEvaluator:
    @staticmethod
    def precision_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
        if k == 0:
            return 0.0
        recommended_k = recommended[:k]
        hits = len(set(recommended_k) & set(relevant))
        return hits / k

    @staticmethod
    def recall_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
        if not relevant:
            return 0.0
        recommended_k = recommended[:k]
        hits = len(set(recommended_k) & set(relevant))
        return hits / len(relevant)

    @staticmethod
    def ndcg_at_k(recommended: List[int], relevant: List[int], k: int) -> float:
        if not relevant or k == 0:
            return 0.0

        dcg = 0.0
        for i, item in enumerate(recommended[:k]):
            if item in relevant:
                dcg += 1.0 / np.log2(i + 2)

        ideal_rels = np.ones(min(len(relevant), k))
        idcg = sum(1.0 / np.log2(i + 2) for i in range(len(ideal_rels)))

        return dcg / idcg if idcg > 0 else 0.0

    @staticmethod
    def average_precision(recommended: List[int], relevant: List[int], k: int) -> float:
        if not relevant:
            return 0.0
        score = 0.0
        num_hits = 0.0
        for i, item in enumerate(recommended[:k]):
            if item in relevant:
                num_hits += 1.0
                score += num_hits / (i + 1.0)
        return score / min(len(relevant), k)

    @staticmethod
    def map_at_k(all_recommendations: List[List[int]], all_relevant: List[List[int]], k: int) -> float:
        aps = []
        for recs, rels in zip(all_recommendations, all_relevant):
            ap = RecommendationEvaluator.average_precision(recs, rels, k)
            aps.append(ap)
        return np.mean(aps) if aps else 0.0

    @staticmethod
    def evaluate_model(recommendations_fn, test_users: List[int], test_ratings_df: pd.DataFrame, k: int = 10, rating_threshold: float = 3.5) -> Dict:
        all_precisions = []
        all_recalls = []
        all_ndcgs = []
        all_aps = []

        for user_id in test_users:
            user_relevant = test_ratings_df[
                (test_ratings_df["user_id"] == user_id) & (test_ratings_df["rating"] >= rating_threshold)
            ]["item_id"].tolist()

            if not user_relevant:
                continue

            recs = recommendations_fn(user_id, limit=k)
            rec_ids = [r["item_id"] for r in recs]

            all_precisions.append(RecommendationEvaluator.precision_at_k(rec_ids, user_relevant, k))
            all_recalls.append(RecommendationEvaluator.recall_at_k(rec_ids, user_relevant, k))
            all_ndcgs.append(RecommendationEvaluator.ndcg_at_k(rec_ids, user_relevant, k))
            all_aps.append(RecommendationEvaluator.average_precision(rec_ids, user_relevant, k))

        return {
            f"precision_at_{k}": round(np.mean(all_precisions), 4) if all_precisions else 0,
            f"recall_at_{k}": round(np.mean(all_recalls), 4) if all_recalls else 0,
            f"ndcg_at_{k}": round(np.mean(all_ndcgs), 4) if all_ndcgs else 0,
            f"map_at_{k}": round(np.mean(all_aps), 4) if all_aps else 0,
            "test_users_evaluated": len(all_precisions),
        }

    @staticmethod
    def rmse(predictions: List[float], actuals: List[float]) -> float:
        return float(np.sqrt(np.mean([(p - a) ** 2 for p, a in zip(predictions, actuals)])))

    @staticmethod
    def mae(predictions: List[float], actuals: List[float]) -> float:
        return float(np.mean([abs(p - a) for p, a in zip(predictions, actuals)]))
