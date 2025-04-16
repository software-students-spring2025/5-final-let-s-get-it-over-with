from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
from flask_login import LoginManager, current_user
import os
from auth.models import User
from auth import create_auth_blueprint 

app = Flask(__name__) 


#connects the app.py to config settings from config.py file in class named Config
app.config.from_object('config.Config') 

#initialize pyMongo, database already set to chatbots 
mongo = PyMongo(app)  

#initialize login manager 
login_manager = LoginManager() 

#configure for login 
login_manager.init_app(app)

#configures flask-login behavior when it gets to a protected route that uses @login_required decorator 
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def findUser(user_id):
  user_data = mongo.db.users.find_one({'_id' : user_id})  
  return User(user_data) if user_data else None




