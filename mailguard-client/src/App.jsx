import { useState, useEffect } from 'react'
import Header from './components/Header'
import StatsGrid from './components/StatsGrid'
import Filters from './components/Filters'
import EmailTable from './components/EmailTable'

function App() {
  const [stats, setStats] = useState({
    total: 0,
    flagged: 0,
    blocked: 0,
    quarantined: 0,
    avg_processing_time_ms: 0
  })
  const [emails, setEmails] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [flaggedOnly, setFlaggedOnly] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')

  const loadStats = async () => {
    try {
      const response = await fetch('/api/stats')
      const data = await response.json()
      setStats(data)
    } catch (err) {
      console.error('Error loading stats:', err)
    }
  }

  const loadEmails = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({
        page: currentPage,
        per_page: 50,
        flagged: flaggedOnly,
        view: 'admin',
        ...(statusFilter && { status: statusFilter })
      })

      const response = await fetch(`/api/emails?${params}`)
      const data = await response.json()

      setEmails(data.emails || [])
      setCurrentPage(data.page || 1)
      setTotalPages(data.pages || 1)
    } catch (err) {
      setError(`Error loading emails: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStats()
    loadEmails()
  }, [currentPage, flaggedOnly, statusFilter])

  // Auto-refresh every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      loadStats()
      loadEmails()
    }, 5000)

    return () => clearInterval(interval)
  }, [currentPage, flaggedOnly, statusFilter])

  const handleFilterChange = (newFlaggedOnly, newStatusFilter) => {
    setFlaggedOnly(newFlaggedOnly)
    setStatusFilter(newStatusFilter)
    setCurrentPage(1) // Reset to first page when filter changes
  }

  const handlePageChange = (delta) => {
    const newPage = currentPage + delta
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage)
    }
  }

  return (
    <div>
      <Header />
      <div className="container">
        <StatsGrid stats={stats} />
        <Filters
          flaggedOnly={flaggedOnly}
          statusFilter={statusFilter}
          onFilterChange={handleFilterChange}
          onRefresh={loadStats}
        />
        <EmailTable
          emails={emails}
          loading={loading}
          error={error}
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
        />
      </div>
    </div>
  )
}

export default App

