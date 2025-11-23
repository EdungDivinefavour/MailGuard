"""SSE notification service."""
import logging

from ...models import EmailLog

logger = logging.getLogger(__name__)


class EmailNotifier:
    """Handles SSE notifications for new emails."""
    
    def __init__(self, flask_app=None):
        pass
    
    def notify_new_email(self, email_log: EmailLog):
        """Notify clients about a new email via SSE."""
        try:
            from ...api.routes.events import add_event
            email_data = email_log.to_dict()
            add_event({
                'type': 'new_email',
                'data': email_data
            })
        except Exception as e:
            logger.error(f"Failed to emit SSE event: {e}", exc_info=True)

