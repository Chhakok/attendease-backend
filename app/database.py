import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env
load_dotenv()

# Get the database URL from .env (default to local sqlite if not found)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")

# 1. CRITICAL FIX: Render sometimes uses 'postgres://', but SQLAlchemy requires 'postgresql://'
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 2. CRITICAL FIX: check_same_thread=False is ONLY for SQLite. It crashes PostgreSQL.
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    print("--- DATABASE: Booting Local SQLite ---")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    print("--- DATABASE: Booting Cloud PostgreSQL ---")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the DB session in routers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import os
# from dotenv import load_dotenv
#
# # Load environment variables from .env
# load_dotenv()
#
# # Get the database URL from .env (default to local sqlite if not found)
# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
#
# # check_same_thread=False is only required for SQLite
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# Base = declarative_base()
#
# # Dependency to get the DB session in routers
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()