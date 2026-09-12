// ==========================================================================
// AgriSmart AI v3.0 - UI Rendering (Organic Theme)
// ==========================================================================

function severityIcon(s) {
    const icons = {
        none: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        moderate: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
        high: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
        critical: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'
    };
    return icons[s] || icons['moderate'];
}
function severityLabel(s) {
    return { none: 'Healthy', moderate: 'Moderate', high: 'High Risk', critical: 'Critical' }[s] || s;
}
function severityPillClass(s) {
    return { none: 'sev-none', moderate: 'sev-moderate', high: 'sev-high', critical: 'sev-critical' }[s] || 'sev-moderate';
}
function barClass(conf) {
    if (conf >= 70) return '';
    if (conf >= 40) return 'amber';
    return 'red';
}

function renderResults(data) {
    const top = data.predictions[0];

    // Crop + Disease
    const cropTag = document.getElementById('resultPlant');
    cropTag.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:4px; vertical-align:-1px;"><path d="M12 22C12 22 12 12 22 12C22 12 12 12 12 2C12 2 12 12 2 12C2 12 12 12 12 22Z"/></svg>${top.plant}`;

    document.getElementById('resultDisease').textContent = top.condition;

    // Confidence
    document.getElementById('confidenceVal').textContent = `${top.confidence}%`;
    const bar = document.getElementById('confidenceBar');
    bar.className = 'conf-bar ' + barClass(top.confidence);
    setTimeout(() => { bar.style.width = `${Math.min(top.confidence, 100)}%`; }, 60);

    // Severity badge
    const badge = document.getElementById('severityBadge');
    badge.className = `severity-pill ${severityPillClass(top.severity)}`;
    badge.innerHTML = `${severityIcon(top.severity)} ${severityLabel(top.severity)}`;

    // Info panels
    document.getElementById('diseaseDescription').textContent = top.description;
    document.getElementById('diseaseTreatment').textContent = top.treatment;
    document.getElementById('diseasePrevention').textContent = top.prevention;

    // Critical alert banner
    const banner = document.getElementById('urgentBanner');
    if (top.severity === 'critical') {
        document.getElementById('urgentBannerText').textContent =
            `${top.condition} on ${top.plant}. Act within 24–48 hours!`;
        banner.style.display = 'block';
    } else {
        banner.style.display = 'none';
    }

    // Full Cure Plan accordion
    const cureDetails = document.getElementById('cureDetails');
    if (top.cure_plan) {
        const cp = top.cure_plan;

        const setItem = (id, label, val) => {
            const el = document.getElementById(id);
            if (val) {
                el.innerHTML = `<span class="cure-label">${label}</span>${val}`;
                el.style.display = 'block';
            } else {
                el.style.display = 'none';
            }
        };

        const icon = (svgStr) => `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:4px; vertical-align:-2px;">${svgStr}</svg>`;

        setItem('cureUrgency', icon('<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>') + 'Urgency', cp.urgency_level);
        setItem('cureRecovery', icon('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>') + 'Recovery', cp.recovery_timeline
            ? `${cp.recovery_timeline} (${cp.recovery_chance_pct || '—'}% chance)` : null);
        setItem('cureOrganic', icon('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>') + 'Organic Treatment', cp.organic_treatment);
        setItem('cureChem', icon('<path d="M10 2v7.31"/><path d="M14 9.3V1.99"/><path d="M8.5 2h7"/><path d="M14 9.3a6.5 6.5 0 1 1-4 0"/>') + 'Chemical Treatment', cp.chemical_treatment);
        setItem('cureContainment', icon('<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><line x1="20" y1="4" x2="8.12" y2="15.88"/><line x1="14.47" y1="14.48" x2="20" y2="20"/><line x1="8.12" y1="8.12" x2="12" y2="12"/>') + 'Containment', cp.containment_action || cp.cultural_management);

        const progEl = document.getElementById('curePrognosis');
        if (cp.prognosis_summary) {
            progEl.innerHTML = icon('<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>') + cp.prognosis_summary;
            progEl.style.display = 'block';
        } else {
            progEl.style.display = 'none';
        }

        cureDetails.style.display = 'block';

        const trigger = document.getElementById('cureDetailsToggle');
        const body = document.getElementById('cureDetailsBody');
        const chevron = document.getElementById('cureChevron');
        body.style.display = 'none';
        chevron.textContent = '＋';
        trigger.onclick = () => {
            const isOpen = body.style.display !== 'none';
            body.style.display = isOpen ? 'none' : 'grid';
            chevron.textContent = isOpen ? '＋' : '－';
        };
    } else {
        cureDetails.style.display = 'none';
    }

    // Alt predictions
    const altContainer = document.getElementById('altPredictions');
    altContainer.innerHTML = '';
    data.predictions.slice(1).forEach((pred) => {
        const div = document.createElement('div');
        div.className = 'alt-card';
        div.innerHTML = `
            <div class="alt-crop">${pred.plant}</div>
            <div class="alt-disease">${pred.condition}</div>
            <div class="alt-conf">${pred.confidence}% confidence</div>
            <div class="alt-track"><div class="alt-fill" data-conf="${pred.confidence}"></div></div>
        `;
        altContainer.appendChild(div);
    });
    setTimeout(() => {
        document.querySelectorAll('.alt-fill').forEach(b => {
            b.style.width = `${Math.min(parseFloat(b.dataset.conf), 100)}%`;
        });
    }, 100);

    // Set chatbot context
    currentDiagnosisContext = {
        disease_name: top.predicted_class || top.condition,
        crop: top.plant
    };
    setChatContext(top.condition, top.plant);
    document.getElementById('chatBubble').style.display = 'flex';
    document.getElementById('openChatFromResult').style.display = 'block';

    // Show results & hide educational content
    resultsSection.style.display = 'block';
    const edu = ['howItWorks', 'diseasesSection', 'tipsSection'];
    edu.forEach(id => { const el = document.getElementById(id); if (el) el.style.display = 'none'; });
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

}
