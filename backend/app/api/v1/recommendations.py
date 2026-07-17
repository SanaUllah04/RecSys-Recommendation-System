from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import InteractionCreate, RatingCreate, ComparisonRequest
from app.models.user import User

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/me")
async def get_my_recommendations(
    algorithm: str = Query("hybrid", regex="^(popularity|content_based|collaborative|matrix_factorization|hybrid)$"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RecommendationService(db)
    return await service.get_recommendations(current_user.id, algorithm, limit)


@router.get("/user/{user_id}")
async def get_user_recommendations(
    user_id: int,
    algorithm: str = Query("hybrid"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RecommendationService(db)
    return await service.get_recommendations(user_id, algorithm, limit)


@router.post("/compare")
async def compare_algorithms(
    algorithms: list[str] = Query(["popularity", "content_based", "collaborative", "matrix_factorization", "hybrid"]),
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RecommendationService(db)
    return await service.compare_algorithms(current_user.id, algorithms, limit)


@router.post("/interaction")
async def record_interaction(
    data: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RecommendationService(db)
    return await service.record_interaction(current_user.id, data)


@router.post("/rate")
async def rate_item(
    data: RatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RecommendationService(db)
    return await service.record_rating(current_user.id, data)


@router.get("/similar/{item_id}")
async def get_similar_items(
    item_id: int,
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RecommendationService(db)
    return await service.get_similar_items(item_id, limit)


@router.get("/all")
async def get_all_algorithms(
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = RecommendationService(db)
    return await service.compare_algorithms(
        current_user.id,
        ["popularity", "content_based", "collaborative", "matrix_factorization", "hybrid"],
        limit,
    )
