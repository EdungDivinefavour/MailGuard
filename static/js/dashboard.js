let currentPage = 1;
let totalPages = 1;

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

function getBadgeClass(status, policy) {
    if (status === 'blocked') return 'blocked';
    if (status === 'quarantined') return 'quarantined';
    if (policy === 'sanitize') return 'sanitized';
    if (policy === 'tag') return 'tagged';
    if (policy === 'block') return 'blocked';
    return '';
}

function formatDetections(detections) {
    if (!detections || detections.length === 0) return '';
    const types = [...new Set(detections.map(d => d.pattern_type))];
    return types.map(t => `<span class="detection-tag">${t}</span>`).join('');
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        document.getElementById('statTotal').textContent = stats.total || 0;
        document.getElementById('statFlagged').textContent = stats.flagged || 0;
        document.getElementById('statBlocked').textContent = stats.blocked || 0;
        document.getElementById('statQuarantined').textContent = stats.quarantined || 0;
        document.getElementById('statAvgTime').textContent = stats.avg_processing_time_ms || 0;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadEmails() {
    const flaggedOnly = document.getElementById('flaggedOnly').checked;
    const statusFilter = document.getElementById('statusFilter').value;

    document.getElementById('loading').style.display = 'block';
    document.getElementById('emailsTable').style.display = 'none';
    document.getElementById('error').style.display = 'none';

    try {
        const params = new URLSearchParams({
            page: currentPage,
            per_page: 50,
            flagged: flaggedOnly,
            ...(statusFilter && { status: statusFilter })
        });

        const response = await fetch(`/api/emails?${params}`);
        const data = await response.json();

        const tbody = document.getElementById('emailsBody');
        tbody.innerHTML = '';

        if (data.emails.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 2rem;">No emails found</td></tr>';
        } else {
            data.emails.forEach(email => {
                const row = document.createElement('tr');
                const badgeClass = getBadgeClass(email.status, email.policy_applied);
                const detections = formatDetections(email.detection_results);

                // Recipients is always an array from the API
                const recipientsDisplay = email.recipients && email.recipients.length > 0
                    ? email.recipients.slice(0, 2).join(', ')
                    : '-';

                row.innerHTML = `
                    <td>${formatDate(email.timestamp)}</td>
                    <td>${email.sender}</td>
                    <td>${recipientsDisplay}</td>
                    <td>${email.subject || '(no subject)'}</td>
                    <td><span class="badge ${badgeClass}">${email.status || 'processed'}</span></td>
                    <td>${email.policy_applied || '-'}</td>
                    <td><div class="detection-tags">${detections || '-'}</div></td>
                    <td>${email.attachment_count || 0}</td>
                    <td>${email.processing_time_ms ? email.processing_time_ms.toFixed(2) : '-'}</td>
                `;
                tbody.appendChild(row);
            });
        }

        currentPage = data.page;
        totalPages = data.pages;

        document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${totalPages}`;
        document.getElementById('prevPage').disabled = currentPage <= 1;
        document.getElementById('nextPage').disabled = currentPage >= totalPages;

        document.getElementById('loading').style.display = 'none';
        document.getElementById('emailsTable').style.display = 'table';
        document.getElementById('pagination').style.display = 'flex';

    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
        document.getElementById('error').textContent = `Error loading emails: ${error.message}`;
    }
}

function changePage(delta) {
    const newPage = currentPage + delta;
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        loadEmails();
    }
}

// Initial load
loadStats();
loadEmails();

// Auto-refresh every 30 seconds
setInterval(() => {
    loadStats();
    loadEmails();
}, 30000);

