"""Server-Sent Events (SSE) API routes."""
import json
import logging
import queue
import threading
import uuid
from flask import Blueprint, Response, stream_with_context

logger = logging.getLogger(__name__)

bp = Blueprint('events', __name__, url_prefix='/api/events')

# Dictionary mapping client_id to their event queue
_client_queues = {}
_clients_lock = threading.Lock()


def add_event(event_data):
    """Add an event to be sent to all connected SSE clients."""
    try:
        with _clients_lock:
            if _client_queues:
                # Add event to each client's queue
                for client_queue in _client_queues.values():
                    try:
                        client_queue.put(event_data, block=False)
                    except queue.Full:
                        # Queue is full, skip this client (they're too slow)
                        logger.warning("Client queue full, skipping event")
                logger.info(f"Added event to SSE queues: {event_data.get('type', 'unknown')} for {len(_client_queues)} clients")
            else:
                logger.debug(f"No SSE clients connected, event discarded: {event_data.get('type', 'unknown')}")
    except Exception as e:
        logger.error(f"Error adding event to SSE queue: {e}", exc_info=True)


@bp.route('/stream', methods=['GET'])
def stream_events():
    """Stream events to client using Server-Sent Events."""
    def event_stream():
        client_id = str(uuid.uuid4())
        client_queue = queue.Queue(maxsize=100)  # Limit queue size to prevent memory issues
        
        with _clients_lock:
            _client_queues[client_id] = client_queue
        
        logger.info(f"SSE client connected: {client_id} (total: {len(_client_queues)})")
        
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'client_id': client_id})}\n\n"
            
            # Keep connection alive and send events
            while True:
                try:
                    # Wait for event with timeout to send keepalive
                    event_data = client_queue.get(timeout=30)
                    yield f"data: {json.dumps(event_data)}\n\n"
                except queue.Empty:
                    # Send keepalive comment to prevent connection timeout
                    yield ": keepalive\n\n"
                except Exception as e:
                    logger.error(f"Error in SSE stream for client {client_id}: {e}", exc_info=True)
                    break
        finally:
            with _clients_lock:
                _client_queues.pop(client_id, None)
            logger.info(f"SSE client disconnected: {client_id} (remaining: {len(_client_queues)})")
    
    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',  # Disable buffering in nginx
            'Connection': 'keep-alive'
        }
    )

