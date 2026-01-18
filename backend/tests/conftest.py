import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

# Mock settings before importing app modules
mock_settings = MagicMock()
mock_settings.database_url = "sqlite:///./test.db"
mock_settings.riot_api_key = "test-key"
mock_settings.riot_api_region = "euw1"
mock_settings.riot_api_cache_ttl = 3600
mock_settings.access_code = "test-code"
mock_settings.jwt_secret = "test-secret"
mock_settings.jwt_algorithm = "HS256"
mock_settings.jwt_expiration_hours = 720

with patch('app.config.settings', mock_settings):
    from app.database import Base, get_db
    from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()