from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, Sequence
from app.models.item import Item
from app.repositories.base import BaseRepository


class ItemRepository(BaseRepository[Item]):
    def __init__(self, db: AsyncSession):
        super().__init__(Item, db)

    async def search(self, query: str, category: Optional[str] = None, skip: int = 0, limit: int = 20):
        stmt = select(Item)
        if query:
            stmt = stmt.where(
                Item.title.ilike(f"%{query}%") |
                Item.description.ilike(f"%{query}%") |
                Item.genres.ilike(f"%{query}%") |
                Item.tags.ilike(f"%{query}%")
            )
        if category:
            stmt = stmt.where(Item.category == category)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_category(self, category: str, limit: int = 20) -> Sequence[Item]:
        result = await self.db.execute(
            select(Item).where(Item.category == category).limit(limit)
        )
        return result.scalars().all()

    async def get_trending(self, limit: int = 20) -> Sequence[Item]:
        result = await self.db.execute(
            select(Item).order_by(Item.popularity_score.desc()).limit(limit)
        )
        return result.scalars().all()

    async def get_top_rated(self, limit: int = 20) -> Sequence[Item]:
        result = await self.db.execute(
            select(Item).where(Item.rating_count > 0).order_by(Item.avg_rating.desc()).limit(limit)
        )
        return result.scalars().all()

    async def get_categories(self) -> list[dict]:
        result = await self.db.execute(
            select(Item.category, func.count(Item.id))
            .where(Item.category.isnot(None))
            .group_by(Item.category)
            .order_by(func.count(Item.id).desc())
        )
        return [{"name": row[0], "count": row[1]} for row in result.all()]

    async def search_count(self, query: str = "", category: Optional[str] = None) -> int:
        stmt = select(func.count(Item.id))
        if query:
            stmt = stmt.where(
                Item.title.ilike(f"%{query}%") |
                Item.description.ilike(f"%{query}%") |
                Item.genres.ilike(f"%{query}%")
            )
        if category:
            stmt = stmt.where(Item.category == category)
        result = await self.db.execute(stmt)
        return result.scalar_one()
