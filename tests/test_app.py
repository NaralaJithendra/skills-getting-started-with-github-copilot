from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def reset_activities():
    # restore initial participants to ensure test isolation
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        },
    })


def test_get_activities():
    reset_activities()
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_and_unsubscribe_flow():
    reset_activities()
    # signup a new user
    response = client.post(
        "/activities/Chess%20Club/signup?email=testuser@example.com"
    )
    assert response.status_code == 200
    assert response.json()[
        "message"] == "Signed up testuser@example.com for Chess Club"

    # verify participant is present
    resp = client.get("/activities")
    assert "testuser@example.com" in resp.json()["Chess Club"]["participants"]

    # attempt duplicate signup -> 400
    resp_dup = client.post(
        "/activities/Chess%20Club/signup?email=testuser@example.com"
    )
    assert resp_dup.status_code == 400

    # unregister
    resp_unreg = client.delete(
        "/activities/Chess%20Club/unregister?email=testuser@example.com"
    )
    assert resp_unreg.status_code == 200
    assert resp_unreg.json()[
        "message"] == "Unregistered testuser@example.com from Chess Club"

    # unregistering again should 404
    resp_unreg2 = client.delete(
        "/activities/Chess%20Club/unregister?email=testuser@example.com"
    )
    assert resp_unreg2.status_code == 404


def test_signup_nonexistent_activity():
    reset_activities()
    resp = client.post("/activities/Nonexistent/signup?email=a@b.com")
    assert resp.status_code == 404


def test_unregister_nonexistent_activity():
    reset_activities()
    resp = client.delete("/activities/Nonexistent/unregister?email=a@b.com")
    assert resp.status_code == 404
