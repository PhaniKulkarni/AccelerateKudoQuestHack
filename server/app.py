from dotenv import load_dotenv
from utils.extensions import oauth, mail
import os
from flask import Flask, redirect, url_for
from flask_cors import CORS
from config.config import Config
from flask_jwt_extended import JWTManager
from routes import register_blueprints
from services.db.agent_facts import load_agent_facts_to_db
from flask_apscheduler import APScheduler
from utils.delete_generated_doc import delete_old_files_job
import logging  

# Load environment variables
load_dotenv()

def run_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    jwt = JWTManager(app)
    mail.init_app(app)

    cors_config = {
        r"*": {
            "origins": [os.getenv("BASE_URL")],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "X-CSRF-Token"
            ],
            "supports_credentials": True  # Allow sending cookies
        }
    }
    CORS(app, resources=cors_config)

    # Initialize OAuth and register providers
    oauth.init_app(app)

    # Register Google OAuth provider
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )

    # Register Microsoft OAuth provider
    oauth.register(
        name='microsoft',
        client_id=os.getenv('MICROSOFT_CLIENT_ID'),
        client_secret=os.getenv('MICROSOFT_CLIENT_SECRET'),
        authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
        refresh_token_url=None,
        client_kwargs={
            'scope': 'openid profile email User.Read',  # Include 'User.Read'
            'response_type': 'code',
        },
    )

    # Register routes
    register_blueprints(app)

    # Base endpoint
    @app.get("/")
    def root():
        """
        Health probe endpoint.
        """    
        return {"status": "ready"}

    # Microsoft OAuth login route
    @app.route("/auth/microsoft")
    def microsoft_login():
        # Generate the full URL for the callback
        redirect_uri = url_for('microsoft_callback', _external=True)
        return oauth.microsoft.authorize_redirect(redirect_uri)

    @app.route('/auth/microsoft/callback')
    def microsoft_callback():
        try:
            # This should match the redirect URI registered in the Azure portal
            token = oauth.microsoft.authorize_access_token()
            user = oauth.microsoft.parse_id_token(token)
            return f'Logged in as: {user}'
        except Exception as e:
            return f"Error: {str(e)}"

    # Initialize APScheduler
    scheduler = APScheduler()
    scheduler.init_app(app)

    # Schedule the delete_old_files_job function
    scheduler.add_job(
        id='Delete Old Files',
        func=delete_old_files_job,
        trigger='cron',
        hour=0, minute=0  # Run daily at midnight
    )

    scheduler.start()

    return app, jwt, mail

# Run the app
app, jwt, mail = run_app()

if __name__ == '__main__':
    HOST = os.getenv("FLASK_RUN_HOST") or "0.0.0.0"
    PORT = os.getenv("FLASK_RUN_PORT") or 8000
    load_agent_facts_to_db()
    app.run(debug=True, host=HOST, port=PORT)
