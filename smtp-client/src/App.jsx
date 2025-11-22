import React, { useState, useEffect } from 'react'
import { io } from 'socket.io-client'
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

  useEffect(() => {
    if (!userEmail) return

    // Use relative path if API_URL is empty (will go through Vite proxy)
    // Otherwise use the full URL
    const socketUrl = API_URL || window.location.origin
    console.log('🔌 Connecting to WebSocket at:', socketUrl)
    const socket = io(socketUrl, {
      transports: ['websocket', 'polling'],
      path: '/socket.io',
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5
    })

    socket.on('connect', () => {
      console.log('✅ Connected to WebSocket server, socket ID:', socket.id)
    })

    socket.on('connected', (data) => {
      console.log('✅ WebSocket connection confirmed:', data)
    })

    socket.onAny((eventName, ...args) => {
      console.log('🔔 Socket event received:', eventName, args)
    })

    socket.on('new_email', (emailData) => {
      console.log('📧 New email event received:', emailData)
      console.log('Current view:', currentView, 'User email:', userEmail)

      console.log('🔄 Reloading emails due to new email event...')
      loadEmails()
    })

    socket.on('error', (error) => {
      console.error('❌ WebSocket error:', error)
    })

    socket.on('disconnect', (reason) => {
      console.log('Disconnected from WebSocket server:', reason)
    })

    socket.on('reconnect', (attemptNumber) => {
      console.log('🔄 Reconnected to WebSocket server after', attemptNumber, 'attempts')
    })

    return () => {
      console.log('🔌 Disconnecting WebSocket...')
      socket.disconnect()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userEmail])

  const loadEmails = async () => {
    setLoading(true)
    try {
      // Use relative path if API_URL is empty (will go through Vite proxy)
      // Otherwise use the full URL
      const apiPath = API_URL ? `${API_URL}/api/emails?per_page=100` : '/api/emails?per_page=100'
      const response = await fetch(apiPath)

      if (!response.ok) {
        const errorText = await response.text()
        console.error(`API error (${response.status}):`, errorText)
        setToast({ message: `Failed to load emails: ${response.status} ${response.statusText}`, type: 'error' })
        setEmails([])
        return
      }

      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text()
        console.error('Response is not JSON:', text.substring(0, 100))
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

