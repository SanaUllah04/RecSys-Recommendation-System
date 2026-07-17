from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False, unique=True)
    algorithm = Column(String(100), nullable=False, index=True)
    model_path = Column(Text, nullable=False)
    metrics = Column(JSON, nullable=True)
    parameters = Column(JSON, nullable=True)
    training_data_size = Column(Integer, default=0)
    training_duration_seconds = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
