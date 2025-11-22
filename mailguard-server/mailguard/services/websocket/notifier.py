"""WebSocket notification service."""
import logging

from ...models import EmailLog

logger = logging.getLogger(__name__)

_flask_app = None


def set_flask_app(app):
    """Set Flask app for WebSocket emissions."""
    global _flask_app
    _flask_app = app


class WebSocketNotifier:
    """Handles WebSocket notifications for real-time updates."""
    
    def __init__(self):
        """Initialize WebSocket notifier."""
        pass
    
    def notify_new_email(self, email_log: EmailLog):
        """
        Emit WebSocket update for new email.
        
        Args:
            email_log: EmailLog object to notify about
        """
        try:
            from ...api.websocket import emit_new_email
            
            email_data = email_log.to_dict()
            emit_new_email(email_data)
        except Exception as ws_err:
            logger.error(f"Could not emit WebSocket event: {ws_err}", exc_info=True)

