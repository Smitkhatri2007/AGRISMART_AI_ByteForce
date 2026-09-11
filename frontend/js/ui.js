// ==========================================================================
// AgriSmart AI - UI Rendering & Severity Helpers
// ==========================================================================

// Severity helpers
function severityIcon(s) {
    return { none: '✅', moderate: '⚠️', high: '🔴', critical: '🚨' }[s] || '⚠️';
}

function severityLabel(s) {
    return { none: 'Healthy', moderate: 'Moderate', high: 'High Risk', critical: 'Critical' }[s] || s;
}

function barClass(conf) {
    if (conf >= 70) return '';
    if (conf >= 40) return 'amber';
    return 'red';
}

// Render Results View
function renderResults(data) {
    const top = data.predictions[0];

    // Primary card
    document.getElementById('resultPlant').textContent = `🌱 ${top.plant}`;
    document.getElementById('resultDisease').textContent = top.condition;
    document.getElementById('confidenceVal').textContent = `${top.confidence}%`;

    const bar = document.getElementById('confidenceBar');
    bar.className = 'bar-fill ' + barClass(top.confidence);
    setTimeout(() => {
        bar.style.width = `${Math.min(top.confidence, 100)}%`;
    }, 50);

    const badge = document.getElementById('severityBadge');
    badge.className = `severity-badge severity-${top.severity}`;
    badge.textContent = `${severityIcon(top.severity)} ${severityLabel(top.severity)}`;

    document.getElementById('diseaseDescription').textContent = top.description;
    document.getElementById('diseaseTreatment').textContent = top.treatment;
    document.getElementById('diseasePrevention').textContent = top.prevention;

    // Alt predictions (2nd and 3rd)
    const altContainer = document.getElementById('altPredictions');
    altContainer.innerHTML = '';
    data.predictions.slice(1).forEach((pred) => {
        const div = document.createElement('div');
        div.className = 'alt-card';
        div.innerHTML = `
            <div class="alt-plant">${pred.plant}</div>
            <div class="alt-disease">${pred.condition}</div>
            <div class="alt-conf">${pred.confidence}% confidence</div>
            <div class="alt-bar-track"><div class="alt-bar-fill" data-conf="${pred.confidence}"></div></div>
        `;
        altContainer.appendChild(div);
    });

    // Animate alt bars
    setTimeout(() => {
        document.querySelectorAll('.alt-bar-fill').forEach((b) => {
            b.style.width = `${Math.min(parseFloat(b.dataset.conf), 100)}%`;
        });
    }, 100);

    // Show results
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
