from pydantic import BaseSettings, Field, PostgresDsn


class Config(BaseSettings):
    DB_URL: PostgresDsn = Field(env="DB_URL")


config = Config()
