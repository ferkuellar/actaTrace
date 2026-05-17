import base64
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.enums import UserRole, UserStatus
from app.models.polling_station import PollingStation
from app.models.user import User


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_user(db: Session, role: UserRole, email: str = "user@example.com") -> User:
    user = User(
        full_name="Test User",
        email=email,
        hashed_password=hash_password("StrongPassword123"),
        role=role,
        organization="ActaTrace QA",
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_headers(client: TestClient, email: str = "user@example.com") -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPassword123"})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_polling_station(db: Session) -> PollingStation:
    station = PollingStation(
        polling_station_code="MXCMX-D12-S0456-B01",
        state="Ciudad de Mexico",
        municipality="Benito Juarez",
        district="D12",
        section="S0456",
        station_type="BASICA",
        status="ACTIVE",
    )
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


def b64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")
