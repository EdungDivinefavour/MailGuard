"""Flask application entry point."""
from mailguard.api import create_app, socketio, init_db
from mailguard.config import Config

app = create_app()

if __name__ == '__main__':
    init_db()
    socketio.run(app, host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG, allow_unsafe_werkzeug=True)
