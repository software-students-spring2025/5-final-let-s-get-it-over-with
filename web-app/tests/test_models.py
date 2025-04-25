import pytest
import bcrypt
import mongomock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bson.objectid import ObjectId
from unittest.mock import patch
import auth
import auth.models as models



# Mocked MongoDB collection
mock_db = mongomock.MongoClient().db
auth.users_collection = mock_db.users

class TestUser:

    def test_create_user(self):
        username = "testuser"
        email = "test@example.com"
        password = "securepassword"

        user_id = models.User.create_user(username, email, password)
        user = auth.users_collection.find_one({"_id": ObjectId(user_id)})

        assert user is not None
        assert user["username"] == username
        assert user["email"] == email
        assert bcrypt.checkpw(password.encode(), user["password"])

    def test_get_by_username(self):
        username = "john_doe"
        auth.users_collection.insert_one({
            "username": username,
            "email": "john@example.com",
            "password": bcrypt.hashpw("pass123".encode(), bcrypt.gensalt())
        })

        user = models.User.get_by_username(username)
        assert user is not None
        assert user["username"] == username

    def test_get_by_email(self):
        email = "jane@example.com"
        auth.users_collection.insert_one({
            "username": "jane_doe",
            "email": email,
            "password": bcrypt.hashpw("pass456".encode(), bcrypt.gensalt())
        })

        user = models.User.get_by_email(email)
        assert user is not None
        assert user["email"] == email

    def test_get_by_id(self):
        inserted_user = auth.users_collection.insert_one({
            "username": "unique_user",
            "email": "unique@example.com",
            "password": bcrypt.hashpw("unique123".encode(), bcrypt.gensalt())
        })

        user = models.User.get_by_id(str(inserted_user.inserted_id))
        assert user is not None
        assert user["_id"] == inserted_user.inserted_id

    def test_verify_password(self):
        password = "mysecret"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        assert models.User.verify_password(hashed, password)
        assert not models.User.verify_password(hashed, "wrongpassword")