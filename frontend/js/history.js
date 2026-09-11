// ==========================================================================
// AgriSmart AI - Scan History Management
// ==========================================================================

function addToHistory(imgSrc, pred) {
    scanHistory.unshift({ imgSrc, pred, time: new Date() });
    if (scanHistory.length > 8) scanHistory.pop();
    renderHistory();
}

function renderHistory() {
    if (scanHistory.length === 0) return;
    historySection.style.display = 'block';
    historyGrid.innerHTML = '';
    scanHistory.forEach((item, i) => {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.innerHTML = `
            <img class="history-img" src="${item.imgSrc}" alt="Scan ${i + 1}">
            <div class="history-info">
                <div class="history-disease">${item.pred.condition}</div>
                <div class="history-conf">${item.pred.confidence}%</div>
            </div>
        `;
        div.addEventListener('click', () => {
            previewImg.src = item.imgSrc;
            previewContainer.style.display = 'block';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        historyGrid.appendChild(div);
    });
}
