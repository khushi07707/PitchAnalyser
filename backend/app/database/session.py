from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.config import settings

# Create engine with connection pooling and health checks (pre-ping)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Configure the local session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models
Base = declarative_base()

# FastAPI Dependency Injection provider for DB sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
