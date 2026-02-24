"""
Tests for the DELETE /activities/{activity_name}/signup (unregister) endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

_initial_participants = {name: list(data["participants"]) for name, data in activities.items()}


@pytest.fixture(autouse=True)
def reset_participants():
    """Restore the in-memory participants list to its original state after every test."""
    yield
    for name, original in _initial_participants.items():
        activities[name]["participants"] = list(original)


client = TestClient(app)


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
        before = len(activities["Drama Club"]["participants"])
        client.delete(
            "/activities/Drama Club/signup",
            params={"email": "charlotte@mergington.edu"},
        )
        assert len(activities["Drama Club"]["participants"]) == before - 1

    def test_unregister_unknown_activity_returns_404(self):
        response = client.delete(
            "/activities/Unknown Activity/signup",
            params={"email": "someone@mergington.edu"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_student_not_signed_up_returns_404(self):
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "notregistered@mergington.edu"},
        )
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_same_student_twice_returns_404_on_second(self):
        client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        assert response.status_code == 404
