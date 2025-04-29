"""
Handles user authentication with signup, login, and logout routes using Flask, MongoDB, and bcrypt.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import bcrypt
from auth import users_collection

# Create a Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handles sign up credentials and logic route.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        #validation for error pop up
        error_message = None

        # Validation
        if not all([username, email, password, confirm_password]):
            error_message = 'All fields are required'
        elif password != confirm_password:
            error_message = 'Passwords do not match'
        #Check if username or email already exists
        elif users_collection.find_one({"username": username}):
            error_message = 'Username already exists'

        elif users_collection.find_one({"email": email}):
            error_message = 'Email already exists'

        #If there's a validation error, show it and return the form
        if error_message:
            flash(error_message, 'error')
            return render_template('auth/signup.html')

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Create new user
        new_user = {
            "username": username,
            "email": email,
            "password": hashed_password
        }

        try:
            users_collection.insert_one(new_user)
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except (ValueError, IOError, KeyError) as error:
            flash(f'An error occurred: {str(error)}', 'error')
            return render_template('auth/signup.html')

    return render_template('auth/signup.html')




@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route with logic and getting username and password. 
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Find user by username
        user = users_collection.find_one({"username": username})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Set session
            session['username'] = username
            session['user_id'] = str(user['_id'])
            flash('Login successful!', 'success')

            #DOUBLE CHECK THIS WORKS, ORIGINALLY return redirect(url_for('home'))
            return redirect(url_for('main.home'))
        flash('Invalid username or password', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """ 
    Logoout functionality and route. 
    """
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
