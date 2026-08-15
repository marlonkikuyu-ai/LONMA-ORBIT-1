# core/config.py
import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv() # load.env file

class Settings(BaseSettings):
    APP_NAME: str = "LONMA Orbit"
    DEBUG: bool = False
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    # add your other env vars here

    class Config:
        env_file = ".env"

settings = Settings()
