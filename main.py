"""Main entry point for MailGuard."""
import logging
import signal
import sys
import time
from threading import Thread

from mailguard.config import Config
from mailguard.proxy import SMTPProxy
from app import app, init_db

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
    """Run Flask app in a separate thread."""
    init_db()
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG, use_reloader=False)

def main():
    """Main function to start proxy and UI."""
    logger.info("Starting MailGuard")
    logger.info(f"Configuration: {Config.DEFAULT_POLICY} policy, Tika: {Config.TIKA_SERVER_URL}")
    
    # Initialize database
    init_db()
    
    # Set up database context for SMTP proxy
    from mailguard.models import db
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")
    
    # Start SMTP proxy (will use app context when needed)
    # Pass app context to proxy for database access
    proxy = SMTPProxy()
    proxy.app_context = app.app_context()  # Store app context for database access
    proxy.start()
    
    # Start Flask UI in separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    logger.info(f"Flask UI starting on http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    logger.info("MailGuard is running. Press Ctrl+C to stop.")
    
    # Handle shutdown
    def signal_handler(sig, frame):
        logger.info("Shutting down...")
        proxy.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main()

