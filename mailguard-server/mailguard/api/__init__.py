"""Flask API application factory."""
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from mailguard.config import Config
from mailguard.models import db

socketio = None


def create_app():
    """Create and configure Flask application."""
    global socketio
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/socket.io/*": {"origins": "*"}})
    
    db.init_app(app)
    
    from .routes import emails, stats, attachments
    app.register_blueprint(emails.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(attachments.bp)
    
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    from .websocket import register_handlers
    register_handlers(socketio)
    
    return app


def init_db():
    """Initialize database tables."""
    app = create_app()
    with app.app_context():
        db.create_all()
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Database initialized")

