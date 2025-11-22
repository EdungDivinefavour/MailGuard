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


@bp.route('/websocket-clients', methods=['GET'])
def get_websocket_clients():
    """Get information about currently connected WebSocket clients."""
    try:
        from ...api.websocket import get_connected_clients
        clients_info = get_connected_clients()
        return jsonify(clients_info)
    except Exception as e:
        logger.error(f"Error getting WebSocket clients: {e}", exc_info=True)
        return jsonify({'error': str(e), 'count': 0, 'clients': {}}), 500

