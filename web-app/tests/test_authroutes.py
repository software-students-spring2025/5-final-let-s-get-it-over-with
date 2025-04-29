"""
Tests for routes.py under auth
"""

from unittest.mock import patch, MagicMock
import sys
import os
import pytest
import bcrypt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import app

# pylint: enable=wrong-import-position


@pytest.fixture(name="client")
def fixture_client():
    """Creates client used for testing"""
    app.app.config["TESTING"] = True
    with app.app.test_client() as client:
        yield client


def test_signup_success(client):
    """Tests successful signup"""
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123",
        "confirm_password": "password123",
    }

    mock_find_one = MagicMock(side_effect=[None, None])
    mock_insert_one = MagicMock()

    with patch("auth.routes.users_collection.find_one", mock_find_one), patch(
        "auth.routes.users_collection.insert_one", mock_insert_one
    ):

        response = client.post("/auth/signup", data=user_data, follow_redirects=False)

        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]
        mock_insert_one.assert_called_once()


def test_signup_existing_username(client):
    """Tests signup when username already exists"""
    user_data = {
        "username": "existinguser",
        "email": "email@example.com",
        "password": "password123",
        "confirm_password": "password123",
    }

    with patch(
        "auth.routes.users_collection.find_one",
        return_value={"username": "existinguser"},
    ):
        response = client.post("/auth/signup", data=user_data)
        assert response.status_code == 200


def test_login_success(client):
    """Tests sucessful login"""
    username = "validuser"
    password = "correctpass"
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    mock_user = {"_id": "someid", "username": username, "password": hashed_pw}

    with patch("auth.routes.users_collection.find_one", return_value=mock_user):
        response = client.post(
            "/auth/login", data={"username": username, "password": password}
        )
        assert response.status_code == 302


def test_login_failure(client):
    """Tests failed login"""
    with patch("auth.routes.users_collection.find_one", return_value=None):
        response = client.post(
            "/auth/login", data={"username": "user", "password": "wrong"}
        )
        assert response.status_code == 200  # stays on login page


def test_logout(client):
    """Tests logging out"""
    with client.session_transaction() as sess:
        sess["username"] = "test"
        sess["user_id"] = "123"

    response = client.get("/auth/logout")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
