import { FiX, FiPaperclip, FiDownload } from 'react-icons/fi'
import { API_URL } from '../config'
import './EmailView.css'

function EmailView({ email, onClose }) {
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleString()
    } catch {
      return dateString
    }
  }

  return (
    <div className="email-view">
      <div className="email-view-header">
        <div className="email-view-title">
          <h2>{email.subject || '(no subject)'}</h2>
          <button className="close-btn" onClick={onClose}>
            <FiX />
          </button>
        </div>
        <div className="email-view-meta">
          <div className="meta-row">
            <span className="meta-label">From:</span>
            <span className="meta-value">{email.sender}</span>
          </div>
          <div className="meta-row">
            <span className="meta-label">To:</span>
            <span className="meta-value">
              {email.recipients && email.recipients.length > 0
                ? email.recipients.join(', ')
                : 'Unknown'}
            </span>
          </div>
          <div className="meta-row">
            <span className="meta-label">Date:</span>
            <span className="meta-value">{formatDate(email.timestamp)}</span>
          </div>
        </div>
      </div>
      <div className="email-view-body">
        <div className="email-content">
          {email.body_text || email.body || '(no content)'}
        </div>
        {((email.attachments && email.attachments.length > 0) || (email.attachment_names && email.attachment_names.length > 0)) && (
          <div className="email-attachments">
            <h3>Attachments:</h3>
            <div className="attachments-list">
              {(email.attachments || email.attachment_names.map(name => ({ filename: name, id: null }))).map((attachment, idx) => {
                const filename = attachment.filename || attachment
                const attachmentId = attachment.id || null

                if (attachmentId) {
                  return (
                    <a
                      key={attachmentId || idx}
                      href={API_URL ? `${API_URL}/api/attachments/${attachmentId}/download` : `/api/attachments/${attachmentId}/download`}
                      download={filename}
                      className="attachment-item"
                      title="Click to download"
                      style={{ cursor: 'pointer' }}
                    >
                      <FiPaperclip />
                      <span>{filename}</span>
                      <FiDownload className="download-icon" />
                    </a>
                  )
                } else {
                  return (
                    <div key={idx} className="attachment-item attachment-disabled">
                      <FiPaperclip />
                      <span>{filename}</span>
                    </div>
                  )
                }
              })}
            </div>
          </div>
        )}
        {email.detection_results && email.detection_results.length > 0 && (
          <div className="email-detections">
            <h3>Detections:</h3>
            <div className="detection-tags">
              {email.detection_results.map((detection, idx) => (
                <span key={idx} className="detection-tag">
                  {detection.pattern_type}
                </span>
              ))}
            </div>
          </div>
        )}
        {email.status && (
          <div className="email-status">
            <span className={`status-badge ${email.status}`}>
              {email.status}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

export default EmailView

