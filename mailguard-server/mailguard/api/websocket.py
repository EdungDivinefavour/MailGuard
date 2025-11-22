"""WebSocket event handlers."""
import logging
from flask_socketio import emit

logger = logging.getLogger(__name__)


def register_handlers(socketio_instance):
    """Register WebSocket handlers with the SocketIO instance."""
    
    @socketio_instance.on('connect')
    def handle_connect():
        """Handle WebSocket connection."""
        logger.info('Client connected via WebSocket')
        try:
            emit('connected', {'status': 'connected'})
            logger.info('Sent connected event to client')
        except Exception as e:
            logger.error(f"Error emitting connect event: {e}")

    @socketio_instance.on('disconnect')
    def handle_disconnect():
        """Handle WebSocket disconnection."""
        logger.info('Client disconnected from WebSocket')


def emit_new_email(email_data):
    """Emit a new email event to all connected clients."""
    from . import socketio
    from flask import has_app_context
    
    if socketio is not None:
        try:
            # If we're in an app context, use it; otherwise emit without context
            if has_app_context():
                socketio.emit('new_email', email_data, namespace='/')
            else:
                # Try to get the app from the notifier's stored app
                from ..services.websocket.notifier import _flask_app
                if _flask_app:
                    with _flask_app.app_context():
                        socketio.emit('new_email', email_data, namespace='/')
                else:
                    # Fallback: emit without context (should work with threading mode)
                    socketio.emit('new_email', email_data, namespace='/')
            logger.info(f"Emitted new_email event for email: {email_data.get('id', 'unknown')}")
        except Exception as e:
            logger.error(f"Error emitting new_email event: {e}", exc_info=True)
    else:
        logger.warning("SocketIO instance is None, cannot emit new_email event")

