"""
Unit and integration tests for activity constraints and validation.
Tests cover max_participants limits and activity structure.
Tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestActivityStructure:
    """Tests for activity data structure and integrity"""
    
    def test_all_activities_have_max_participants(self, client, reset_activities):
        """
        Test that all activities have a max_participants limit defined
        
        AAA Pattern:
        - Arrange: Fetch all activities
        - Act: Iterate through activities
        - Assert: Verify each has max_participants as positive integer
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity in activities.items():
            assert "max_participants" in activity
            assert isinstance(activity["max_participants"], int)
            assert activity["max_participants"] > 0
            
    def test_participants_list_is_always_list(self, client, reset_activities):
        """
        Test that participants is always a list (even if empty)
        
        AAA Pattern:
        - Arrange: Fetch all activities
        - Act: Check participants field type
        - Assert: Verify participants is always a list
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity in activities.items():
            assert "participants" in activity
            assert isinstance(activity["participants"], list)
            
    def test_participants_are_valid_emails(self, client, reset_activities):
        """
        Test that all participants have valid email format
        
        AAA Pattern:
        - Arrange: Fetch all activities
        - Act: Validate email format for each participant
        - Assert: Verify all follow email pattern
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity in activities.items():
            for email in activity["participants"]:
                assert "@" in email
                assert "." in email.split("@")[1]
                assert email.endswith(".edu")


class TestParticipantCapacity:
    """Tests for participant capacity constraints"""
    
    def test_activities_have_reasonable_capacity_limits(self, client, reset_activities):
        """
        Test that activities have reasonable maximum participant counts
        
        AAA Pattern:
        - Arrange: Fetch all activities
        - Act: Check capacity limits
        - Assert: Verify limits are between 10 and 30
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert - Reasonable capacity bounds
        for activity_name, activity in activities.items():
            max_participants = activity["max_participants"]
            assert 10 <= max_participants <= 30, \
                f"{activity_name} has unreasonable capacity: {max_participants}"
                
    def test_current_participants_not_exceed_max(self, client, reset_activities):
        """
        Test that current participants never exceed the maximum allowed
        
        AAA Pattern:
        - Arrange: Fetch all activities
        - Act: Compare current vs max participants
        - Assert: Verify current <= max for all activities
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity in activities.items():
            current_count = len(activity["participants"])
            max_count = activity["max_participants"]
            assert current_count <= max_count, \
                f"{activity_name} has {current_count} participants but max is {max_count}"


class TestMultipleSignups:
    """Tests for handling multiple signups and removals"""
    
    def test_multiple_different_students_can_signup_same_activity(self, client, reset_activities):
        """
        Test that multiple different students can sign up for same activity
        
        AAA Pattern:
        - Arrange: Multiple unique email addresses
        - Act: Sign up each student sequentially
        - Assert: Verify all are added to participants list
        """
        # Arrange
        activity_name = "Debate Club"
        students = [
            "debater1@mergington.edu",
            "debater2@mergington.edu",
            "debater3@mergington.edu"
        ]
        
        # Act
        responses = []
        for student_email in students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student_email}
            )
            responses.append(response)
        
        activities_result = client.get("/activities").json()
        
        # Assert
        for response in responses:
            assert response.status_code == 200
        
        for student_email in students:
            assert student_email in activities_result[activity_name]["participants"]
            
    def test_activities_with_existing_participants_tracked_correctly(self, client, reset_activities):
        """
        Test that activities with pre-existing participants maintain correct counts
        
        AAA Pattern:
        - Arrange: Activities with initial participants (from fixture)
        - Act: Fetch activities data
        - Assert: Verify initial participant counts are correct
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert - Chess Club should have 2 initial participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        
        # Programming Class should have 2 initial participants
        assert len(activities["Programming Class"]["participants"]) == 2
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
        assert "sophia@mergington.edu" in activities["Programming Class"]["participants"]
        
        # Gym Class should have 2 initial participants
        assert len(activities["Gym Class"]["participants"]) == 2
        
    def test_signup_increments_participant_count(self, client, reset_activities):
        """
        Test that each successful signup increases participant count by 1
        
        AAA Pattern:
        - Arrange: Get initial participant count for Science Club
        - Act: Sign up a new student and fetch activities again
        - Assert: Verify count increased by exactly 1
        """
        # Arrange
        activity_name = "Science Club"
        new_email = "scientist@mergington.edu"
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity_name]["participants"])
        
        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        updated_activities = client.get("/activities").json()
        updated_count = len(updated_activities[activity_name]["participants"])
        
        # Assert
        assert signup_response.status_code == 200
        assert updated_count == initial_count + 1
        
    def test_removal_decrements_participant_count(self, client, reset_activities):
        """
        Test that each removal decreases participant count by exactly 1
        
        AAA Pattern:
        - Arrange: Get initial participant count for Chess Club
        - Act: Remove a student and fetch activities again
        - Assert: Verify count decreased by exactly 1
        """
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity_name]["participants"])
        
        # Act
        removal_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email_to_remove}
        )
        updated_activities = client.get("/activities").json()
        updated_count = len(updated_activities[activity_name]["participants"])
        
        # Assert
        assert removal_response.status_code == 200
        assert updated_count == initial_count - 1
