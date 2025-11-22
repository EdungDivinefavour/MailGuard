import { FiInbox, FiSend, FiEdit3, FiMail, FiX } from 'react-icons/fi'
import './Sidebar.css'

function Sidebar({ currentView, onViewChange, onCompose, userEmail, sidebarOpen, setSidebarOpen }) {
  const handleViewChange = (view) => {
    onViewChange(view)
    setSidebarOpen(false) // Close sidebar on mobile after selection
  }

  const handleCompose = () => {
    onCompose()
    setSidebarOpen(false) // Close sidebar on mobile after compose
  }

  return (
    <>
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}
      <div className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
      <div className="sidebar-header">
        <div className="logo">
          <FiMail className="logo-icon" />
          <span>Mail Client</span>
        </div>
        <button className="sidebar-close-btn" onClick={() => setSidebarOpen(false)}>
          <FiX />
        </button>
        <div className="user-email">{userEmail}</div>
      </div>
      
      <button className="compose-btn" onClick={handleCompose}>
        <FiEdit3 />
        <span>Compose</span>
      </button>

      <nav className="sidebar-nav">
        <button
          className={`nav-item ${currentView === 'inbox' ? 'active' : ''}`}
          onClick={() => handleViewChange('inbox')}
        >
          <FiInbox />
          <span>Inbox</span>
        </button>
        <button
          className={`nav-item ${currentView === 'sent' ? 'active' : ''}`}
          onClick={() => handleViewChange('sent')}
        >
          <FiSend />
          <span>Sent</span>
        </button>
      </nav>
    </div>
    </>
  )
}

export default Sidebar

