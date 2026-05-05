"""
Integration tests for signup/removal endpoints.
Tests cover POST /activities/{activity_name}/signup and DELETE variants.
Tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success_with_valid_activity_and_email(self, client, reset_activities):
        """
        Test successful student signup for an activity
        
        AAA Pattern:
        - Arrange: Valid activity name and new email address
        - Act: Make POST request to signup endpoint
        - Assert: Verify success response and participant is added
        """
        # Arrange
        activity_name = "Basketball Team"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
    def test_signup_fails_with_nonexistent_activity(self, client, reset_activities):
        """
        Test signup fails with 404 for nonexistent activity
        
        AAA Pattern:
        - Arrange: Invalid activity name and valid email
        - Act: Make POST request to signup endpoint with fake activity
        - Assert: Verify 404 error response
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
        
    def test_signup_fails_when_student_already_enrolled(self, client, reset_activities):
        """
        Test signup fails with 400 when student is already signed up
        
        AAA Pattern:
        - Arrange: Activity "Chess Club" already has participants
        - Act: Try to sign up a student already in the activity
        - Assert: Verify 400 error response
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        
    def test_signup_adds_participant_to_activity_list(self, client, reset_activities):
        """
        Test that signup actually adds participant to the participants list
        
        AAA Pattern:
        - Arrange: Empty activity "Soccer Club" and new email
        - Act: Make signup request and fetch activities to verify state
        - Assert: Verify participant list was updated
        """
        # Arrange
        activity_name = "Soccer Club"
        email = "newplayer@mergington.edu"
        
        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]


class TestRemovalEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_removal_success_with_enrolled_student(self, client, reset_activities):
        """
        Test successful removal of enrolled student from activity
        
        AAA Pattern:
        - Arrange: Student enrolled in "Chess Club"
        - Act: Make DELETE request to remove them
        - Assert: Verify success response and participant is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        
    def test_removal_fails_with_nonexistent_activity(self, client, reset_activities):
        """
        Test removal fails with 404 for nonexistent activity
        
        AAA Pattern:
        - Arrange: Invalid activity name
        - Act: Make DELETE request with fake activity
        - Assert: Verify 404 error response
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
        
    def test_removal_fails_when_student_not_enrolled(self, client, reset_activities):
        """
        Test removal fails with 400 when student is not signed up
        
        AAA Pattern:
        - Arrange: Student not in "Art Club"
        - Act: Try to remove student from activity they're not in
        - Assert: Verify 400 error response
        """
        # Arrange
        activity_name = "Art Club"
        email = "notstudent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"
        
    def test_removal_actually_removes_participant_from_list(self, client, reset_activities):
        """
        Test that removal actually removes participant from the participants list
        
        AAA Pattern:
        - Arrange: Student enrolled in "Chess Club"
        - Act: Make DELETE request and verify state by fetching activities
        - Assert: Verify participant list was updated
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        removal_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert removal_response.status_code == 200
        assert email not in activities[activity_name]["participants"]


class TestSignupRemovalCycle:
    """Tests for complete signup and removal workflow"""
    
    def test_signup_then_removal_workflow(self, client, reset_activities):
        """
        Test complete workflow: signup, verify, remove, verify
        
        AAA Pattern:
        - Arrange: Student not yet signed up
        - Act: Sign up, check state, remove, check state
        - Assert: Verify all state transitions are correct
        """
        # Arrange
        activity_name = "Drama Club"
        email = "actor@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_after_signup = client.get("/activities").json()
        
        # Act - Remove
        removal_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_after_removal = client.get("/activities").json()
        
        # Assert
        assert signup_response.status_code == 200
        assert email in activities_after_signup[activity_name]["participants"]
        assert removal_response.status_code == 200
        assert email not in activities_after_removal[activity_name]["participants"]
