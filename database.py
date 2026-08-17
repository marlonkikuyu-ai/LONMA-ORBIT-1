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

# Retry for Render free DB cold start
for i in range(3):
    try:
        Base.metadata.create_all(bind=engine)
        print("TABLES CREATED")
        break
    except OperationalError as e:
        print(f"DB NOT READY YET, retrying... {i+1}/3")
        time.sleep(5)
else:
    print("COULD NOT CONNECT TO DB AFTER 3 TRIES")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
