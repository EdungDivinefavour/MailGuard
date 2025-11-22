function Filters({ flaggedOnly, statusFilter, onFilterChange, onRefresh }) {
  const handleFlaggedChange = (e) => {
    onFilterChange(e.target.checked, statusFilter)
  }

  const handleStatusChange = (e) => {
    onFilterChange(flaggedOnly, e.target.value)
  }

  return (
    <div className="filters">
      <label>
        <input
          type="checkbox"
          checked={flaggedOnly}
          onChange={handleFlaggedChange}
        />
        Flagged only
      </label>
      <label>
        Status:
        <select value={statusFilter} onChange={handleStatusChange}>
          <option value="">All</option>
          <option value="processed">Processed</option>
          <option value="blocked">Blocked</option>
          <option value="quarantined">Quarantined</option>
          <option value="error">Error</option>
        </select>
      </label>
      <button onClick={onRefresh}>Refresh Stats</button>
    </div>
  )
}

export default Filters

