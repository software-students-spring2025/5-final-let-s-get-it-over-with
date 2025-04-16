from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from auth.models import User
from auth import auth_bp
import datetime
from app import app, mongo 

#get mongo instance from app to get database 
@app.route('/login', methods = ['GET', 'POST']) 
def login(): 

  #redirect logged-in users 
  if current_user.is_authenticated:  
    #FILLER 
    return redirect(url_for('dashboard '))  

  
  if request.method == 'POST': 
    username = request.form.get('username') 
    password = request.form.get('password')
    remember = 'remember' in request.form 

    if not username or not password:
      flash('Please enter both username and password', 'error')
      return render_template('auth/login.html')

    users = mongo.user_data 
     
