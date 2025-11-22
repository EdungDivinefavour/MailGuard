"""Flask application for MailGuard API."""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
import smtplib
import os
from email.message import EmailMessage

from mailguard.config import Config
from mailguard.models import db, EmailLog, EmailAttachment

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for React frontend
CORS(app, resources={r"/api/*": {"origins": "*"}, r"/socket.io/*": {"origins": "*"}})

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

db.init_app(app)

# Global function to emit email updates
def emit_new_email(email_data):
    """Emit a new email event to all connected clients."""
    socketio.emit('new_email', email_data, namespace='/')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Get email logs with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    flagged_only = request.args.get('flagged', 'false').lower() == 'true'
    status_filter = request.args.get('status', None)
    
    query = EmailLog.query
    
    if flagged_only:
        query = query.filter(EmailLog.flagged == True)
    
    if status_filter:
        query = query.filter(EmailLog.status == status_filter)
    
    query = query.order_by(EmailLog.timestamp.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'emails': [email.to_dict() for email in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@app.route('/api/emails/<int:email_id>', methods=['GET'])
def get_email(email_id):
    """Get details for a specific email."""
    email = EmailLog.query.get_or_404(email_id)
    return jsonify(email.to_dict())

@app.route('/api/attachments/<int:attachment_id>/download', methods=['GET'])
def download_attachment(attachment_id):
    """Download an attachment file."""
    try:
        attachment = EmailAttachment.query.get_or_404(attachment_id)
        
        if not attachment.file_path or not os.path.exists(attachment.file_path):
            return jsonify({'error': 'Attachment file not found'}), 404
        
        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        logger.error(f"Error downloading attachment: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
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

@app.route('/api/send-email', methods=['POST'])
def send_email():
    """Send email via SMTP proxy."""
    try:
        # Get form data
        from_email = request.form.get('from')
        to_email = request.form.get('to')
        subject = request.form.get('subject', '')
        body = request.form.get('body', '')
        
        if not from_email or not to_email:
            return jsonify({'error': 'From and To email addresses are required'}), 400
        
        # Create email message
        msg = EmailMessage()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.set_content(body)
        
        # Add attachments
        attachment_keys = [key for key in request.files.keys() if key.startswith('attachment_')]
        for key in attachment_keys:
            file = request.files[key]
            if file and file.filename:
                file_data = file.read()
                msg.add_attachment(
                    file_data,
                    maintype='application',
                    subtype='octet-stream',
                    filename=file.filename
                )
        
        # Send via SMTP proxy
        try:
            with smtplib.SMTP(Config.PROXY_HOST, Config.PROXY_PORT) as server:
                server.send_message(msg)
            logger.info(f"Email sent from {from_email} to {to_email}")
            return jsonify({'success': True, 'message': 'Email sent successfully'})
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return jsonify({'error': f'Failed to send email: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error in send_email endpoint: {e}")
        return jsonify({'error': str(e)}), 500


def init_db():
    """Initialize database tables."""
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    logger.info('Client connected via WebSocket')
    emit('connected', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    logger.info('Client disconnected from WebSocket')

if __name__ == '__main__':
    init_db()
    socketio.run(app, host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG, allow_unsafe_werkzeug=True)

