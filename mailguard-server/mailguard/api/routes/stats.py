"""Statistics API routes."""
from flask import Blueprint, jsonify
import logging

from mailguard.models import db, EmailLog

logger = logging.getLogger(__name__)

bp = Blueprint('stats', __name__, url_prefix='/api/stats')


@bp.route('', methods=['GET'])
def get_stats():
    """Get stats about intercepted emails."""
    total = EmailLog.query.count()
    flagged = EmailLog.query.filter(EmailLog.flagged == True).count()
    blocked = EmailLog.query.filter(EmailLog.status == 'blocked').count()
    quarantined = EmailLog.query.filter(EmailLog.status == 'quarantined').count()
    
    # Calculate average processing time
    avg_time = db.session.query(db.func.avg(EmailLog.processing_time_ms)).scalar()
    avg_time = round(avg_time, 2) if avg_time else 0
    
    return jsonify({
        'total': total,
        'flagged': flagged,
        'blocked': blocked,
        'quarantined': quarantined,
        'avg_processing_time_ms': avg_time
    })


@bp.route('/sse-clients', methods=['GET'])
def get_sse_clients():
    """Get information about currently connected SSE clients."""
    try:
        from .events import _client_queues, _clients_lock
        with _clients_lock:
            count = len(_client_queues)
        return jsonify({'count': count})
    except Exception as e:
        logger.error(f"Error getting SSE clients: {e}", exc_info=True)
        return jsonify({'error': str(e), 'count': 0}), 500


@bp.route('/test-sse', methods=['POST'])
def test_sse():
    """Test endpoint to manually trigger an SSE event."""
    try:
        from .events import add_event
        
        test_data = {
            'type': 'new_email',
            'data': {
                'id': 'test',
                'subject': 'Test SSE Event',
                'sender': 'test@example.com',
                'recipients': ['test@example.com'],
                'body': 'This is a test event'
            }
        }
        
        add_event(test_data)
        
        return jsonify({'success': True, 'message': 'Test event emitted'})
    except Exception as e:
        logger.error(f"Error in test_sse: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

