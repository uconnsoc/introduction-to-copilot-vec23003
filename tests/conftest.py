import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def test_activities():
    """Provide a fresh copy of activities for each test to ensure isolation"""
    return deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities(test_activities):
    """Reset activities to test data before each test"""
    import src.app
    src.app.activities = test_activities
    yield
    # No need to cleanup as next test gets fresh copy
