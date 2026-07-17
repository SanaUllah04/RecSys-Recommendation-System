import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import time
import os
import json
from datetime import datetime

from app.models.item import Item
from app.models.rating import Rating
from app.models.interaction import Interaction
from app.models.model_version import ModelVersion
from ml.pipelines.hybrid import HybridRecommender
from ml.pipelines.popularity import PopularityRecommender
from ml.pipelines.content_based import ContentBasedRecommender
from ml.pipelines.collaborative import CollaborativeRecommender
from ml.pipelines.matrix_factorization import MatrixFactorizationRecommender
from ml.pipelines.evaluator import RecommendationEvaluator
from app.core.config import get_settings

settings = get_settings()


class MLPipeline:
    def __init__(self):
        self.hybrid = HybridRecommender()
        self.popularity = PopularityRecommender()
        self.content_based = ContentBasedRecommender()
        self.collaborative = CollaborativeRecommender()
        self.matrix_factorization = MatrixFactorizationRecommender()
        self.is_trained = False
        self.model_dir = settings.ML_MODEL_DIR
        os.makedirs(self.model_dir, exist_ok=True)

    async def load_data(self, db: AsyncSession) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        items_result = await db.execute(select(Item))
        items = items_result.scalars().all()
        items_df = pd.DataFrame([{
            "item_id": i.id, "title": i.title, "description": i.description or "",
            "category": i.category or "", "genres": i.genres or "", "tags": i.tags or "",
            "image_url": i.image_url, "avg_rating": i.avg_rating or 0,
            "rating_count": i.rating_count or 0, "popularity_score": i.popularity_score or 0,
        } for i in items])

        ratings_result = await db.execute(select(Rating))
        ratings = ratings_result.scalars().all()
        ratings_df = pd.DataFrame([{
            "user_id": r.user_id, "item_id": r.item_id, "rating": r.rating,
        } for r in ratings]) if ratings else pd.DataFrame(columns=["user_id", "item_id", "rating"])

        interactions_result = await db.execute(select(Interaction))
        interactions = interactions_result.scalars().all()
        interactions_df = pd.DataFrame([{
            "user_id": interaction.user_id, "item_id": interaction.item_id, "weight": interaction.weight,
            "interaction_type": interaction.interaction_type,
        } for interaction in interactions]) if interactions else pd.DataFrame(columns=["user_id", "item_id", "weight", "interaction_type"])

        return items_df, ratings_df, interactions_df

    async def train(self, db: AsyncSession, algorithm: str = "hybrid", parameters: Optional[dict] = None) -> dict:
        start_time = time.time()

        print("Loading data from database...")
        items_df, ratings_df, interactions_df = await self.load_data(db)

        if len(items_df) == 0:
            return {"status": "error", "message": "No items found in database"}

        print(f"Loaded {len(items_df)} items, {len(ratings_df)} ratings, {len(interactions_df)} interactions")

        if algorithm == "hybrid" or algorithm == "all":
            self.hybrid.train(items_df, ratings_df, interactions_df)
        elif algorithm == "popularity":
            self.popularity.train(items_df, interactions_df)
        elif algorithm == "content_based":
            self.content_based.train(items_df, ratings_df)
        elif algorithm == "collaborative":
            self.collaborative.train(ratings_df, items_df, interactions_df)
        elif algorithm == "matrix_factorization":
            self.matrix_factorization.train(ratings_df, items_df)

        duration = time.time() - start_time

        metrics = {}
        if len(ratings_df) > 10:
            test_users = ratings_df["user_id"].unique()[:min(20, len(ratings_df["user_id"].unique()))]
            try:
                if algorithm in ("hybrid", "all"):
                    metrics = RecommendationEvaluator.evaluate_model(
                        lambda uid, limit=10: self.hybrid.recommend(uid, limit),
                        test_users.tolist(), ratings_df, k=min(10, len(items_df))
                    )
                elif algorithm == "popularity":
                    metrics = RecommendationEvaluator.evaluate_model(
                        lambda uid, limit=10: self.popularity.recommend(uid, limit),
                        test_users.tolist(), ratings_df, k=min(10, len(items_df))
                    )
                elif algorithm == "content_based":
                    metrics = RecommendationEvaluator.evaluate_model(
                        lambda uid, limit=10: self.content_based.recommend(uid, limit),
                        test_users.tolist(), ratings_df, k=min(10, len(items_df))
                    )
                elif algorithm == "collaborative":
                    metrics = RecommendationEvaluator.evaluate_model(
                        lambda uid, limit=10: self.collaborative.recommend(uid, limit),
                        test_users.tolist(), ratings_df, k=min(10, len(items_df))
                    )
                elif algorithm == "matrix_factorization":
                    metrics = RecommendationEvaluator.evaluate_model(
                        lambda uid, limit=10: self.matrix_factorization.recommend(uid, limit),
                        test_users.tolist(), ratings_df, k=min(10, len(items_df))
                    )
            except Exception as e:
                print(f"Evaluation error: {e}")

        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_version = ModelVersion(
            version=f"v_{algorithm}_{version}",
            algorithm=algorithm,
            model_path=f"{self.model_dir}/{algorithm}_{version}.pkl",
            metrics=metrics,
            parameters=parameters or {},
            training_data_size=len(items_df),
            training_duration_seconds=round(duration, 2),
            is_active=True,
            description=f"Trained {algorithm} model on {len(items_df)} items",
        )
        db.add(model_version)
        await db.commit()

        self.is_trained = True
        return {
            "status": "success",
            "message": f"{algorithm} model trained successfully",
            "model_version": model_version.version,
            "metrics": metrics,
            "training_duration": round(duration, 2),
            "data_size": {"items": len(items_df), "ratings": len(ratings_df), "interactions": len(interactions_df)},
        }

    def recommend(self, user_id: int, algorithm: str = "hybrid", limit: int = 20, exclude_ids: Optional[list[int]] = None) -> list[dict]:
        if algorithm == "popularity":
            return self.popularity.recommend(user_id, limit, exclude_ids)
        elif algorithm == "content_based":
            return self.content_based.recommend(user_id, limit, exclude_ids)
        elif algorithm == "collaborative":
            return self.collaborative.recommend(user_id, limit, exclude_ids)
        elif algorithm == "matrix_factorization":
            return self.matrix_factorization.recommend(user_id, limit, exclude_ids)
        else:
            return self.hybrid.recommend(user_id, limit, exclude_ids)

    def get_all_recommendations(self, user_id: int, limit: int = 10, exclude_ids: Optional[list[int]] = None) -> dict:
        if not self.is_trained:
            empty = lambda: []
            return {
                "popularity": self.popularity.recommend(user_id, limit, exclude_ids),
                "content_based": self.content_based.recommend(user_id, limit, exclude_ids),
                "collaborative": self.collaborative.recommend(user_id, limit, exclude_ids),
                "matrix_factorization": self.matrix_factorization.recommend(user_id, limit, exclude_ids),
                "hybrid": self.hybrid.recommend(user_id, limit, exclude_ids),
            }
        return self.hybrid.get_all_user_recommendations(user_id, limit, exclude_ids)


ml_pipeline = MLPipeline()
