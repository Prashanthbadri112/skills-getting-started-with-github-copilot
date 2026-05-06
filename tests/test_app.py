"""
FastAPI tests for the Mergington High School activities management system.

All tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and fixtures
- Act: Execute the code being tested
- Assert: Verify the results
"""

import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Reset the in-memory activities database to its original state
    before and after each test to prevent cross-test pollution.
    """
    # Store the original state before the test
    original_activities = copy.deepcopy(activities)
    
    yield
    
    # Restore the original state after the test
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index(client, reset_activities):
    """Test that GET / redirects to /static/index.html"""
    # Arrange
    # (client is already set up via fixture)
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client, reset_activities):
    """Test that GET /activities returns the complete activities dictionary"""
    # Arrange
    # (client is already set up via fixture)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_success(client, reset_activities):
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "newalex@mergington.edu"
    initial_participants = len(activities[activity_name]["participants"])
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_participants + 1


def test_signup_for_nonexistent_activity(client, reset_activities):
    """Test signup fails (404) when activity does not exist"""
    # Arrange
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_signed_up(client, reset_activities):
    """Test signup fails (400) when student is already signed up for activity"""
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]  # Use existing participant
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_success(client, reset_activities):
    """Test successful removal of a participant from an activity"""
    # Arrange
    activity_name = "Basketball Team"
    email = activities[activity_name]["participants"][0]  # Use existing participant
    initial_count = len(activities[activity_name]["participants"])
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count - 1


def test_remove_nonexistent_participant(client, reset_activities):
    """Test removal fails (404) when participant is not in the activity"""
    # Arrange
    activity_name = "Soccer Club"
    email = "nonexistent@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_from_nonexistent_activity(client, reset_activities):
    """Test removal fails (404) when activity does not exist"""
    # Arrange
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
