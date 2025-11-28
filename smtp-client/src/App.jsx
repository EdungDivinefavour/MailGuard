import React, { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import EmailList from './components/EmailList'
import EmailView from './components/EmailView'
import ComposeEmail from './components/ComposeEmail'
import Toast from './components/Toast'
import { API_URL } from './config'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState('inbox')
  const [selectedEmail, setSelectedEmail] = useState(null)
  const [composing, setComposing] = useState(false)
  const [emails, setEmails] = useState([])
  const [userEmail, setUserEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [newEmailIds, setNewEmailIds] = useState(new Set())

  useEffect(() => {
    const savedEmail = localStorage.getItem('userEmail')
    if (savedEmail) {
      setUserEmail(savedEmail)
    } else {
      const email = prompt('Enter your email address:')
      if (email) {
        setUserEmail(email)
        localStorage.setItem('userEmail', email)
      }
    }
  }, [])

  useEffect(() => {
    if (userEmail && currentView !== 'compose') {
      loadEmails()
    }
  }, [userEmail, currentView])

  const handleNewEmail = useCallback((newEmail) => {
    // Check if email matches current view filter
    const matchesView = currentView === 'inbox'
      ? newEmail.recipients && newEmail.recipients.some(r => r.toLowerCase().includes(userEmail.toLowerCase()))
      : newEmail.sender && newEmail.sender.toLowerCase().includes(userEmail.toLowerCase())

    if (matchesView) {
      setEmails(prevEmails => {
        // Check if email already exists (avoid duplicates)
        if (prevEmails.some(e => e.id === newEmail.id)) {
          return prevEmails
        }
        // Add new email at the top (emails are sorted by timestamp desc)
        const updated = [newEmail, ...prevEmails]
        // Mark as new for animation
        setNewEmailIds(prev => new Set([...prev, newEmail.id]))
        // Remove animation class after animation completes
        setTimeout(() => {
          setNewEmailIds(prev => {
            const next = new Set(prev)
            next.delete(newEmail.id)
            return next
          })
        }, 600) // Match animation duration
        return updated
      })
    }
  }, [currentView, userEmail])

  useEffect(() => {
    if (!userEmail) return

    const eventSourceUrl = API_URL
      ? `${API_URL}/api/events/stream`
      : '/api/events/stream'

    const eventSource = new EventSource(eventSourceUrl)

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'new_email' && data.data) {
          // Filter out blocked emails for this client
          if (data.data.status === 'blocked') {
            return
          }
          handleNewEmail(data.data)
        }
      } catch (error) {
        console.error('Error parsing SSE event:', error)
      }
    }

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error)
    }

    return () => {
      eventSource.close()
    }
  }, [userEmail, handleNewEmail])

  const loadEmails = async () => {
    setLoading(true)
    try {
      // Use relative path if API_URL is empty (will go through Vite proxy)
      // Otherwise use the full URL
      const apiPath = API_URL ? `${API_URL}/api/emails?per_page=100&view=smtp_client` : '/api/emails?per_page=100&view=smtp_client'
      const response = await fetch(apiPath)

      if (!response.ok) {
        setToast({ message: `Failed to load emails: ${response.status} ${response.statusText}`, type: 'error' })
        setEmails([])
        return
      }

      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        setToast({ message: 'Server returned invalid response format', type: 'error' })
        setEmails([])
        return
      }

      const data = await response.json()

      let filtered = data.emails || []
      if (currentView === 'inbox') {
        filtered = filtered.filter(email =>
          email.recipients && email.recipients.some(r => r.toLowerCase().includes(userEmail.toLowerCase()))
        )
      } else if (currentView === 'sent') {
        filtered = filtered.filter(email =>
          email.sender && email.sender.toLowerCase().includes(userEmail.toLowerCase())
        )
      }

      setEmails(filtered)
    } catch (error) {
      console.error('Error loading emails:', error)
      setToast({ message: `Error loading emails: ${error.message}`, type: 'error' })
      setEmails([])
    } finally {
      setLoading(false)
    }
  }

  const handleCompose = () => {
    setComposing(true)
    setSelectedEmail(null)
  }

  const handleEmailSent = () => {
    setComposing(false)
    setToast({ message: 'Email sent successfully!', type: 'success' })
    loadEmails()
  }

  const handleEmailSelect = (email) => {
    setSelectedEmail(email)
    setComposing(false)
  }

  const handleViewChange = (view) => {
    setCurrentView(view)
    setSelectedEmail(null)
    setComposing(false)
  }

  if (!userEmail) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '1.2rem'
      }}>
        Please enter your email address to continue
      </div>
    )
  }

  return (
    <div className="app">
      <Sidebar
        currentView={currentView}
        onViewChange={handleViewChange}
        onCompose={handleCompose}
        userEmail={userEmail}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />
      <div className="main-content">
        {composing ? (
          <ComposeEmail
            userEmail={userEmail}
            onSend={handleEmailSent}
            onCancel={() => setComposing(false)}
          />
        ) : (
          <>
            <EmailList
              emails={emails}
              selectedEmail={selectedEmail}
              onEmailSelect={handleEmailSelect}
              loading={loading}
              currentView={currentView}
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
              newEmailIds={newEmailIds}
            />
            {selectedEmail && (
              <EmailView
                email={selectedEmail}
                onClose={() => setSelectedEmail(null)}
              />
            )}
          </>
        )}
      </div>
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  )
}

export default App

