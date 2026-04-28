import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index.html"""
        # Arrange
        # (No setup needed - endpoint is simple)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        # Arrange
        # (Test data already loaded via fixtures)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        # Arrange
        # (Test data provided by fixture)

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_participants_is_list(self, client):
        """Test that participants field is a list"""
        # Arrange
        # (Using fixture data)

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert isinstance(data["Chess Club"]["participants"], list)

    def test_activities_have_participants(self, client):
        """Test that activities have some participants"""
        # Arrange
        # (Fixture provides activities with initial participants)

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert len(data["Chess Club"]["participants"]) > 0


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        # Arrange
        new_email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_email in data["message"]
        assert activity_name in data["message"]

    def test_participant_added_after_signup(self, client):
        """Test that participant is actually added after signup"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert email in data[activity_name]["participants"]

    def test_signup_duplicate_email_error(self, client):
        """Test that signing up with duplicate email returns error"""
        # Arrange
        duplicate_email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={duplicate_email}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_activity_not_found_error(self, client):
        """Test that signup to non-existent activity returns 404"""
        # Arrange
        email = "student@mergington.edu"
        nonexistent_activity = "NonexistentClub"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_multiple_different_activities(self, client):
        """Test that same student can signup for multiple activities"""
        # Arrange
        email = "student@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act
        response1 = client.post(f"/activities/{activity1}/signup?email={email}")
        response2 = client.post(f"/activities/{activity2}/signup?email={email}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_signup_response_format(self, client):
        """Test that signup response has correct format"""
        # Arrange
        email = "testuser@mergington.edu"
        activity_name = "Drama Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert isinstance(data["message"], str)


class TestRemoveParticipantEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_successful_removal(self, client):
        """Test successful removal of a participant"""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_participant_removed_from_list(self, client):
        """Test that participant is actually removed from activity"""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.delete(f"/activities/{activity_name}/participants/{email}")
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert email not in data[activity_name]["participants"]

    def test_remove_participant_not_found_error(self, client):
        """Test that removing non-existent participant returns 404"""
        # Arrange
        nonexistent_email = "nonexistent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_remove_from_nonexistent_activity_error(self, client):
        """Test that removing from non-existent activity returns 404"""
        # Arrange
        email = "student@mergington.edu"
        nonexistent_activity = "NonexistentClub"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_remove_response_format(self, client):
        """Test that remove response has correct format"""
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert isinstance(data["message"], str)

    def test_remove_multiple_participants(self, client):
        """Test removing multiple participants from same activity"""
        # Arrange
        email1 = "michael@mergington.edu"
        email2 = "daniel@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.delete(f"/activities/{activity_name}/participants/{email1}")
        response = client.delete(
            f"/activities/{activity_name}/participants/{email2}"
        )
        data = client.get("/activities").json()

        # Assert
        assert response.status_code == 200
        assert len(data[activity_name]["participants"]) == 0


class TestIntegrationScenarios:
    """Integration tests for common user scenarios"""

    def test_signup_then_remove_participant(self, client):
        """Test complete flow: signup then remove participant"""
        # Arrange
        email = "integration@mergington.edu"
        activity_name = "Chess Club"

        # Act - Signup
        response_signup = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert - Signup successful
        assert response_signup.status_code == 200

        # Act - Verify signup
        activities = client.get("/activities").json()

        # Assert - Participant added
        assert email in activities[activity_name]["participants"]

        # Act - Remove
        response_remove = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert - Removal successful
        assert response_remove.status_code == 200

        # Act - Verify removal
        activities = client.get("/activities").json()

        # Assert - Participant removed
        assert email not in activities[activity_name]["participants"]

    def test_signup_and_other_participants_remain(self, client):
        """Test that adding participant doesn't affect others"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newperson@mergington.edu"
        initial_activities = client.get("/activities").json()
        initial_participants = initial_activities[activity_name]["participants"]
        initial_count = len(initial_participants)

        # Act
        client.post(f"/activities/{activity_name}/signup?email={new_email}")
        updated_activities = client.get("/activities").json()
        updated_participants = updated_activities[activity_name]["participants"]

        # Assert
        assert len(updated_participants) == initial_count + 1
        for participant in initial_participants:
            assert participant in updated_participants

