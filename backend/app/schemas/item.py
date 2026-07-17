from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class ItemCreate(BaseModel):
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    category: Optional[str] = None
    genres: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None
    release_date: Optional[datetime] = None
    metadata_json: Optional[dict] = None


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    genres: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[str] = None


class ItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: Optional[str]
    genres: Optional[str]
    tags: Optional[str]
    image_url: Optional[str]
    release_date: Optional[datetime]
    avg_rating: float
    rating_count: int
    popularity_score: float
    metadata_json: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
