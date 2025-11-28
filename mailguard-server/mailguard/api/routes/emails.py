"""Email API routes."""
from flask import Blueprint, jsonify, request
import logging
from sqlalchemy.orm import joinedload

from mailguard.models import EmailLog, db

logger = logging.getLogger(__name__)

bp = Blueprint('emails', __name__, url_prefix='/api/emails')


@bp.route('', methods=['GET'])
def get_emails():
    """Get email logs with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        flagged_only = request.args.get('flagged', 'false').lower() == 'true'
        status_filter = request.args.get('status', None)
        
        query = EmailLog.query.options(
            joinedload(EmailLog.recipients),
            joinedload(EmailLog.attachments)
        )
        
        # Filter based on client view
        view_mode = request.args.get('view', 'admin')
        if view_mode == 'smtp_client':
            query = query.filter(EmailLog.status != 'blocked')
            
        if flagged_only:
            query = query.filter(EmailLog.flagged == True)
        
        if status_filter:
            query = query.filter(EmailLog.status == status_filter)
        
        query = query.order_by(EmailLog.timestamp.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        emails_data = []
        for email in pagination.items:
            try:
                emails_data.append(email.to_dict())
            except Exception as e:
                logger.error(f"Error serializing email {email.id}: {e}", exc_info=True)
                continue
        
        return jsonify({
            'emails': emails_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception as e:
        logger.error(f"Error in get_emails: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:email_id>', methods=['GET'])
def get_email(email_id):
    """Get details for a specific email."""
    try:
        from sqlalchemy.orm import joinedload
        email = EmailLog.query.options(
            joinedload(EmailLog.recipients),
            joinedload(EmailLog.attachments)
        ).get_or_404(email_id)
        return jsonify(email.to_dict())
    except Exception as e:
        logger.error(f"Error in get_email: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

