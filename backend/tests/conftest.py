import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token, get_password_hash
from app.models.user import User, UserRole

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing"""
    user = User(
        email="admin@test.com",
        username="admin_test",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin Test User",
        role=UserRole.ADMIN,
        department="IT",
        phone="+1234567890",
        is_active=True,
        is_superuser=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def manager_user(db_session):
    """Create a manager user for testing"""
    user = User(
        email="manager@test.com",
        username="manager_test",
        hashed_password=get_password_hash("manager123"),
        full_name="Manager Test User",
        role=UserRole.MANAGER,
        department="Operations",
        phone="+1234567891",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def staff_user(db_session):
    """Create a staff user for testing"""
    user = User(
        email="staff@test.com",
        username="staff_test",
        hashed_password=get_password_hash("staff123"),
        full_name="Staff Test User",
        role=UserRole.STAFF,
        department="Warehouse",
        phone="+1234567892",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def viewer_user(db_session):
    """Create a viewer user for testing"""
    user = User(
        email="viewer@test.com",
        username="viewer_test",
        hashed_password=get_password_hash("viewer123"),
        full_name="Viewer Test User",
        role=UserRole.VIEWER,
        department="Sales",
        phone="+1234567893",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_token(admin_user):
    """Create an access token for admin user"""
    return create_access_token(data={"sub": admin_user.username})

@pytest.fixture
def manager_token(manager_user):
    """Create an access token for manager user"""
    return create_access_token(data={"sub": manager_user.username})

@pytest.fixture
def staff_token(staff_user):
    """Create an access token for staff user"""
    return create_access_token(data={"sub": staff_user.username})

@pytest.fixture
def viewer_token(viewer_user):
    """Create an access token for viewer user"""
    return create_access_token(data={"sub": viewer_user.username})

@pytest.fixture
def admin_headers(admin_token):
    """Create headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def manager_headers(manager_token):
    """Create headers with manager token"""
    return {"Authorization": f"Bearer {manager_token}"}

@pytest.fixture
def staff_headers(staff_token):
    """Create headers with staff token"""
    return {"Authorization": f"Bearer {staff_token}"}

@pytest.fixture
def viewer_headers(viewer_token):
    """Create headers with viewer token"""
    return {"Authorization": f"Bearer {viewer_token}"} 