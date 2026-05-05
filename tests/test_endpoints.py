"""
Integration tests for FastAPI endpoints (root and activities list).
Tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_endpoint_redirects_to_static_index(self, client, reset_activities):
        """
        Test that GET / redirects to /static/index.html
        
        AAA Pattern:
        - Arrange: TestClient is ready (fixture)
        - Act: Make GET request to /
        - Assert: Verify redirect status and location
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Test that GET /activities returns the complete list of activities
        
        AAA Pattern:
        - Arrange: Activities data is loaded (fixture)
        - Act: Make GET request to /activities
        - Assert: Verify response contains all activities with correct structure
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(activities_data, dict)
        assert len(activities_data) == 9  # 9 extracurricular activities
        
    def test_get_activities_returns_correct_activity_structure(self, client, reset_activities):
        """
        Test that each activity has the required fields
        
        AAA Pattern:
        - Arrange: Activities data is loaded (fixture)
        - Act: Make GET request to /activities
        - Assert: Verify each activity has required structure
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity in activities_data.items():
            assert isinstance(activity, dict)
            assert required_fields.issubset(activity.keys())
            assert isinstance(activity["participants"], list)
            assert isinstance(activity["max_participants"], int)
            
    def test_get_activities_includes_chess_club(self, client, reset_activities):
        """
        Test that GET /activities includes the Chess Club activity
        
        AAA Pattern:
        - Arrange: Activities data is loaded (fixture)
        - Act: Make GET request to /activities
        - Assert: Verify Chess Club is in the response
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert "Chess Club" in activities_data
        assert activities_data["Chess Club"]["max_participants"] == 12
