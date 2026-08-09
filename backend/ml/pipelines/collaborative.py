import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
from typing import Optional
import pickle


class CollaborativeRecommender:
    def __init__(self):
        self.name = "collaborative"
        self.is_trained = False
        self.model = None
        self.user_item_matrix = None
        self.user_mapper = {}
        self.item_mapper = {}
        self.reverse_user_mapper = {}
        self.reverse_item_mapper = {}
        self.items_df = None

    def train(self, ratings_df: pd.DataFrame, items_df: pd.DataFrame, interactions_df: Optional[pd.DataFrame] = None):
        self.items_df = items_df.copy()

        if ratings_df is not None and len(ratings_df) > 0:
            df = ratings_df.copy()
        elif interactions_df is not None and len(interactions_df) > 0:
            df = interactions_df.copy()
            if "weight" in df.columns:
                df = df.rename(columns={"weight": "rating"})
            else:
                df["rating"] = 1.0
        else:
            self.is_trained = False
            return

        users = df["user_id"].unique()
        items = df["item_id"].unique()
        self.user_mapper = {u: i for i, u in enumerate(users)}
        self.item_mapper = {it: i for i, it in enumerate(items)}
        self.reverse_user_mapper = {i: u for u, i in self.user_mapper.items()}
        self.reverse_item_mapper = {i: it for it, i in self.item_mapper.items()}

        rows = df["user_id"].map(self.user_mapper).values
        cols = df["item_id"].map(self.item_mapper).values
        vals = df["rating"].values.astype(float)

        self.user_item_matrix = csr_matrix((vals, (rows, cols)), shape=(len(users), len(items)))

        self.model = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=min(20, len(users)))
        self.model.fit(self.user_item_matrix)
        self.is_trained = True

    def recommend(self, user_id: int, limit: int = 20, exclude_ids: Optional[list[int]] = None) -> list[dict]:
        if not self.is_trained or user_id not in self.user_mapper:
            return self._fallback_recommendations(limit, exclude_ids)

        user_idx = self.user_mapper[user_id]
        user_vector = self.user_item_matrix[user_idx]

        n_neighbors = min(10, self.user_item_matrix.shape[0] - 1)
        distances, indices = self.model.kneighbors(user_vector, n_neighbors=n_neighbors + 1)

        neighbor_distances = distances[0][1:]
        neighbor_indices = indices[0][1:]
        similarity_scores = 1 - neighbor_distances

        item_scores = {}
        item_weights = {}

        for n_idx, sim in zip(neighbor_indices, similarity_scores):
            neighbor_items = self.user_item_matrix[n_idx].toarray().flatten()
            for item_local_idx, rating in enumerate(neighbor_items):
                if rating > 0:
                    original_item_id = self.reverse_item_mapper.get(item_local_idx)
                    if original_item_id and (not exclude_ids or original_item_id not in exclude_ids):
                        item_scores[original_item_id] = item_scores.get(original_item_id, 0) + rating * sim
                        item_weights[original_item_id] = item_weights.get(original_item_id, 0) + sim

        for item_id in item_scores:
            if item_weights[item_id] > 0:
                item_scores[item_id] /= item_weights[item_id]

        sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)[:limit]

        recommendations = []
        for item_id, score in sorted_items:
            item_info = self.items_df[self.items_df["item_id"] == item_id]
            if len(item_info) == 0:
                continue
            row = item_info.iloc[0]
            normalized_score = min(score / 5.0, 1.0)
            recommendations.append({
                "item_id": int(item_id),
                "title": row["title"],
                "image_url": row.get("image_url"),
                "category": row.get("category"),
                "genres": row.get("genres"),
                "avg_rating": float(row.get("avg_rating", 0)),
                "score": round(normalized_score, 4),
                "confidence": round(min(normalized_score * 0.85, 0.95), 3),
                "reason": "Users with similar taste also enjoyed this",
                "similarity_pct": round(min(normalized_score * 100, 99.9), 1),
                "algorithm": "collaborative",
            })
        return recommendations

    def _fallback_recommendations(self, limit: int, exclude_ids: Optional[list[int]]) -> list[dict]:
        if self.items_df is None:
            return []
        df = self.items_df.copy()
        if exclude_ids:
            df = df[~df["item_id"].isin(exclude_ids)]
        top = df.nlargest(limit, "avg_rating")
        return [
            {
                "item_id": int(row["item_id"]),
                "title": row["title"],
                "image_url": row.get("image_url"),
                "category": row.get("category"),
                "genres": row.get("genres"),
                "avg_rating": float(row.get("avg_rating", 0)),
                "score": 0.5,
                "confidence": 0.5,
                "reason": "Popular items you might like",
                "similarity_pct": 50.0,
                "algorithm": "collaborative",
            }
            for _, row in top.iterrows()
        ]

    def save(self, path: str):
        data = {
            "model": self.model, "user_item_matrix": self.user_item_matrix,
            "user_mapper": self.user_mapper, "item_mapper": self.item_mapper,
            "reverse_user_mapper": self.reverse_user_mapper,
            "reverse_item_mapper": self.reverse_item_mapper,
            "items_df": self.items_df,
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.model = data["model"]
        self.user_item_matrix = data["user_item_matrix"]
        self.user_mapper = data["user_mapper"]
        self.item_mapper = data["item_mapper"]
        self.reverse_user_mapper = data["reverse_user_mapper"]
        self.reverse_item_mapper = data["reverse_item_mapper"]
        self.items_df = data["items_df"]
        self.is_trained = True
