from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(255), nullable=True, index=True)
    genres = Column(String(500), nullable=True)
    tags = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    release_date = Column(DateTime, nullable=True)
    avg_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    popularity_score = Column(Float, default=0.0)
    embedding = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    interactions = relationship("Interaction", back_populates="item", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="item", cascade="all, delete-orphan")
