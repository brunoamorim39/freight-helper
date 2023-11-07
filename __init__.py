'''
Initializes important modules for running the application
'''
import json
import os

import boto3
from botocore.config import Config
from flask import Flask
from flask_login import LoginManager
from flask_jwt_extended import JWTManager

with open('./config/aws_config.json', encoding='utf-8') as config_file:
    aws_config = json.load(config_file)

boto_config = Config(
    region_name = aws_config.get("REGION_NAME")
)

dynamodb = boto3.resource('dynamodb', config=boto_config)
aws_lambda = boto3.client('lambda', config=boto_config)

app = Flask(__name__, static_folder='static')

with open('./config/app_config.json', encoding='utf-8') as config_file:
    app_config = json.load(config_file)

app.config['SECRET_KEY'] = app_config.get('SECRET_KEY')

# login_manager = LoginManager()
# login_manager.session_protection = 'strong'
# login_manager.login_view = 'login'
# login_manager.login_message = 'You must be logged in to access this.'
# login_manager.login_message_category = 'info'
# login_manager.init_app(app)

app.config['JWT_SECRET_KEY'] = app_config.get('JWT_SECRET_KEY')
jwt = JWTManager(app)

app.config['MAX_CONTENT_LENGTH'] = app_config.get('MANIFEST_MAX_CONTENT_LENGTH')
app.config['MANIFEST_UPLOAD_FOLDER'] = app_config.get('MANIFEST_UPLOAD_FOLDER')

with open('./config/api_config.json', 'r', encoding='utf-8') as api_config_file:
    api_config = json.load(api_config_file)

sendgrid_api_key = api_config.get('SENDGRID_API_KEY')
