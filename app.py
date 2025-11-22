"""Flask application for email interceptor UI."""
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import logging

from email_interceptor.config import Config
from email_interceptor.models import db, EmailLog

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Get paginated email logs."""
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
    """Get detailed email information."""
    email = EmailLog.query.get_or_404(email_id)
    return jsonify(email.to_dict())

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about intercepted emails."""
    total = EmailLog.query.count()
    flagged = EmailLog.query.filter(EmailLog.flagged == True).count()
    blocked = EmailLog.query.filter(EmailLog.status == 'blocked').count()
    quarantined = EmailLog.query.filter(EmailLog.status == 'quarantined').count()
    
    # Average processing time
    avg_time = db.session.query(db.func.avg(EmailLog.processing_time_ms)).scalar()
    avg_time = round(avg_time, 2) if avg_time else 0
    
    return jsonify({
        'total': total,
        'flagged': flagged,
        'blocked': blocked,
        'quarantined': quarantined,
        'avg_processing_time_ms': avg_time
    })


def init_db():
    """Initialize database tables."""
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")

if __name__ == '__main__':
    init_db()
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)

