import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("FATAL: DATABASE_URL env var is missing on Render")
    raise RuntimeError("DATABASE_URL is not set")

print(f"ENV CHECK: DATABASE_URL exists? True | starts with {DATABASE_URL[:20]}...")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
if DATABASE_URL.startswith("postgresql://") and "psycopg2" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    try:
        from modules.auth.models import User
        from modules.user.models import Address, Wallet, Transaction
        Base.metadata.create_all(bind=engine)
        print("DB TABLES CREATED - SUCCESS")
    except Exception as e:
        print(f"DB CREATE FAILED - REAL ERROR: {e}")
        raise e

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
