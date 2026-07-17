import pandas as pd
import numpy as np
from typing import Optional


class PopularityRecommender:
    def __init__(self):
        self.name = "popularity"
        self.is_trained = False
        self.items_df = None

    def train(self, items_df: pd.DataFrame, interactions_df: Optional[pd.DataFrame] = None):
        self.items_df = items_df.copy()

        if interactions_df is not None and len(interactions_df) > 0:
            interaction_counts = interactions_df.groupby("item_id").size().reset_index(name="interaction_count")
            self.items_df = self.items_df.merge(interaction_counts, on="item_id", how="left")
            self.items_df["interaction_count"] = self.items_df["interaction_count"].fillna(0)
        else:
            self.items_df["interaction_count"] = self.items_df.get("rating_count", 0)

        self.items_df["popularity_score"] = self._compute_popularity()
        self.is_trained = True

    def _compute_popularity(self) -> pd.Series:
        df = self.items_df
        rating_norm = (df["avg_rating"] - df["avg_rating"].min()) / (df["avg_rating"].max() - df["avg_rating"].min() + 1e-8)
        count_norm = (df["interaction_count"] - df["interaction_count"].min()) / (df["interaction_count"].max() - df["interaction_count"].min() + 1e-8)
        popularity = 0.6 * count_norm + 0.4 * rating_norm
        return popularity

    def recommend(self, user_id: int, limit: int = 20, exclude_ids: Optional[list[int]] = None) -> list[dict]:
        if not self.is_trained:
            return []

        df = self.items_df.copy()
        if exclude_ids:
            df = df[~df["item_id"].isin(exclude_ids)]

        top_items = df.nlargest(limit, "popularity_score")

        recommendations = []
        for _, row in top_items.iterrows():
            recommendations.append({
                "item_id": int(row["item_id"]),
                "title": row["title"],
                "image_url": row.get("image_url"),
                "category": row.get("category"),
                "genres": row.get("genres"),
                "avg_rating": float(row.get("avg_rating", 0)),
                "score": float(row["popularity_score"]),
                "confidence": 0.85,
                "reason": "Trending and popular among all users",
                "similarity_pct": round(float(row["popularity_score"]) * 100, 1),
                "algorithm": "popularity",
            })
        return recommendations

    def get_metrics(self) -> dict:
        return {"algorithm": "popularity", "is_trained": self.is_trained}
