function StatsGrid({ stats }) {
  return (
    <div className="stats-grid">
      <div className="stat-card">
        <h3>Total Emails</h3>
        <div className="value">{stats.total || 0}</div>
      </div>
      <div className="stat-card flagged">
        <h3>Flagged</h3>
        <div className="value">{stats.flagged || 0}</div>
      </div>
      <div className="stat-card blocked">
        <h3>Blocked</h3>
        <div className="value">{stats.blocked || 0}</div>
      </div>
      <div className="stat-card quarantined">
        <h3>Quarantined</h3>
        <div className="value">{stats.quarantined || 0}</div>
      </div>
      <div className="stat-card">
        <h3>Avg Processing (ms)</h3>
        <div className="value">{stats.avg_processing_time_ms || 0}</div>
      </div>
    </div>
  )
}

export default StatsGrid

