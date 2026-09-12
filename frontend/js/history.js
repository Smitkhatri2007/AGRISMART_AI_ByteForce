// ==========================================================================
// AgriSmart AI v3.0 - Scan History (History Tab)
// ==========================================================================

function addToHistory(imgSrc, pred) {
    scanHistory.unshift({ imgSrc, pred, time: new Date() });
    if (scanHistory.length > 12) scanHistory.pop();

    // Update stats panel
    const statsEl = document.getElementById('historyStats');
    if (statsEl) {
        statsEl.style.display = 'flex';
        document.getElementById('hstatTotal').textContent = scanHistory.length;
        document.getElementById('hstatHealthy').textContent = scanHistory.filter(s => s.pred.severity === 'none').length;
        document.getElementById('hstatInfected').textContent = scanHistory.filter(s => s.pred.severity !== 'none').length;
    }

    renderHistory();
}


function renderHistory() {
    if (!historyGrid) return;

    if (scanHistory.length === 0) {
        historyGrid.innerHTML = `
            <div class="history-empty">
                <div class="history-empty-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                </div>
                <h3>No scans yet</h3>
                <p>Go to <strong>Diagnose</strong> and analyze your first leaf to see results here.</p>
                <button class="btn-primary" onclick="document.querySelector('[data-tab=diagnose]').click()" style="margin-top:1rem;">Start Diagnosing →</button>
            </div>`;
        return;
    }

    historyGrid.innerHTML = '';
    scanHistory.forEach((item, i) => {
        const div = document.createElement('div');
        div.className = 'history-card';
        div.innerHTML = `
            <img class="history-img" src="${item.imgSrc}" alt="Scan ${i + 1}">
            <div class="history-info">
                <div class="history-disease">${item.pred.condition}</div>
                <div class="history-conf">${item.pred.confidence}%</div>
            </div>
        `;
        div.addEventListener('click', () => {
            // Switch to diagnose tab and show image
            document.querySelector('[data-tab="diagnose"]').click();
            previewImg.src = item.imgSrc;
            previewContainer.style.display = 'block';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        historyGrid.appendChild(div);
    });
}
