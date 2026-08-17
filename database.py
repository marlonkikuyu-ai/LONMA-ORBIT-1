import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    for i in range(5): # 5 retries
        try:
            Base.metadata.create_all(bind=engine)
            print("TABLES CREATED")
            return
        except OperationalError:
            print(f"DB NOT READY YET, retrying... {i+1}/5")
            time.sleep(5)
    print("COULD NOT CONNECT TO DB")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
