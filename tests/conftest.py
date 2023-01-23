import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.orm import clear_mappers, sessionmaker

from app.orm import meta_data, start_mappers


@pytest.fixture
def in_memory_db() -> Connection:
    engine = create_engine("sqlite:///:memory:")
    meta_data.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db: Connection) -> sessionmaker:
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()
