"""
Shared fixtures for FastAPI tests.
Provides test client and app instance for all test modules.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provides a TestClient instance for making HTTP requests to the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture to reset the in-memory activities database to a clean state before each test.
    This ensures test isolation and prevents tests from affecting each other.
    """
    # Store original activities state
    original_state = {
        name: {
            "description": activity["description"],
            "schedule": activity["schedule"],
            "max_participants": activity["max_participants"],
            "participants": activity["participants"].copy()
        }
        for name, activity in activities.items()
    }
    
    yield
    
    # Restore original state after test
    activities.clear()
    for name, activity in original_state.items():
        activities[name] = activity
