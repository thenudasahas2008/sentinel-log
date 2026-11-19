import pytest
import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.utils.security import hash_password

@pytest.fixture(scope="session")
def engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

@pytest.fixture(scope="function")
def db(engine):
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    # Seed test users
    admin = User(
        username="testadmin",
        email="testadmin@sentinellog.local",
        full_name="Test Administrator",
        hashed_password=hash_password("TestSecret123!"),
        role=UserRole.ADMIN,
        is_active=True
    )
    analyst = User(
        username="testanalyst",
        email="testanalyst@sentinellog.local",
        full_name="Test Analyst",
        hashed_password=hash_password("TestSecret123!"),
        role=UserRole.ANALYST,
        is_active=True
    )
    session.add_all([admin, analyst])
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
