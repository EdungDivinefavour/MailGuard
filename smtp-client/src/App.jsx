import { useState, useEffect } from 'react'
import { io } from 'socket.io-client'
import Sidebar from './components/Sidebar'
import EmailList from './components/EmailList'
import EmailView from './components/EmailView'
import ComposeEmail from './components/ComposeEmail'
import Toast from './components/Toast'
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
    // Load user email from localStorage or prompt
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

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!userEmail) return

    const socket = io('http://localhost:5001', {
      transports: ['websocket', 'polling']
    })

    socket.on('connect', () => {
      console.log('Connected to WebSocket server')
    })

    socket.on('new_email', (emailData) => {
      // Check if this email is relevant to the current user
      const isRelevant = 
        (currentView === 'inbox' && emailData.recipients && 
         emailData.recipients.some(r => r.toLowerCase().includes(userEmail.toLowerCase()))) ||
        (currentView === 'sent' && emailData.sender && 
         emailData.sender.toLowerCase().includes(userEmail.toLowerCase()))
      
      if (isRelevant || currentView === 'inbox' || currentView === 'sent') {
        // Reload emails to get the latest
        loadEmails()
      }
    })

    socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server')
    })

    return () => {
      socket.disconnect()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userEmail, currentView])

  const loadEmails = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/emails?per_page=100`)
      const data = await response.json()
      
      // Filter emails based on current view
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

