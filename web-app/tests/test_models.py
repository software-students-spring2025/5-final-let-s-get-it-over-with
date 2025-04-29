"""
Tests for models.py under auth
"""

from unittest.mock import patch, MagicMock
import sys
import os
import bcrypt
from bson.objectid import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from auth.models import User

# pylint: enable=wrong-import-position


def test_verify_password_correct():
    """Tests password verfication for correct password"""
    password = "testpass"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    assert User.verify_password(hashed, password) is True


def test_verify_password_incorrect():
    """Tests password verfication for incorrect password"""
    password = "testpass"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    assert User.verify_password(hashed, "wrongpass") is False


@patch("auth.models.users_collection")
def test_create_user(mock_users_collection):
    """Tests creating a new user"""
    username = "testuser"
    email = "testuser@example.com"
    password = "testpasasword"

    mock_insert_result = MagicMock()
    mock_insert_result.inserted_id = "mock_id"
    mock_users_collection.insert_one.return_value = mock_insert_result

    user_id = User.create_user(username, email, password)

    args, _ = mock_users_collection.insert_one.call_args
    inserted_data = args[0]

    assert inserted_data["username"] == username
    assert inserted_data["email"] == email
    assert bcrypt.checkpw(password.encode(), inserted_data["password"])
    assert user_id == "mock_id"


@patch("auth.models.users_collection")
def test_get_by_username(mock_users_collection):
    """Tests retrieving a stored user"""
    mock_user = {"username": "tester", "email": "tester@example.com"}
    mock_users_collection.find_one.return_value = mock_user

    user = User.get_by_username("tester")

    mock_users_collection.find_one.assert_called_once_with({"username": "tester"})
    assert user == mock_user


@patch("auth.models.users_collection")
def test_get_by_email(mock_users_collection):
    """Tests retrieving a user by email"""
    mock_user = {"username": "testuser2", "email": "testuser2@example.com"}
    mock_users_collection.find_one.return_value = mock_user

    user = User.get_by_email("testuser2@example.com")

    mock_users_collection.find_one.assert_called_once_with(
        {"email": "testuser2@example.com"}
    )
    assert user == mock_user


@patch("auth.models.users_collection")
def test_get_by_id(mock_users_collection):
    """Tests retrieving a user by id"""
    fake_id = ObjectId()
    mock_user = {"_id": fake_id, "username": "user_id", "email": "id@example.com"}
    mock_users_collection.find_one.return_value = mock_user

    user = User.get_by_id(str(fake_id))

    mock_users_collection.find_one.assert_called_once_with({"_id": fake_id})
    assert user == mock_user
