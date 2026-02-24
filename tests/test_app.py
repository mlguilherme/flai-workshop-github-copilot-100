"""
Tests for the Mergington High School API.
"""

import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

# Snapshot of initial participant lists to restore after each test
_initial_participants = {name: list(data["participants"]) for name, data in activities.items()}


@pytest.fixture(autouse=True)
def reset_participants():
    """Restore the in-memory participants list to its original state after every test."""
    yield
    for name, original in _initial_participants.items():
        activities[name]["participants"] = list(original)


client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

class TestGetActivities:
    def test_returns_all_activities(self):
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9

    def test_activity_has_expected_fields(self):
        response = client.get("/activities")
        data = response.json()
        chess = data["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert "participants" in chess

    def test_chess_club_initial_participants(self):
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


# ---------------------------------------------------------------------------
# GET /  (redirect)
# ---------------------------------------------------------------------------

class TestRoot:
    def test_redirects_to_static(self):
        response = client.get("/", follow_redirects=False)
        assert response.status_code in (301, 302, 307, 308)
        assert response.headers["location"].endswith("/static/index.html")


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestSignup:
    def test_signup_success(self):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"},
        )
        assert response.status_code == 200
        assert "newstudent@mergington.edu" in response.json()["message"]
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_adds_participant_to_list(self):
        before = len(activities["Drama Club"]["participants"])
        client.post(
            "/activities/Drama Club/signup",
            params={"email": "new@mergington.edu"},
        )
        assert len(activities["Drama Club"]["participants"]) == before + 1

    def test_signup_duplicate_returns_400(self):
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_unknown_activity_returns_404(self):
        response = client.post(
            "/activities/Unknown Activity/signup",
            params={"email": "someone@mergington.edu"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestUnregister:
    def test_unregister_success(self):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 200
        assert "michael@mergington.edu" in response.json()["message"]
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_removes_participant_from_list(self):
        before = len(activities["Chess Club"]["participants"])
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": "daniel@mergington.edu"},
        )
        assert len(activities["Chess Club"]["participants"]) == before - 1

    def test_unregister_not_signed_up_returns_404(self):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "ghost@mergington.edu"},
        )
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_unknown_activity_returns_404(self):
        response = client.delete(
            "/activities/Unknown Activity/signup",
            params={"email": "someone@mergington.edu"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
