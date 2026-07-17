from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RecommendationItem(BaseModel):
    item_id: int
    title: str
    image_url: Optional[str]
    category: Optional[str]
    genres: Optional[str]
    avg_rating: float
    score: float
    confidence: float
    reason: str
    similarity_pct: float
    algorithm: str


class RecommendationResponse(BaseModel):
    user_id: int
    algorithm: str
    recommendations: list[RecommendationItem]
    generated_at: datetime
    total_count: int


class RecommendationLogCreate(BaseModel):
    user_id: int
    algorithm: str
    recommended_item_ids: list[int]
    scores: Optional[list[float]] = None
    response_time_ms: Optional[float] = None


class InteractionCreate(BaseModel):
    item_id: int
    interaction_type: str
    weight: float = 1.0
    duration_seconds: int = 0


class RatingCreate(BaseModel):
    item_id: int
    rating: float


class ComparisonRequest(BaseModel):
    user_id: int
    algorithms: list[str]
    limit: int = 10


class ComparisonResponse(BaseModel):
    user_id: int
    results: dict[str, list[RecommendationItem]]
    generated_at: datetime
