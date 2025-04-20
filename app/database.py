from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# database connection
DATABASE_URL = os.getenv("DATABASE_URL")

# check if environment is not properly configured
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in .env file. Please set it before running the application.")

# SQLAlchemy engine for database communication
engine = create_engine(DATABASE_URL, future=True, echo=False)

# Configure session factory for creating new DB sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

# Base class for declarative ORM models
Base = declarative_base()


def get_db():
    """
    Dependency function to provide a database session.
    Used for injecting into FastAPI routes or service layers.
    Ensures session lifecycle is properly managed with 'yield'.
    """
    db = SessionLocal()
    try:
        yield db  # route handler
    finally:
        db.close()  # to ensure the session is closed after the request
