from .auth import auth_routes
from .AI import ai_routes
from .quiz_ai import quiz_ai_routes

def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(auth_routes)
    app.register_blueprint(ai_routes)
    app.register_blueprint(quiz_ai_routes)
    