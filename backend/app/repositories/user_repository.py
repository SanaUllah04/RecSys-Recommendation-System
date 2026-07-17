from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_active_users_count(self) -> int:
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        result = await self.db.execute(
            select(func.count(User.id)).where(User.created_at >= cutoff)
        )
        return result.scalar_one()

    async def search_users(self, query: str, skip: int = 0, limit: int = 20):
        result = await self.db.execute(
            select(User)
            .where(User.username.ilike(f"%{query}%") | User.email.ilike(f"%{query}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
