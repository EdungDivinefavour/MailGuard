"""SMTP proxy server."""
import logging
from aiosmtpd.controller import Controller

from ..config import Config
from ..engines import DetectionEngine, ContentExtractor, PolicyEngine
from ..services import EmailProcessor

logger = logging.getLogger(__name__)


class SMTPProxy:
    """SMTP proxy server."""
    
    def __init__(self, app_context=None, flask_app=None):
        """Initialize SMTP proxy.
        
        Args:
            app_context: Flask application context (optional, for database access)
            flask_app: Flask application instance (for WebSocket emissions)
        """
        self.detection_engine = DetectionEngine(
            use_presidio=Config.USE_PRESIDIO
        )
        self.content_extractor = ContentExtractor(Config.TIKA_SERVER_URL)
        self.policy_engine = PolicyEngine(
            default_policy=Config.DEFAULT_POLICY,
            quarantine_dir=Config.QUARANTINE_DIR
        )
        self.controller = None
        self.app_context = app_context
        self.flask_app = flask_app
    
    def start(self):
        """Start the SMTP proxy server."""
        handler = EmailProcessor(
            self.detection_engine,
            self.content_extractor,
            self.policy_engine,
            flask_app=self.flask_app
        )
        
        self.controller = Controller(
            handler,
            hostname=Config.PROXY_HOST,
            port=Config.PROXY_PORT
        )
        
        # Check Tika availability
        if not self.content_extractor.is_tika_available():
            logger.warning("Tika server not available. Attachment extraction may fail.")
            logger.warning("Start Tika with: docker-compose up -d")
        
        logger.info(f"Starting SMTP proxy on {Config.PROXY_HOST}:{Config.PROXY_PORT}")
        logger.info(f"Forwarding to {Config.UPSTREAM_SMTP_HOST}:{Config.UPSTREAM_SMTP_PORT}")
        print(f"\n{'='*60}")
        print(f"✓ SMTP Proxy is listening on port {Config.PROXY_PORT}")
        print(f"✓ Ready to intercept emails...")
        print(f"✓ Handler type: {type(handler).__name__}")
        print(f"{'='*60}\n")
        
        self.controller.start()
        print(f"[DEBUG] Controller started: {self.controller}")
        print(f"[DEBUG] Controller running: {self.controller._thread.is_alive() if hasattr(self.controller, '_thread') else 'N/A'}\n")
    
    def stop(self):
        """Stop the SMTP proxy server."""
        if self.controller:
            self.controller.stop()
            logger.info("SMTP proxy stopped")
