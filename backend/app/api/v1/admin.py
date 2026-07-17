from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.deps import get_admin_user
from app.models.user import User
from app.models.item import Item
from app.models.interaction import Interaction
from app.models.rating import Rating
from app.models.model_version import ModelVersion
from app.models.recommendation_log import RecommendationLog
from app.repositories.user_repository import UserRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.model_repository import ModelRepository
from ml.pipelines.main_pipeline import ml_pipeline
from app.schemas.model import TrainRequest, TrainStatus

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db), admin: User = Depends(get_admin_user)):
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_items = (await db.execute(select(func.count(Item.id)))).scalar_one()
    total_interactions = (await db.execute(select(func.count(Interaction.id)))).scalar_one()
    total_ratings = (await db.execute(select(func.count(Rating.id)))).scalar_one()
    total_recs = (await db.execute(select(func.count(RecommendationLog.id)))).scalar_one()
    avg_rating = (await db.execute(select(func.avg(Rating.rating)))).scalar_one() or 0

    categories_result = await db.execute(
        select(Item.category, func.count(Item.id))
        .where(Item.category.isnot(None))
        .group_by(Item.category)
        .order_by(func.count(Item.id).desc())
        .limit(10)
    )
    top_categories = [{"name": r[0], "count": r[1]} for r in categories_result.all()]

    interaction_types = await db.execute(
        select(Interaction.interaction_type, func.count(Interaction.id))
        .group_by(Interaction.interaction_type)
    )
    interaction_stats = [{"type": r[0], "count": r[1]} for r in interaction_types.all()]

    return {
        "total_users": total_users,
        "total_items": total_items,
        "total_interactions": total_interactions,
        "total_ratings": total_ratings,
        "active_users_24h": total_users,
        "total_recommendations": total_recs,
        "avg_rating": round(float(avg_rating), 2),
        "top_categories": top_categories,
        "interaction_types": interaction_stats,
    }


@router.post("/train")
async def train_model(
    request: TrainRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    result = await ml_pipeline.train(db, request.algorithm, request.parameters)
    return result


@router.get("/models", response_model=list)
async def list_models(db: AsyncSession = Depends(get_db), admin: User = Depends(get_admin_user)):
    repo = ModelRepository(db)
    models = await repo.get_all(limit=50)
    return [{"id": m.id, "version": m.version, "algorithm": m.algorithm, "metrics": m.metrics,
             "training_data_size": m.training_data_size, "training_duration_seconds": m.training_duration_seconds,
             "is_active": m.is_active, "created_at": str(m.created_at)} for m in models]


@router.get("/users")
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    repo = UserRepository(db)
    users = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()
    return {
        "users": [{"id": u.id, "email": u.email, "username": u.username, "full_name": u.full_name,
                    "is_active": u.is_active, "is_admin": u.is_admin, "created_at": str(u.created_at)} for u in users],
        "total": total,
    }


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(get_admin_user)):
    repo = UserRepository(db)
    if user_id == admin.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    deleted = await repo.delete(user_id)
    if not deleted:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.get("/logs")
async def get_recommendation_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    from app.repositories.recommendation_log_repository import RecommendationLogRepository
    repo = RecommendationLogRepository(db)
    logs = await repo.get_all(skip=skip, limit=limit)
    total = await repo.count()
    return {
        "logs": [{"id": l.id, "user_id": l.user_id, "algorithm": l.algorithm,
                   "response_time_ms": l.response_time_ms, "created_at": str(l.created_at)} for l in logs],
        "total": total,
    }
