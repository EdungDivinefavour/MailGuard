"""Attachment API routes."""
from flask import Blueprint, jsonify, request, send_file
import logging
import os
import smtplib
from email.message import EmailMessage

from mailguard.config import Config
from mailguard.models import EmailAttachment

logger = logging.getLogger(__name__)

bp = Blueprint('attachments', __name__, url_prefix='/api')


@bp.route('/attachments/<int:attachment_id>/download', methods=['GET'])
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


@bp.route('/send-email', methods=['POST'])
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
            logger.info(f"📤 Sending email via SMTP proxy - From: {from_email}, To: {to_email}, Subject: {subject}")
            logger.info(f"📤 Connecting to SMTP proxy at {Config.PROXY_HOST}:{Config.PROXY_PORT}")
            with smtplib.SMTP(Config.PROXY_HOST, Config.PROXY_PORT) as server:
                logger.info(f"📤 SMTP connection established, sending message...")
                server.send_message(msg)
                logger.info(f"📤 Message sent successfully via SMTP proxy")
            logger.info(f"✅ Email sent from {from_email} to {to_email} - should be intercepted and processed by proxy")
            return jsonify({'success': True, 'message': 'Email sent successfully'})
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}", exc_info=True)
            return jsonify({'error': f'Failed to send email: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error in send_email endpoint: {e}")
        return jsonify({'error': str(e)}), 500

