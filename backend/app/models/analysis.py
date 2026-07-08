import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Audio Analysis Metrics (Librosa)
    speaking_rate = Column(Float, nullable=False)        # Words Per Minute
    pitch_mean = Column(Float, nullable=False)           # Hz
    pitch_stability = Column(Float, nullable=False)      # standard deviation of F0
    energy = Column(Float, nullable=False)               # Root Mean Square energy
    pauses_count = Column(Integer, nullable=False)
    silence_duration = Column(Float, nullable=False)     # total silence in seconds
    voice_modulation = Column(Float, nullable=False)     # score of modulation
    
    # NLP Analysis Metrics (NLTK, TextBlob)
    filler_words = Column(JSON, nullable=False)          # counts & list of filler words
    repeated_words = Column(JSON, nullable=False)        # sequential repetitions
    grammar_issues = Column(JSON, nullable=False)        # heuristic grammar/syntactic findings
    sentiment_polarity = Column(Float, nullable=False)   # polarity score
    sentiment_subjectivity = Column(Float, nullable=False) # subjectivity score
    keywords = Column(JSON, nullable=False)              # keywords
    confidence_indicators = Column(JSON, nullable=False) # confidence markers
    speaking_style = Column(String(100), nullable=False) # computed style
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    upload = relationship("Upload", back_populates="analysis_result")
