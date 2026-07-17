import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Optional
import pickle
import os


class ContentBasedRecommender:
    def __init__(self):
        self.name = "content_based"
        self.is_trained = False
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.items_df = None
        self.user_profiles = {}

    def train(self, items_df: pd.DataFrame, ratings_df: Optional[pd.DataFrame] = None):
        self.items_df = items_df.copy()

        text_features = self._combine_features(items_df)
        self.tfidf_vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(text_features)

        if ratings_df is not None and len(ratings_df) > 0:
            self._build_user_profiles(ratings_df)

        self.is_trained = True

    def _combine_features(self, df: pd.DataFrame) -> pd.Series:
        features = []
        for _, row in df.iterrows():
            parts = [
                str(row.get("title", "")),
                str(row.get("description", "")),
                str(row.get("category", "")),
                str(row.get("genres", "")),
                str(row.get("tags", "")),
            ]
            features.append(" ".join(parts))
        return pd.Series(features)

    def _build_user_profiles(self, ratings_df: pd.DataFrame):
        for user_id in ratings_df["user_id"].unique():
            user_ratings = ratings_df[ratings_df["user_id"] == user_id]
            liked_items = user_ratings[user_ratings["rating"] >= 3.5]["item_id"].values

            if len(liked_items) == 0:
                continue

            item_indices = []
            weights = []
            for item_id in liked_items:
                idx_list = self.items_df[self.items_df["item_id"] == item_id].index.tolist()
                if idx_list:
                    item_indices.append(idx_list[0])
                    rating = user_ratings[user_ratings["item_id"] == item_id]["rating"].values
                    weights.append(float(rating[0]) if len(rating) > 0 else 1.0)

            if item_indices:
                profile = np.zeros(self.tfidf_matrix.shape[1])
                total_weight = sum(weights)
                for idx, weight in zip(item_indices, weights):
                    profile += self.tfidf_matrix[idx].toarray().flatten() * (weight / total_weight)
                self.user_profiles[user_id] = profile

    def recommend(self, user_id: int, limit: int = 20, exclude_ids: Optional[list[int]] = None) -> list[dict]:
        if not self.is_trained:
            return []

        if user_id in self.user_profiles:
            user_profile = self.user_profiles[user_id].reshape(1, -1)
            scores = cosine_similarity(user_profile, self.tfidf_matrix).flatten()
        else:
            scores = np.ones(self.tfidf_matrix.shape[0]) * 0.5

        df = self.items_df.copy()
        df["content_score"] = scores

        if exclude_ids:
            df = df[~df["item_id"].isin(exclude_ids)]

        top_items = df.nlargest(limit, "content_score")

        recommendations = []
        for _, row in top_items.iterrows():
            score = float(row["content_score"])
            genre = row.get("genres", "various genres")
            recommendations.append({
                "item_id": int(row["item_id"]),
                "title": row["title"],
                "image_url": row.get("image_url"),
                "category": row.get("category"),
                "genres": row.get("genres"),
                "avg_rating": float(row.get("avg_rating", 0)),
                "score": score,
                "confidence": round(min(score * 0.9, 0.95), 3),
                "reason": f"Similar to your preference for {genre}",
                "similarity_pct": round(min(score * 100, 99.9), 1),
                "algorithm": "content_based",
            })
        return recommendations

    def get_metrics(self) -> dict:
        return {"algorithm": "content_based", "is_trained": self.is_trained, "vocabulary_size": self.tfidf_matrix.shape[1] if self.tfidf_matrix is not None else 0}

    def save(self, path: str):
        data = {"vectorizer": self.tfidf_vectorizer, "matrix": self.tfidf_matrix, "user_profiles": self.user_profiles, "items_df": self.items_df}
        with open(path, "wb") as f:
            pickle.dump(data, f)

    def load(self, path: str):
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.tfidf_vectorizer = data["vectorizer"]
        self.tfidf_matrix = data["matrix"]
        self.user_profiles = data["user_profiles"]
        self.items_df = data["items_df"]
        self.is_trained = True
