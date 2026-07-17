from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Sequence
from app.models.interaction import Interaction
from app.repositories.base import BaseRepository


class InteractionRepository(BaseRepository[Interaction]):
    def __init__(self, db: AsyncSession):
        super().__init__(Interaction, db)

    async def get_user_interactions(self, user_id: int, limit: int = 50) -> Sequence[Interaction]:
        result = await self.db.execute(
            select(Interaction)
            .where(Interaction.user_id == user_id)
            .order_by(Interaction.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_item_interactions(self, item_id: int, limit: int = 50) -> Sequence[Interaction]:
        result = await self.db.execute(
            select(Interaction)
            .where(Interaction.item_id == item_id)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_item_interactions(self, user_id: int, item_id: int) -> Sequence[Interaction]:
        result = await self.db.execute(
            select(Interaction)
            .where(Interaction.user_id == user_id, Interaction.item_id == item_id)
        )
        return result.scalars().all()

    async def get_interactions_matrix(self):
        result = await self.db.execute(
            select(Interaction.user_id, Interaction.item_id, Interaction.weight)
        )
        return result.all()

    async def get_interaction_counts(self) -> list[dict]:
        result = await self.db.execute(
            select(Interaction.interaction_type, func.count(Interaction.id))
            .group_by(Interaction.interaction_type)
        )
        return [{"type": row[0], "count": row[1]} for row in result.all()]

    async def get_total_count(self) -> int:
        result = await self.db.execute(select(func.count(Interaction.id)))
        return result.scalar_one()
