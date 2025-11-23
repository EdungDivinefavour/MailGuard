"""Main entry point for MailGuard."""
import logging
import os
import signal
import sys
import time
from threading import Thread

# Enable remote debugging if DEBUG_MODE is set
if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
    import debugpy
    debugpy.listen(('0.0.0.0', 5678))
    print("🐛 Debugpy listening on port 5678. Waiting for debugger to attach...")
    # Uncomment the next line to wait for debugger before starting
    # debugpy.wait_for_client()
    print("🐛 Debugger attached!")

from mailguard.config import Config
from mailguard.proxy import SMTPProxy
from mailguard.api import create_app, init_db

app = create_app()

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
    app.run(
        host=Config.FLASK_HOST, 
        port=Config.FLASK_PORT, 
        debug=Config.FLASK_DEBUG,
        use_reloader=False  # Disable reloader when running in a thread
    )

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

