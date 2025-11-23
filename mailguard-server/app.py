"""Flask application entry point."""
from mailguard.api import create_app, init_db
from mailguard.config import Config

app = create_app()

if __name__ == '__main__':
    init_db()
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)
