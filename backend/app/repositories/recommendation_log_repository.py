from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.recommendation_log import RecommendationLog
from app.repositories.base import BaseRepository


class RecommendationLogRepository(BaseRepository[RecommendationLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(RecommendationLog, db)

    async def get_user_logs(self, user_id: int, limit: int = 50):
        result = await self.db.execute(
            select(RecommendationLog)
            .where(RecommendationLog.user_id == user_id)
            .order_by(RecommendationLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_total_count(self) -> int:
        result = await self.db.execute(select(func.count(RecommendationLog.id)))
        return result.scalar_one()

    async def get_click_rate(self, algorithm: str) -> float:
        result = await self.db.execute(
            select(
                func.avg(RecommendationLog.was_clicked)
            ).where(RecommendationLog.algorithm == algorithm)
        )
        return result.scalar_one() or 0.0
