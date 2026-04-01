import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Save and restore activities so each test starts with clean state."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_root_redirects_to_index():
    # Arrange
    # No setup needed
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange
    # Use existing activities from fixture
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    assert response.status_code == 200
    assert "Chess Club" in data
    for key in ("description", "schedule", "max_participants", "participants"):
        assert key in data["Chess Club"]


def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email in activities[activity_name]["participants"]


def test_signup_activity_not_found():
    # Arrange
    activity_name = "Nonexistent"
    email = "test@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_registered():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered in this activity
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Registered in Chess Club
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister", params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]
    assert email not in activities[activity_name]["participants"]


def test_unregister_activity_not_found():
    # Arrange
    activity_name = "Nonexistent"
    email = "test@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister", params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_registered():
    # Arrange
    activity_name = "Chess Club"
    email = "unknown@mergington.edu"  # Not registered in Chess Club
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister", params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"
