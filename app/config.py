from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    db_url = Field(env="DB_URL", default="sqlite:///./db.db")


settings = Settings()
