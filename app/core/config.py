from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    SECRET_KEY: str
    DEBUG: bool

    class Config:
        env_file = ".env"

settings = Settings()

def get_db_url():
    return (f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@"
            f"{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")