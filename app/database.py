from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get the database URL from .env (default to local sqlite if not found)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")

# check_same_thread=False is only required for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the DB session in routers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()