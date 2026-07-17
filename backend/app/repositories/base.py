from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from typing import TypeVar, Generic, Type, Optional, Sequence
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def count(self) -> int:
        result = await self.db.execute(select(func.count(self.model.id)))
        return result.scalar_one()

    async def create(self, obj_data: dict) -> ModelType:
        obj = self.model(**obj_data)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: int, obj_data: dict) -> Optional[ModelType]:
        obj = await self.get_by_id(id)
        if obj:
            for key, value in obj_data.items():
                if value is not None:
                    setattr(obj, key, value)
            await self.db.commit()
            await self.db.refresh(obj)
        return obj

    async def delete(self, id: int) -> bool:
        obj = await self.get_by_id(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False
