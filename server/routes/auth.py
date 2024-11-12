"""This module defines the routes for user authentication and registration"""

import logging
from utils.extensions import oauth, mail
from flask import Blueprint, request, jsonify, current_app, url_for, redirect, session
import os
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from services.azure_mongodb import MongoDBClient
from models.user import User as UserModel
from dotenv import load_dotenv
from pydantic import ValidationError
from email_validator import validate_email, EmailNotValidError
from secrets import token_urlsafe
from flask_mail import Message
from utils.reset_tokens import generate_reset_token, verify_reset_token

# Load environment variables from .env file
load_dotenv()

# Create a blueprint for the auth routes
auth_routes = Blueprint("auth", __name__)

# Route for user registration
@auth_routes.post('/user/signup')
def signup():
    try:
        logging.info("Starting user registration process")
        user_data = request.get_json()
        logging.info(f"Received user data: {user_data}")

        user = UserModel(**user_data)

        db_client = MongoDBClient.get_client()
        db = db_client[MongoDBClient.get_db_name()]

        # Check if user already exists with the same username or email
        logging.info("Checking for existing users")
        existing_user = db['users'].find_one({"$or": [{"username": user.username}, {"email": user.email}]})
        if existing_user:
            logging.info("User already exists")
            return jsonify({"error": "User with this username or email already exists"}), 409
        
        hashed_password = generate_password_hash(user.password)
        user_data['password'] = hashed_password
        result = db['users'].insert_one(user_data)
        if result:
            logging.info("User registration successful")
            user_id = result.inserted_id
            access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(hours=72))

            return jsonify({"message": "User registered successfully", "access_token": access_token, "userId": str(user_id)}), 201
        else:
            logging.error("Failed to save user")
            return jsonify({"error": "Failed to register user"}), 500
    except Exception as e:
        logging.error(f"Exception during registration: {str(e)}")
        return jsonify({"error": str(e)}), 400

# Route for user login
@auth_routes.post('/user/login')
def login():
    try:
        identifier = request.json.get('identifier', None)
        password = request.json.get('password', None)
        
        if not identifier or not password:
            return jsonify({"msg": "Missing identifier or password"}), 400

        try:
            validate_email(identifier)
            is_email = True
        except EmailNotValidError:
            is_email = False

        if is_email:
            user = UserModel.find_by_email(identifier)
        else:
            user = UserModel.find_by_username(identifier)

        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=72))
            return jsonify(access_token=access_token, userId=str(user.id)), 200
        else:
            return jsonify({"msg": "Invalid identifier or password"}), 401
        
    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        return jsonify({"error": ve.errors()}), 400
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Route for user logout
@auth_routes.post('/user/logout')
@jwt_required()
def logout():
    jwt_id = get_jwt_identity()
    logging.info(f"User {jwt_id} logged out successfully")
    return jsonify({"msg": "Logout successful"}), 200

# Route to start Google OAuth
@auth_routes.route('/auth/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    nonce = token_urlsafe(16)
    session['oauth_nonce'] = nonce
    logging.info(f"Redirect URI: {redirect_uri}")
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)

# Route to handle Google OAuth callback
@auth_routes.route('/auth/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        nonce = session.pop('oauth_nonce', None)

        if not nonce:
            logging.error("Nonce not found in session")
            return jsonify({'error': 'Session expired or invalid'}), 400

        claims_options = {
            'iss': {
                'values': ['https://accounts.google.com', 'accounts.google.com'],
            },
            'aud': {
                'values': [os.getenv('GOOGLE_CLIENT_ID')],
            },
            'nonce': {
                'values': [nonce],
            },
        }
       
        user_info = oauth.google.parse_id_token(token, nonce=nonce, claims_options=claims_options)
        email = user_info.get('email')
        name = user_info.get('name')
        google_id = user_info.get('sub')

        if not email:
            return jsonify({'error': 'Failed to retrieve email from Google'}), 400

        user = UserModel.find_by_email(email)

        if not user:
            user_data = {
                'username': email.split('@')[0],
                'email': email,
                'name': name,
                'google_id': google_id,
            }
            db_client = MongoDBClient.get_client()
            db = db_client[MongoDBClient.get_db_name()]
            result = db['users'].insert_one(user_data)
            user_id = result.inserted_id
        else:
            user_id = user.id

        access_token = create_access_token(
            identity=str(user_id),
            expires_delta=timedelta(hours=72)
        )

        frontend_redirect_url = os.getenv('BASE_URL')  
        redirect_url = f"{frontend_redirect_url}/auth/auth-callback?token={access_token}&userId={user_id}"
        return redirect(redirect_url, code=302)

    except Exception as e:
        logging.error(f"Google login error: {str(e)}")
        return jsonify({'error': 'Authentication failed'}), 500

# Route to start Microsoft OAuth
@auth_routes.route('/auth/microsoft')
def microsoft_login():
    redirect_uri = url_for('auth.microsoft_callback', _external=True)
    nonce = token_urlsafe(16)
    session['oauth_nonce'] = nonce
    logging.info(f"Redirect URI: {redirect_uri}")
    return oauth.microsoft.authorize_redirect(redirect_uri, nonce=nonce)

# Route to handle Microsoft OAuth callback
@auth_routes.route('/auth/microsoft/callback')
def microsoft_callback():
    try:
        token = oauth.microsoft.authorize_access_token()
        nonce = session.pop('oauth_nonce', None)

        if not nonce:
            logging.error("Nonce not found in session")
            return jsonify({'error': 'Session expired or invalid'}), 400

        claims_options = {
            'iss': {
                'values': ['https://login.microsoftonline.com', 'login.microsoftonline.com'],
            },
            'aud': {
                'values': [os.getenv('MICROSOFT_CLIENT_ID')],
            },
            'nonce': {
                'values': [nonce],
            },
        }

        user_info = oauth.microsoft.parse_id_token(token, nonce=nonce, claims_options=claims_options)
        email = user_info.get('email')
        name = user_info.get('name')
        microsoft_id = user_info.get('sub')

        if not email:
            return jsonify({'error': 'Failed to retrieve email from Microsoft'}), 400

        user = UserModel.find_by_email(email)

        if not user:
            user_data = {
                'username': email.split('@')[0],
                'email': email,
                'name': name,
                'microsoft_id': microsoft_id,
            }
            db_client = MongoDBClient.get_client()
            db = db_client[MongoDBClient.get_db_name()]
            result = db['users'].insert_one(user_data)
            user_id = result.inserted_id
        else:
            user_id = user.id

        access_token = create_access_token(
            identity=str(user_id),
            expires_delta=timedelta(hours=72)
        )

        frontend_redirect_url = os.getenv('BASE_URL')  
        redirect_url = f"{frontend_redirect_url}/auth/auth-callback?token={access_token}&userId={user_id}"
        return redirect(redirect_url, code=302)

    except Exception as e:
        logging.error(f"Microsoft login error: {str(e)}")
        return jsonify({'error': 'Authentication failed'}), 500

# Route to request password reset
@auth_routes.post('/user/request_reset')
def request_password_reset():
    try:
        data = request.get_json()
        email = data.get('email')
        if not email:
            logging.warning("No email provided in the request")
            return jsonify({"error": "Email is required"}), 400
        
        user = UserModel.find_by_email(email)
        if not user:
            logging.warning("User with the provided email not found")
            return jsonify({"error": "No user found with that email"}), 404

        # Generate and send reset email
        reset_token = generate_reset_token(user.id)
        reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
        msg = Message('Password Reset Request', recipients=[email])
        msg.body = f"Please click the following link to reset your password: {reset_url}"
        mail.send(msg)

        return jsonify({"message": "Password reset email sent"}), 200
    except Exception as e:
        logging.error(f"Error in password reset request: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500
