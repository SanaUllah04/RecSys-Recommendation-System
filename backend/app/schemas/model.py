from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class TrainRequest(BaseModel):
    algorithm: str = "hybrid"
    parameters: Optional[dict] = None
    test_size: float = 0.2


class ModelVersionResponse(BaseModel):
    id: int
    version: str
    algorithm: str
    model_path: str
    metrics: Optional[dict]
    parameters: Optional[dict]
    training_data_size: int
    training_duration_seconds: float
    is_active: bool
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ModelMetrics(BaseModel):
    precision_at_k: Optional[float] = None
    recall_at_k: Optional[float] = None
    ndcg: Optional[float] = None
    map_score: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None


class TrainStatus(BaseModel):
    status: str
    message: str
    model_version: Optional[str] = None
    metrics: Optional[dict] = None
    training_duration: Optional[float] = None


class DashboardStats(BaseModel):
    total_users: int
    total_items: int
    total_interactions: int
    total_ratings: int
    active_users_24h: int
    total_recommendations: int
    avg_rating: float
    top_categories: list[dict]
    interaction_types: list[dict]
