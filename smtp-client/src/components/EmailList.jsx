import { FiMenu } from 'react-icons/fi'
import './EmailList.css'

function EmailList({ emails, selectedEmail, onEmailSelect, loading, currentView, onMenuClick, newEmailIds = new Set() }) {
  const formatDate = (dateString) => {
    try {
      if (!dateString) return 'Unknown'

      // Handle ISO format strings
      const date = new Date(dateString)

      // Check if date is valid
      if (isNaN(date.getTime())) {
        return dateString
      }

      const now = new Date()
      const diffMs = now - date

      // If negative, it's in the future (shouldn't happen, but handle it)
      if (diffMs < 0) {
        return date.toLocaleDateString()
      }

      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)

      if (diffMins < 1) return 'just now'
      if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`
      if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
      if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
      return date.toLocaleDateString()
    } catch (e) {
      console.error('Date formatting error:', e, dateString)
      return dateString || 'Unknown'
    }
  }

  const getPreview = (email) => {
    if (email.subject) return email.subject
    return '(no subject)'
  }

  if (loading) {
    return (
      <div className="email-list">
        <div className="email-list-header">
          <h2>{currentView === 'inbox' ? 'Inbox' : 'Sent'}</h2>
        </div>
        <div className="loading-state">Loading emails...</div>
      </div>
    )
  }

  return (
    <div className="email-list">
      <div className="email-list-header">
        {onMenuClick && (
          <button className="menu-btn" onClick={onMenuClick}>
            <FiMenu />
          </button>
        )}
        <h2>{currentView === 'inbox' ? 'Inbox' : 'Sent'}</h2>
        <span className="email-count">{emails.length} {emails.length === 1 ? 'email' : 'emails'}</span>
      </div>
      <div className="email-list-content">
        {emails.length === 0 ? (
          <div className="empty-state">
            <p>No emails in {currentView}</p>
          </div>
        ) : (
          emails.map((email) => (
            <div
              key={email.id}
              className={`email-item ${selectedEmail?.id === email.id ? 'selected' : ''} ${newEmailIds.has(email.id) ? 'email-item-new' : ''}`}
              onClick={() => onEmailSelect(email)}
            >
              <div className="email-item-header">
                <div className="email-sender">
                  {currentView === 'inbox' ? email.sender :
                    (email.recipients && email.recipients[0]) || 'Unknown'}
                </div>
                <div className="email-date">{formatDate(email.timestamp)}</div>
              </div>
              <div className="email-subject">{getPreview(email)}</div>
              {email.attachment_count > 0 && (
                <div className="email-attachment-badge">
                  📎 {email.attachment_count}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default EmailList

