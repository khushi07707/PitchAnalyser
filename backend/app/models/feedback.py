import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    strengths = Column(JSON, nullable=False)           # array of strings
    weaknesses = Column(JSON, nullable=False)          # array of strings
    suggestions = Column(JSON, nullable=False)         # array of strings
    overall_review = Column(Text, nullable=False)
    presentation_tips = Column(JSON, nullable=False)   # array of strings
    communication_tips = Column(JSON, nullable=False)  # array of strings
    confidence_tips = Column(JSON, nullable=False)     # array of strings

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    upload = relationship("Upload", back_populates="feedback")
