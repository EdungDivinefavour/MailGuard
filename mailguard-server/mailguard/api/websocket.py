"""WebSocket event handlers."""
import logging
from flask import request
from flask_socketio import emit

logger = logging.getLogger(__name__)

# Track connected clients: {socket_id: {'ip': str, 'user_agent': str, 'connected_at': str}}
connected_clients = {}


def register_handlers(socketio_instance):
    """Register WebSocket handlers with the SocketIO instance."""
    
    @socketio_instance.on('connect')
    def handle_connect(auth):
        """Handle WebSocket connection."""
        from datetime import datetime
        
        socket_id = request.sid
        client_ip = request.remote_addr or request.environ.get('REMOTE_ADDR', 'unknown')
        user_agent = request.headers.get('User-Agent', 'unknown')
        connected_at = datetime.now().isoformat()
        
        # Store client information
        connected_clients[socket_id] = {
            'ip': client_ip,
            'user_agent': user_agent,
            'connected_at': connected_at
        }
        
        all_client_ids = list(connected_clients.keys())
        logger.info(
            f"✅ Client connected via WebSocket - "
            f"Socket ID: {socket_id}, "
            f"IP: {client_ip}, "
            f"User-Agent: {user_agent[:50]}, "
            f"Total connected clients: {len(connected_clients)} - "
            f"All Socket IDs: {all_client_ids}"
        )
        
        try:
            emit('connected', {
                'status': 'connected',
                'socket_id': socket_id,
                'total_clients': len(connected_clients),
                'connected_socket_ids': all_client_ids
            })
            logger.info(f"Sent connected event to client {socket_id}")
        except Exception as e:
            logger.error(f"Error emitting connect event: {e}")

    @socketio_instance.on('disconnect')
    def handle_disconnect():
        """Handle WebSocket disconnection."""
        socket_id = request.sid
        
        # Remove client from tracking
        client_info = connected_clients.pop(socket_id, None)
        
        remaining_client_ids = list(connected_clients.keys())
        if client_info:
            logger.info(
                f"❌ Client disconnected from WebSocket - "
                f"Socket ID: {socket_id}, "
                f"IP: {client_info.get('ip', 'unknown')}, "
                f"Total connected clients: {len(connected_clients)} - "
                f"Remaining Socket IDs: {remaining_client_ids}"
            )
        else:
            logger.info(
                f"❌ Client disconnected from WebSocket - "
                f"Socket ID: {socket_id} (not found in tracking), "
                f"Total connected clients: {len(connected_clients)} - "
                f"Remaining Socket IDs: {remaining_client_ids}"
            )


def emit_new_email(email_data):
    """Emit a new email event to all connected clients."""
    from . import socketio
    
    if socketio is not None:
        try:
            # Get count of connected clients before emitting
            client_count = len(connected_clients)
            
            # Broadcast to all connected clients
            socketio.emit('new_email', email_data, namespace='/')
            
            email_id = email_data.get('id', 'unknown')
            email_subject = email_data.get('subject', 'no subject')
            
            # Get all client IDs for logging
            client_ids = list(connected_clients.keys())
            
            logger.info(
                f"📧 Emitted new_email event - "
                f"Email ID: {email_id}, "
                f"Subject: {email_subject[:50]}, "
                f"Broadcasted to {client_count} connected client(s) - "
                f"Socket IDs: {client_ids}"
            )
        except Exception as e:
            logger.error(f"Error emitting new_email event: {e}", exc_info=True)
    else:
        logger.warning("SocketIO instance is None, cannot emit new_email event")


def get_connected_clients():
    """Get information about currently connected clients."""
    return {
        'count': len(connected_clients),
        'clients': dict(connected_clients)
    }

