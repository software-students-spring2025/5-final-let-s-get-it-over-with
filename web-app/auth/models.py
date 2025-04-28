"""
Defines the User model with methods to create users, retrieve users by username, email, or ID, 
and verify passwords, interacting with a MongoDB users collection.
"""
import bcrypt
from bson.objectid import ObjectId
from auth import users_collection

class User:
    @staticmethod
    def create_user(username, email, password):
        """
        Create a new user with hashed password
        """
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user_data = {
            "username": username,
            "email": email,
            "password": hashed_password
        }

        result = users_collection.insert_one(user_data)
        return result.inserted_id

    @staticmethod
    def get_by_username(username):
        """
        Get user by username
        """
        return users_collection.find_one({"username": username})

    @staticmethod
    def get_by_email(email):
        """
        Get user by email
        """
        return users_collection.find_one({"email": email})

    @staticmethod
    def get_by_id(user_id):
        """
        Get user by ID
        """
        return users_collection.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def verify_password(stored_password, provided_password):
        """
        Verify if the provided password matches the stored hashed password
        """
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
