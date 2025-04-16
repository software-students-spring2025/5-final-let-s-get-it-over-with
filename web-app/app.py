from flask import Flask, render_template, redirect, url_for, session, flash, request, make_response
from dotenv import load_dotenv
import os

# Import auth blueprint
from auth.routes import auth_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# Register blueprint
app.register_blueprint(auth_bp)

# Add cache control headers to all responses
@app.after_request
def add_cache_control(response):
    # Prevent caching for authenticated pages
    if 'username' in session:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

@app.route('/')
def home():
    # Check if user is logged in
    if 'username' in session:
        # Additional check to verify if the session is still valid
        from auth import users_collection
        user_exists = users_collection.find_one({"username": session['username']})
        if not user_exists:
            # If user doesn't exist in database, clear session
            session.clear()
            flash('Your session has expired. Please log in again.', 'error')
            return redirect(url_for('auth.login'))
            
        response = make_response(render_template('dashboard.html', username=session['username']))
        # Set cache control headers
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return redirect(url_for('auth.login'))

if __name__ == '__main__': 
    #RUNS ON 5001
    app.run(host='0.0.0.0', port=5001)  
