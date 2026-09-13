// ==========================================================================
// AgriSmart AI v3.0 - Scan History (History Tab)
// ==========================================================================

document.addEventListener('DOMContentLoaded', loadHistory);

// --- Time-ago helper ---
function timeAgo(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    if (diff < 60)     return 'Just now';
    if (diff < 3600)   return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400)  return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
    return date.toLocaleDateString();
}

// --- Severity badge class ---
function severityClass(severity) {
    const s = (severity || 'none').toLowerCase();
    if (s === 'none')     return 'severity-none';
    if (s === 'low')      return 'severity-low';
    if (s === 'high')     return 'severity-high';
    if (s === 'critical') return 'severity-critical';
    return 'severity-medium';
}

// --- Confidence bar color ---
function confBarClass(conf) {
    if (conf >= 75) return 'bar-green';
    if (conf >= 45) return 'bar-amber';
    return 'bar-red';
}

// --- Load from localStorage ---
function loadHistory() {
    try {
        const stored = localStorage.getItem('agriHistory');
        if (stored) {
            scanHistory = JSON.parse(stored);
            updateStats();
            renderHistory();
        }
    } catch (e) {
        console.error('Failed to load history', e);
    }
}

// --- Save to localStorage ---
function saveHistory() {
    try {
        localStorage.setItem('agriHistory', JSON.stringify(scanHistory));
    } catch (e) {
        console.warn('History not saved (quota exceeded).');
    }
}

// --- Update stats bar ---
function updateStats() {
    const statsEl = document.getElementById('historyStats');
    const clearBtn = document.getElementById('clearAllHistoryBtn');

    if (scanHistory.length === 0) {
        if (statsEl) statsEl.style.display = 'none';
        if (clearBtn) clearBtn.style.display = 'none';
        return;
    }
    if (statsEl) {
        statsEl.style.display = 'flex';
        document.getElementById('hstatTotal').textContent = scanHistory.length;
        document.getElementById('hstatHealthy').textContent = scanHistory.filter(s => (s.pred.severity || 'none').toLowerCase() === 'none').length;
        document.getElementById('hstatInfected').textContent = scanHistory.filter(s => (s.pred.severity || 'none').toLowerCase() !== 'none').length;
    }
    if (clearBtn) clearBtn.style.display = 'inline-flex';
}

// --- Add a new scan to history ---
function addToHistory(imgSrc, pred) {
    scanHistory.unshift({ imgSrc, pred, time: new Date().toISOString() });
    if (scanHistory.length > 12) scanHistory.pop();
    updateStats();
    renderHistory();
    saveHistory();
}

// --- Delete a single entry ---
function deleteHistoryItem(index) {
    scanHistory.splice(index, 1);
    updateStats();
    renderHistory();
    saveHistory();
}

// --- Clear-all button ---
document.addEventListener('DOMContentLoaded', () => {
    const clearAllBtn = document.getElementById('clearAllHistoryBtn');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', () => {
            if (!confirm('Clear all scan history?')) return;
            scanHistory = [];
            updateStats();
            renderHistory();
            saveHistory();
        });
    }
});

// --- Render all history cards ---
function renderHistory() {
    if (!historyGrid) return;

    if (scanHistory.length === 0) {
        historyGrid.innerHTML = `
            <div class="history-empty" id="historyEmpty">
                <div class="history-empty-icon">🍃</div>
                <h3 data-i18n="history_empty_title">No scans yet</h3>
                <p data-i18n="history_empty_sub">Your scan history is securely saved on this device across sessions. Go to Diagnose and analyze your first leaf to see results here.</p>
                <button class="btn-primary" style="margin-top:1.5rem;" onclick="document.querySelector('.nav-tab[data-tab=\\'diagnose\\']').click()">
                    <span data-i18n="btn_start_diagnosing">Start Diagnosing →</span>
                </button>
            </div>`;
        return;
    }

    historyGrid.innerHTML = '';
    scanHistory.forEach((item, i) => {
        const conf = item.pred.confidence ?? 0;
        const severity = (item.pred.severity || 'none').toLowerCase();
        const sevLabel = severity === 'none' ? 'Healthy' : (severity.charAt(0).toUpperCase() + severity.slice(1));
        const crop = item.pred.plant || item.pred.crop || '';
        const disease = item.pred.condition || item.pred.disease_name || 'Unknown';
        const when = item.time ? timeAgo(item.time) : '';

        const div = document.createElement('div');
        div.className = 'history-card';
        div.innerHTML = `
            <div class="history-img-wrap">
                <img class="history-img" src="${item.imgSrc}" alt="Scan ${i + 1}" loading="lazy">
                <span class="history-severity-badge ${severityClass(severity)}">${sevLabel}</span>
                <button class="history-delete-btn" title="Remove" data-idx="${i}">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
            </div>
            <div class="history-info">
                ${crop ? `<div class="history-crop">${crop}</div>` : ''}
                <div class="history-disease" title="${disease}">${disease}</div>
                <div class="history-meta">
                    <div class="history-conf-bar-wrap">
                        <div class="history-conf-bar ${confBarClass(conf)}" style="width:${conf}%"></div>
                    </div>
                    <span class="history-conf-pct">${conf}%</span>
                </div>
                ${when ? `<div class="history-time">${when}</div>` : ''}
            </div>`;

        // Delete button — stop propagation so it doesn't trigger re-diagnose
        div.querySelector('.history-delete-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteHistoryItem(i);
        });

        // Click card → switch to diagnose and preload image
        div.addEventListener('click', () => {
            document.querySelector('[data-tab="diagnose"]').click();
            previewImg.src = item.imgSrc;
            previewContainer.style.display = 'block';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });

        historyGrid.appendChild(div);
    });
}


