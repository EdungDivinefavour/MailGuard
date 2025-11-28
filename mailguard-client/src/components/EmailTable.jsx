function EmailTable({ emails, loading, error, currentPage, totalPages, onPageChange }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  const getBadgeClass = (status, policy) => {
    if (status === 'blocked') return 'blocked'
    if (status === 'quarantined') return 'quarantined'
    if (status === 'flagged') return 'flagged'
    if (policy === 'sanitize') return 'sanitized'
    if (policy === 'tag') return 'tagged'
    if (policy === 'block') return 'blocked'
    return ''
  }

  const formatDetections = (detections) => {
    if (!detections || detections.length === 0) return null
    const types = [...new Set(detections.map(d => d.pattern_type))]
    return types.map((type, index) => (
      <span key={index} className="detection-tag">{type}</span>
    ))
  }

  if (loading) {
    return (
      <div className="emails-table">
        <div className="loading">Loading emails...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="emails-table">
        <div className="error">{error}</div>
      </div>
    )
  }

  return (
    <div className="emails-table">
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>From</th>
            <th>To</th>
            <th>Subject</th>
            <th>Status</th>
            <th>Policy</th>
            <th>Detections</th>
            <th>Attachments</th>
            <th>Time (ms)</th>
          </tr>
        </thead>
        <tbody>
          {emails.length === 0 ? (
            <tr>
              <td colSpan="9" style={{ textAlign: 'center', padding: '2rem' }}>
                No emails found
              </td>
            </tr>
          ) : (
            emails.map((email) => {
              const badgeClass = getBadgeClass(email.status, email.policy_applied)
              const recipientsDisplay = email.recipients && email.recipients.length > 0
                ? email.recipients.slice(0, 2).join(', ')
                : '-'

              return (
                <tr key={email.id}>
                  <td>{formatDate(email.timestamp)}</td>
                  <td>{email.sender}</td>
                  <td>{recipientsDisplay}</td>
                  <td>{email.subject || '(no subject)'}</td>
                  <td>
                    <span className={`badge ${badgeClass}`}>
                      {email.status || 'processed'}
                    </span>
                  </td>
                  <td>{email.policy_applied || '-'}</td>
                  <td>
                    <div className="detection-tags">
                      {formatDetections(email.detection_results) || '-'}
                    </div>
                  </td>
                  <td>{email.attachment_count || 0}</td>
                  <td>
                    {email.processing_time_ms
                      ? email.processing_time_ms.toFixed(2)
                      : '-'}
                  </td>
                </tr>
              )
            })
          )}
        </tbody>
      </table>
      {emails.length > 0 && (
        <div className="pagination">
          <button
            onClick={() => onPageChange(-1)}
            disabled={currentPage <= 1}
          >
            Previous
          </button>
          <span>Page {currentPage} of {totalPages}</span>
          <button
            onClick={() => onPageChange(1)}
            disabled={currentPage >= totalPages}
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

export default EmailTable

