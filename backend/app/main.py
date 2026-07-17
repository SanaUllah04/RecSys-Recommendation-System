from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import init_db
from app.api.v1.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up AI Recommendation System...")
    await init_db()
    print("Database initialized")

    from ml.pipelines.main_pipeline import ml_pipeline
    from app.core.database import async_session_factory
    try:
        async with async_session_factory() as db:
            from sqlalchemy import select, func
            from app.models.item import Item
            result = await db.execute(select(func.count(Item.id)))
            item_count = result.scalar_one()
            if item_count > 0 and not ml_pipeline.is_trained:
                print(f"Found {item_count} items. Auto-training models...")
                await ml_pipeline.train(db, "hybrid")
                print("Models trained and ready!")
    except Exception as e:
        print(f"Auto-training skipped: {e}")

    yield
    print("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready AI Recommendation System with multiple ML algorithms",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "AI Recommendation System API", "version": settings.APP_VERSION, "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
