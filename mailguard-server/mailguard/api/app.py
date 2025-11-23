"""Flask API application factory."""
from flask import Flask
from flask_cors import CORS

from mailguard.config import Config
from mailguard.models import db


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    db.init_app(app)
    
    from .routes import emails, stats, attachments, events
    app.register_blueprint(emails.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(attachments.bp)
    app.register_blueprint(events.bp)
    
    return app


def init_db():
    """Initialize database tables."""
    app = create_app()
    with app.app_context():
        db.create_all()
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Database initialized")

