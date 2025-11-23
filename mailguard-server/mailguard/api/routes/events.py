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
                for client_queue in _client_queues.values():
                    try:
                        client_queue.put(event_data, block=False)
                    except queue.Full:
                        logger.warning("Client queue full, skipping event")
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
        
        try:
            yield f"data: {json.dumps({'type': 'connected'})}\n\n"
            
            while True:
                try:
                    event_data = client_queue.get(timeout=30)
                    yield f"data: {json.dumps(event_data)}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
                except Exception as e:
                    logger.error(f"Error in SSE stream: {e}", exc_info=True)
                    break
        finally:
            with _clients_lock:
                _client_queues.pop(client_id, None)
    
    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',  # Disable buffering in nginx
            'Connection': 'keep-alive'
        }
    )

