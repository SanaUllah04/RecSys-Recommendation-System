from sqlalchemy import Column, Integer, ForeignKey, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    algorithm = Column(String(100), nullable=False)
    recommended_item_ids = Column(JSON, nullable=False)
    scores = Column(JSON, nullable=True)
    was_clicked = Column(Integer, default=0)
    was_purchased = Column(Integer, default=0)
    response_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
