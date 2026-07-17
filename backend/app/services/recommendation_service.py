import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.rating_repository import RatingRepository
from app.repositories.recommendation_log_repository import RecommendationLogRepository
from ml.pipelines.main_pipeline import ml_pipeline
from app.core.redis import cache
from app.schemas.recommendation import RecommendationLogCreate, InteractionCreate, RatingCreate


class RecommendationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.interaction_repo = InteractionRepository(db)
        self.rating_repo = RatingRepository(db)
        self.log_repo = RecommendationLogRepository(db)

    async def get_recommendations(self, user_id: int, algorithm: str = "hybrid", limit: int = 20) -> dict:
        cached = await cache.get_recommendations(user_id, algorithm)
        if cached:
            return {
                "user_id": user_id,
                "algorithm": algorithm,
                "recommendations": cached,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "total_count": len(cached),
                "cached": True,
            }

        start = time.time()
        user_interactions = await self.interaction_repo.get_user_interactions(user_id, limit=200)
        exclude_ids = [i.item_id for i in user_interactions]

        recs = ml_pipeline.recommend(user_id, algorithm, limit, exclude_ids)
        response_time = (time.time() - start) * 1000

        await cache.set_recommendations(user_id, algorithm, recs)
        await self.log_repo.create({
            "user_id": user_id,
            "algorithm": algorithm,
            "recommended_item_ids": [r["item_id"] for r in recs],
            "scores": [r["score"] for r in recs],
            "response_time_ms": round(response_time, 2),
        })

        return {
            "user_id": user_id,
            "algorithm": algorithm,
            "recommendations": recs,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_count": len(recs),
            "cached": False,
            "response_time_ms": round(response_time, 2),
        }

    async def compare_algorithms(self, user_id: int, algorithms: list[str], limit: int = 10) -> dict:
        user_interactions = await self.interaction_repo.get_user_interactions(user_id, limit=200)
        exclude_ids = [i.item_id for i in user_interactions]

        results = {}
        for algo in algorithms:
            results[algo] = ml_pipeline.recommend(user_id, algo, limit, exclude_ids)

        return {
            "user_id": user_id,
            "results": results,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

    async def record_interaction(self, user_id: int, data: InteractionCreate) -> dict:
        from ml.utils.helpers import create_interaction_weight
        weight = create_interaction_weight(data.interaction_type, data.duration_seconds)
        await self.interaction_repo.create({
            "user_id": user_id,
            "item_id": data.item_id,
            "interaction_type": data.interaction_type,
            "weight": weight,
            "duration_seconds": data.duration_seconds,
        })
        await cache.invalidate_pattern(f"rec:{user_id}:*")
        return {"status": "recorded", "weight": weight}

    async def record_rating(self, user_id: int, data: RatingCreate) -> dict:
        existing = await self.rating_repo.get_user_item_rating(user_id, data.item_id)
        if existing:
            existing.rating = data.rating
            await self.db.commit()
        else:
            await self.rating_repo.create({
                "user_id": user_id,
                "item_id": data.item_id,
                "rating": data.rating,
            })
        await cache.invalidate_pattern(f"rec:{user_id}:*")
        return {"status": "recorded", "rating": data.rating}

    async def get_similar_items(self, item_id: int, limit: int = 10) -> list[dict]:
        if ml_pipeline.is_trained and ml_pipeline.content_based.is_trained:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity

            items_df = ml_pipeline.content_based.items_df
            tfidf_matrix = ml_pipeline.content_based.tfidf_matrix

            item_idx_list = items_df[items_df["item_id"] == item_id].index.tolist()
            if not item_idx_list:
                return []

            item_idx = item_idx_list[0]
            item_vector = tfidf_matrix[item_idx]
            similarities = cosine_similarity(item_vector, tfidf_matrix).flatten()

            top_indices = similarities.argsort()[::-1][1:limit + 1]

            results = []
            for idx in top_indices:
                row = items_df.iloc[idx]
                results.append({
                    "item_id": int(row["item_id"]),
                    "title": row["title"],
                    "image_url": row.get("image_url"),
                    "category": row.get("category"),
                    "genres": row.get("genres"),
                    "avg_rating": float(row.get("avg_rating", 0)),
                    "score": round(float(similarities[idx]), 4),
                    "similarity_pct": round(float(similarities[idx]) * 100, 1),
                })
            return results
        return []
