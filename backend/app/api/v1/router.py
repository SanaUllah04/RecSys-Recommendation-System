from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.recommendations import router as recs_router
from app.api.v1.search import router as search_router
from app.api.v1.items import router as items_router
from app.api.v1.admin import router as admin_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(recs_router)
api_router.include_router(search_router)
api_router.include_router(items_router)
api_router.include_router(admin_router)
