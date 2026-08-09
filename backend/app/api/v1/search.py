from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemResponse, ItemListResponse
from app.models.user import User

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
async def search_items(
    q: str = Query("", description="Search query"),
    category: str = Query(None, description="Filter by category"),
    sort_by: str = Query("popularity", pattern="^(popularity|rating|date|title)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ItemRepository(db)
    skip = (page - 1) * page_size
    items = await repo.search(q, category, skip, page_size)
    total = await repo.search_count(q, category)

    return {
        "items": [ItemResponse.model_validate(i) for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = ItemRepository(db)
    return await repo.get_categories()
