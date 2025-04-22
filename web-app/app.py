from flask import Flask, render_template, redirect, url_for, session, flash, request, make_response, jsonify
from dotenv import load_dotenv
import os
import requests
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


@app.route('/chat')
def chat():
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
        

        #ERROR 
        response = make_response(render_template('chat.html', username=session['username']))
        # Set cache control headers
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return redirect(url_for('auth.login'))


@app.route("/generate-comment", methods=["POST"])
def proxy_generate_comment():
    print("Transfering control to the ml-client ...")

    try:
        print("DEBUG: sending info")
        ml_url = "http://ml-client:8000/generate-comment"  # Internal Docker service name
        data = request.get_json() or {}
        res = requests.post(ml_url, json=request.get_json())
        return res.json(), res.status_code

    except Exception as e:
        print("Error contacting ml-client:", e)
        return {"error": "ML service unreachable"}, 500   


@app.route("/process-question", methods=["POST"])
def proxy_process_question():
    print("Transferring control to ml-client process-question for speech recognition")
    
    try:
        print("DEBUG: sending info for speech")
        ml_url_speech = "http://ml-client:8000/process-question"
        data = request.get_json() or {}
        res = requests.post(ml_url_speech, json=data)
        return res.json(), res.status_code
    
    except Exception as e:
        print("Error contacting ml-client for speech processing:", e)
        return {"error": "ML speech service unreachable"}, 500


if __name__ == '__main__': 
    #RUNS ON 5001
    app.run(debug=True, host='0.0.0.0', port=5001)  