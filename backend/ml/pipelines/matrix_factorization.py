import pandas as pd
import numpy as np
from typing import Optional
from scipy.sparse import csr_matrix
import pickle


class MatrixFactorizationRecommender:
    def __init__(self, n_factors: int = 50, n_iterations: int = 20, learning_rate: float = 0.005, regularization: float = 0.02):
        self.name = "matrix_factorization"
        self.is_trained = False
        self.n_factors = n_factors
        self.n_iterations = n_iterations
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.user_factors = None
        self.item_factors = None
        self.user_bias = None
        self.item_bias = None
        self.global_mean = 0
        self.user_mapper = {}
        self.item_mapper = {}
        self.reverse_user_mapper = {}
        self.reverse_item_mapper = {}
        self.items_df = None

    def train(self, ratings_df: pd.DataFrame, items_df: pd.DataFrame):
        self.items_df = items_df.copy()
        df = ratings_df.copy()

        users = df["user_id"].unique()
        items = df["item_id"].unique()
        self.user_mapper = {u: i for i, u in enumerate(users)}
        self.item_mapper = {it: i for i, it in enumerate(items)}
        self.reverse_user_mapper = {i: u for u, i in self.user_mapper.items()}
        self.reverse_item_mapper = {i: it for it, i in self.item_mapper.items()}

        n_users = len(users)
        n_items = len(items)

        self.global_mean = df["rating"].mean()
        self.user_bias = np.zeros(n_users)
        self.item_bias = np.zeros(n_items)

        scale = 1.0 / np.sqrt(self.n_factors)
        self.user_factors = np.random.normal(0, scale, (n_users, self.n_factors))
        self.item_factors = np.random.normal(0, scale, (n_items, self.n_factors))

        rows = df["user_id"].map(self.user_mapper).values
        cols = df["item_id"].map(self.item_mapper).values
        ratings = df["rating"].values

        for iteration in range(self.n_iterations):
            np.random.seed(iteration)
            indices = np.arange(len(df))
            np.random.shuffle(indices)

            total_loss = 0
            for idx in indices:
                u = rows[idx]
                i = cols[idx]
                r = ratings[idx]

                pred = self.global_mean + self.user_bias[u] + self.item_bias[i] + np.dot(self.user_factors[u], self.item_factors[i])
                error = r - pred
                total_loss += error ** 2

                self.user_bias[u] += self.learning_rate * (error - self.regularization * self.user_bias[u])
                self.item_bias[i] += self.learning_rate * (error - self.regularization * self.item_bias[i])

                user_factor_old = self.user_factors[u].copy()
                self.user_factors[u] += self.learning_rate * (error * self.item_factors[i] - self.regularization * self.user_factors[u])
                self.item_factors[i] += self.learning_rate * (error * user_factor_old - self.regularization * self.item_factors[i])

            rmse = np.sqrt(total_loss / len(df))
            if (iteration + 1) % 5 == 0:
                print(f"  MF Iteration {iteration + 1}/{self.n_iterations}, RMSE: {rmse:.4f}")

        self.is_trained = True

    def predict(self, user_id: int, item_id: int) -> float:
        if user_id not in self.user_mapper or item_id not in self.item_mapper:
            return self.global_mean

        u = self.user_mapper[user_id]
        i = self.item_mapper[item_id]
        pred = self.global_mean + self.user_bias[u] + self.item_bias[i] + np.dot(self.user_factors[u], self.item_factors[i])
        return float(np.clip(pred, 1.0, 5.0))

    def recommend(self, user_id: int, limit: int = 20, exclude_ids: Optional[list[int]] = None) -> list[dict]:
        if not self.is_trained:
            return []

        if user_id not in self.user_mapper:
            return self._popular_fallback(limit, exclude_ids)

        u = self.user_mapper[user_id]
        scores = self.global_mean + self.user_bias[u] + self.item_bias + np.dot(self.item_factors, self.user_factors[u])

        scored_items = []
        for i, score in enumerate(scores):
            original_id = self.reverse_item_mapper[i]
            if exclude_ids and original_id in exclude_ids:
                continue
            scored_items.append((original_id, float(np.clip(score, 1.0, 5.0))))

        scored_items = sorted(scored_items, key=lambda x: x[1], reverse=True)[:limit]

        recommendations = []
        for item_id, score in scored_items:
            item_info = self.items_df[self.items_df["item_id"] == item_id]
            if len(item_info) == 0:
                continue
            row = item_info.iloc[0]
            normalized = (score - 1.0) / 4.0
            recommendations.append({
                "item_id": int(item_id),
                "title": row["title"],
                "image_url": row.get("image_url"),
                "category": row.get("category"),
                "genres": row.get("genres"),
                "avg_rating": float(row.get("avg_rating", 0)),
                "score": round(normalized, 4),
                "confidence": round(min(normalized * 0.9, 0.95), 3),
                "reason": "Based on your latent preferences",
                "similarity_pct": round(min(normalized * 100, 99.9), 1),
                "algorithm": "matrix_factorization",
            })
        return recommendations

    def _popular_fallback(self, limit: int, exclude_ids: Optional[list[int]]) -> list[dict]:
        if self.items_df is None:
            return []
        df = self.items_df.copy()
        if exclude_ids:
            df = df[~df["item_id"].isin(exclude_ids)]
        top = df.nlargest(limit, "popularity_score")
        return [
            {
                "item_id": int(row["item_id"]), "title": row["title"],
                "image_url": row.get("image_url"), "category": row.get("category"),
                "genres": row.get("genres"), "avg_rating": float(row.get("avg_rating", 0)),
                "score": 0.5, "confidence": 0.5,
                "reason": "Popular items", "similarity_pct": 50.0,
                "algorithm": "matrix_factorization",
            }
            for _, row in top.iterrows()
        ]

    def save(self, path: str):
        data = {
            "user_factors": self.user_factors, "item_factors": self.item_factors,
            "user_bias": self.user_bias, "item_bias": self.item_bias,
            "global_mean": self.global_mean, "user_mapper": self.user_mapper,
            "item_mapper": self.item_mapper, "reverse_user_mapper": self.reverse_user_mapper,
            "reverse_item_mapper": self.reverse_item_mapper, "items_df": self.items_df,
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            data = pickle.load(f)
        for k, v in data.items():
            setattr(self, k, v)
        self.is_trained = True
