from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Sequence
from app.models.model_version import ModelVersion
from app.repositories.base import BaseRepository


class ModelRepository(BaseRepository[ModelVersion]):
    def __init__(self, db: AsyncSession):
        super().__init__(ModelVersion, db)

    async def get_active_models(self) -> Sequence[ModelVersion]:
        result = await self.db.execute(
            select(ModelVersion).where(ModelVersion.is_active == True)
        )
        return result.scalars().all()

    async def get_active_by_algorithm(self, algorithm: str) -> Optional[ModelVersion]:
        result = await self.db.execute(
            select(ModelVersion)
            .where(ModelVersion.algorithm == algorithm, ModelVersion.is_active == True)
            .order_by(ModelVersion.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def deactivate_previous(self, algorithm: str):
        models = await self.db.execute(
            select(ModelVersion).where(ModelVersion.algorithm == algorithm, ModelVersion.is_active == True)
        )
        for model in models.scalars().all():
            model.is_active = False
        await self.db.commit()
