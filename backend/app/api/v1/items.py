from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemResponse, ItemListResponse
from app.models.user import User

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/", response_model=ItemListResponse)
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ItemRepository(db)
    skip = (page - 1) * page_size
    if category:
        items = await repo.get_by_category(category, limit=page_size)
    else:
        items = await repo.get_all(skip=skip, limit=page_size)
    total = await repo.count()
    return ItemListResponse(
        items=[ItemResponse.model_validate(i) for i in items],
        total=total, page=page, page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/trending")
async def trending_items(limit: int = Query(20, ge=1, le=50), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = ItemRepository(db)
    items = await repo.get_trending(limit)
    return [ItemResponse.model_validate(i) for i in items]


@router.get("/top-rated")
async def top_rated_items(limit: int = Query(20, ge=1, le=50), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = ItemRepository(db)
    items = await repo.get_top_rated(limit)
    return [ItemResponse.model_validate(i) for i in items]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = ItemRepository(db)
    item = await repo.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse.model_validate(item)
