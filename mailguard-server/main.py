"""Main entry point for MailGuard."""
import logging
import signal
import sys
import time
from threading import Thread

from mailguard.config import Config
from mailguard.proxy import SMTPProxy
from mailguard.api import create_app, init_db
from mailguard.services.websocket.notifier import set_flask_app

app = create_app()
from mailguard.api import socketio
set_flask_app(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mailguard.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_flask():
    """Run Flask in a separate thread."""
    socketio.run(app, host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG, allow_unsafe_werkzeug=True)

def main():
    """Start the proxy and UI."""
    logger.info("Starting MailGuard")
    logger.info(f"Configuration: {Config.DEFAULT_POLICY} policy, Tika: {Config.TIKA_SERVER_URL}")
    
    init_db()
    
    from mailguard.models import db
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")
    
    proxy = SMTPProxy(flask_app=app)
    proxy.app_context = app.app_context()
    proxy.start()
    
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    logger.info(f"Flask UI starting on http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    logger.info("MailGuard is running. Press Ctrl+C to stop.")
    
    def signal_handler(sig, frame):
        logger.info("Shutting down...")
        proxy.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main()

