#setup for usage as a package in main webapp file for importing

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes
