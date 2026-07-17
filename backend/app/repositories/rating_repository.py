from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Sequence
from app.models.rating import Rating
from app.repositories.base import BaseRepository


class RatingRepository(BaseRepository[Rating]):
    def __init__(self, db: AsyncSession):
        super().__init__(Rating, db)

    async def get_user_ratings(self, user_id: int) -> Sequence[Rating]:
        result = await self.db.execute(
            select(Rating).where(Rating.user_id == user_id)
        )
        return result.scalars().all()

    async def get_user_item_rating(self, user_id: int, item_id: int) -> Optional[Rating]:
        result = await self.db.execute(
            select(Rating).where(Rating.user_id == user_id, Rating.item_id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_ratings_matrix(self):
        result = await self.db.execute(
            select(Rating.user_id, Rating.item_id, Rating.rating)
        )
        return result.all()

    async def get_avg_rating(self) -> float:
        result = await self.db.execute(select(func.avg(Rating.rating)))
        return result.scalar_one() or 0.0

    async def get_total_count(self) -> int:
        result = await self.db.execute(select(func.count(Rating.id)))
        return result.scalar_one()
