import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class Upload(Base):
    __tablename__ = "uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    filepath = Column(String(1000), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(200), nullable=False)
    duration = Column(Float, nullable=True)
    status = Column(String(100), nullable=False, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="uploads")
    transcript = relationship("Transcript", uselist=False, back_populates="upload", cascade="all, delete-orphan")
    analysis_result = relationship("AnalysisResult", uselist=False, back_populates="upload", cascade="all, delete-orphan")
    feedback = relationship("Feedback", uselist=False, back_populates="upload", cascade="all, delete-orphan")
    report = relationship("Report", uselist=False, back_populates="upload", cascade="all, delete-orphan")
