import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# The database URL will be read from an environment variable.
# This makes the application configurable for different environments (dev, prod).
# A default SQLite connection string is provided for local development if the variable is not set.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./life.db")

# The engine is the entry point to the database.
engine = create_engine(
    DATABASE_URL,
    # The 'connect_args' is needed for SQLite to allow multi-threaded access.
    # It's ignored by PostgreSQL.
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# A sessionmaker provides a factory for creating Session objects.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is a factory for creating ORM models.
Base = declarative_base()

def get_db():
    """
    FastAPI dependency to get a database session.
    Ensures the database connection is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()