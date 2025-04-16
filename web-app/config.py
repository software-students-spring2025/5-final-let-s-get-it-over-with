#place to store all configuration settings for Flask app  
#use this to connect MongoDB database

import os 
from dotenv import load_dotenv 

#load env variables 
load_dotenv()  

class Config: 

  MONGO_URI = os.getenv("MONGO_URI")  
  SECRET_KEY = os.getenv("SECRET_KEY")

