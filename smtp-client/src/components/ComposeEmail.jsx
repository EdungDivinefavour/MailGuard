import { useState, useRef } from 'react'
import { FiSend, FiX, FiPaperclip } from 'react-icons/fi'
import { API_URL } from '../config'
import './ComposeEmail.css'

function ComposeEmail({ userEmail, onSend, onCancel }) {
  const [to, setTo] = useState('')
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [attachments, setAttachments] = useState([])
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files)
    setAttachments(prev => [...prev, ...files])
  }

  const removeAttachment = (index) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }

  const handleSend = async () => {
    if (!to.trim()) {
      setError('Please enter a recipient email address')
      return
    }

    setSending(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('from', userEmail)
      formData.append('to', to)
      formData.append('subject', subject)
      formData.append('body', body)
      
      attachments.forEach((file, index) => {
        formData.append(`attachment_${index}`, file)
      })

      // Use relative path if API_URL is empty (will go through Vite proxy)
      const apiPath = API_URL ? `${API_URL}/api/send-email` : '/api/send-email'
      const response = await fetch(apiPath, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to send email')
      }

      // Reset form
      setTo('')
      setSubject('')
      setBody('')
      setAttachments([])
      onSend()
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="compose-email">
      <div className="compose-header">
        <h2>Compose Email</h2>
        <button className="close-btn" onClick={onCancel}>
          <FiX />
        </button>
      </div>
      
      <div className="compose-body">
        {error && (
          <div className="error-message">{error}</div>
        )}
        
        <div className="compose-field">
          <label>From</label>
          <input
            type="email"
            value={userEmail}
            disabled
            className="disabled-input"
          />
        </div>

        <div className="compose-field">
          <label>To</label>
          <input
            type="email"
            value={to}
            onChange={(e) => setTo(e.target.value)}
            placeholder="recipient@example.com"
            required
          />
        </div>

        <div className="compose-field">
          <label>Subject</label>
          <input
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="Email subject"
          />
        </div>

        <div className="compose-field">
          <label>Message</label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Type your message here..."
            rows={12}
          />
        </div>

        {attachments.length > 0 && (
          <div className="compose-field">
            <label>Attachments</label>
            <div className="attachments-list">
              {attachments.map((file, index) => (
                <div key={index} className="attachment-item">
                  <FiPaperclip />
                  <span>{file.name}</span>
                  <span className="file-size">
                    ({(file.size / 1024).toFixed(1)} KB)
                  </span>
                  <button
                    className="remove-attachment"
                    onClick={() => removeAttachment(index)}
                  >
                    <FiX />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="compose-actions">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            multiple
            style={{ display: 'none' }}
          />
          <button
            className="attach-btn"
            onClick={() => fileInputRef.current?.click()}
          >
            <FiPaperclip />
            Attach Files
          </button>
          <div className="action-buttons">
            <button className="cancel-btn" onClick={onCancel}>
              Cancel
            </button>
            <button
              className="send-btn"
              onClick={handleSend}
              disabled={sending || !to.trim()}
            >
              <FiSend />
              {sending ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ComposeEmail

