"""Pytest configuration and fixtures"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock

from app.main import app
from app.db.base import Base, get_db


# Test database (SQLite in memory for faster tests)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Mock Redis client
class MockRedis:
    def __init__(self):
        self.data = {}
        self.zsets = {}

    async def ping(self):
        return True
    
    async def get(self, key):
        return self.data.get(key)
    
    async def setex(self, key, ttl, value):
        self.data[key] = value
    
    async def delete(self, key):
        self.data.pop(key, None)
    
    async def exists(self, key):
        return 1 if key in self.data else 0
    
    async def zadd(self, key, mapping):
        if key not in self.zsets:
            self.zsets[key] = []
        for member, score in mapping.items():
            self.zsets[key].append((member, score))
    
    async def zcard(self, key):
        return len(self.zsets.get(key, []))
    
    async def zremrangebyscore(self, key, min_score, max_score):
        if key in self.zsets:
            self.zsets[key] = [(m, s) for m, s in self.zsets[key] if not (min_score <= s <= max_score)]
    
    async def expire(self, key, ttl):
        pass

# Mock MongoDB
class MockMongoDB:
    def __init__(self):
        self.collections = {}
    
    def __getattr__(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection()
        return self.collections[name]

class MockCollection:
    def __init__(self):
        self.documents = []
    
    async def insert_one(self, document):
        self.documents.append(document)
        return MagicMock(inserted_id="mock_id")
    
    def find(self, query=None):
        return MockCursor(self.documents)

class MockCursor:
    def __init__(self, documents):
        self.documents = documents
    
    def sort(self, *args, **kwargs):
        return self
    
    def limit(self, n):
        return self
    
    async def to_list(self, length):
        return self.documents[:length]

# Global mocks
mock_redis = MockRedis()
mock_mongo = MockMongoDB()

@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Create fresh test database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    """Provide test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    """Create test client with all mocked dependencies"""
    from app.db.redis import redis_db, get_redis # Import the singleton
    from app.db.base import get_db
    from app.db.mongodb import get_mongo_db
    
    redis_db.client = mock_redis
    # Override database
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # Override Redis
    async def override_get_redis():
        return mock_redis
    
    # Override MongoDB
    async def override_get_mongo_db():
        return mock_mongo
    
    # Apply overrides
    from app.db.base import get_db
    from app.db.redis import get_redis
    from app.db.mongodb import get_mongo_db
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_mongo_db] = override_get_mongo_db
    
    # Reset mocks between tests
    mock_redis.data.clear()
    mock_redis.zsets.clear()
    mock_mongo.collections.clear()
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()
    redis_db.client = None
