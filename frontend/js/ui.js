// ==========================================================================
// AgriSmart AI v3.0 - UI Rendering (Organic Theme)
// ==========================================================================

// Parse markdown safely
function renderMd(text) {
    if (!text) return '';
    return (typeof marked !== 'undefined') ? marked.parse(text) : text.replace(/\n/g, '<br>');
}

// Populate crops dynamically on load
document.addEventListener('DOMContentLoaded', () => {
    const cropContainer = document.getElementById('aboutCropTags');
    if (cropContainer && window.AGRI_CONFIG && window.AGRI_CONFIG.SUPPORTED_CROPS) {
        cropContainer.innerHTML = '';
        window.AGRI_CONFIG.SUPPORTED_CROPS.forEach(c => {
            const span = document.createElement('span');
            span.className = 'crop-tag';
            span.textContent = c;
            cropContainer.appendChild(span);
        });
        const cropNumEl = document.getElementById('statCropNum');
        if (cropNumEl) cropNumEl.textContent = window.AGRI_CONFIG.SUPPORTED_CROPS.length;
        
        // Metrics
        if (window.AGRI_CONFIG.MODEL_METRICS) {
            const m = window.AGRI_CONFIG.MODEL_METRICS;
            const setM = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
            setM('metricArch', m.ARCHITECTURE);
            setM('metricF1', m.MACRO_F1);
            setM('metricTrain', m.TRAIN_DATASET);
            setM('metricEval', m.EVAL_DATASET);
            const gh = document.getElementById('metricGithub');
            if (gh) gh.href = m.GITHUB_URL;
        }
    }
    
    // Initial translation pass
    updateTranslations();
});

// Translation is handled by updateTranslations() below.
// translateElement() was removed (was a no-op stub).


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
    
    // Hide weather advice on new scan until loaded
    const weatherEl = document.getElementById('weatherAdvice');
    if (weatherEl) weatherEl.style.display = 'none';

    // Reset Sustainability badge
    const susBadge = document.getElementById('sustainabilityBadge');
    if (susBadge) susBadge.style.display = 'none';

    // Crop + Disease
    const cropTag = document.getElementById('resultPlant');
    cropTag.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:4px; vertical-align:-1px;"><path d="M12 22C12 22 12 12 22 12C22 12 12 12 12 2C12 2 12 12 2 12C2 12 12 12 12 22Z"/></svg>${top.plant}`;

    document.getElementById('resultDisease').textContent = top.condition;

    // Confidence
    document.getElementById('confidenceVal').textContent = `${top.confidence}%`;
    const confBar = document.getElementById('confidenceBar');
    
    // Confidence Bar Coloring
    confBar.className = 'conf-bar'; // reset
    if (window.AGRI_CONFIG) {
        if (top.confidence < window.AGRI_CONFIG.CONFIDENCE.MODERATE) confBar.classList.add('red');
        else if (top.confidence < window.AGRI_CONFIG.CONFIDENCE.HIGH) confBar.classList.add('amber');
    }
    
    confBar.style.width = '0%';
    setTimeout(() => { confBar.style.width = `${top.confidence}%`; }, 60);

    // Severity badge
    const badge = document.getElementById('severityBadge');
    badge.className = `severity-pill ${severityPillClass(top.severity)}`;
    badge.innerHTML = `${severityIcon(top.severity)} ${severityLabel(top.severity)}`;

    // Info panels (Markdown rendered)
    document.getElementById('diseaseDescription').innerHTML = renderMd(top.description);
    document.getElementById('diseaseTreatment').innerHTML = renderMd(top.treatment);
    document.getElementById('diseasePrevention').innerHTML = renderMd(top.prevention);

    // Critical alert banner
    const banner = document.getElementById('urgentBanner');
    if (top.severity === 'critical') {
        document.getElementById('urgentBannerText').textContent =
            `${top.condition} on ${top.plant}. Act within 24–48 hours!`;
        banner.style.display = 'block';
    } else {
        banner.style.display = 'none';
    }
    
    // Low Confidence / Uncertain Diagnosis
    const primaryCard = document.getElementById('primaryCard');
    const uncertainBanner = document.getElementById('uncertainDisclaimer');
    if (window.AGRI_CONFIG && top.confidence < window.AGRI_CONFIG.CONFIDENCE.UNCERTAIN) {
        primaryCard.style.opacity = '0.7';
        uncertainBanner.style.display = 'block';
    } else {
        primaryCard.style.opacity = '1';
        uncertainBanner.style.display = 'none';
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
        setItem('cureOrganic', icon('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>') + 'Organic Treatment', renderMd(cp.organic_treatment));
        setItem('cureChem', icon('<path d="M10 2v7.31"/><path d="M14 9.3V1.99"/><path d="M8.5 2h7"/><path d="M14 9.3a6.5 6.5 0 1 1-4 0"/>') + 'Chemical Treatment', renderMd(cp.chemical_treatment));
        setItem('cureContainment', icon('<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><line x1="20" y1="4" x2="8.12" y2="15.88"/><line x1="14.47" y1="14.48" x2="20" y2="20"/><line x1="8.12" y1="8.12" x2="12" y2="12"/>') + 'Containment', renderMd(cp.containment_action || cp.cultural_management));

        const progEl = document.getElementById('curePrognosis');
        if (cp.prognosis_summary) {
            progEl.innerHTML = icon('<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2 z"/>') + renderMd(cp.prognosis_summary);
            progEl.style.display = 'block';
        } else {
            progEl.style.display = 'none';
        }
        
        // Setup toggle logic
        const techToggle = document.getElementById('techToggleCheckbox');
        const simpleView = document.getElementById('simpleViewContainer');
        const techView = document.getElementById('technicalViewContainer');
        if (techToggle && simpleView && techView) {
            techToggle.checked = false; // default to simple
            simpleView.style.display = 'block';
            techView.style.display = 'none';
            techToggle.onchange = (e) => {
                if (e.target.checked) {
                    simpleView.style.display = 'none';
                    techView.style.display = 'block';
                } else {
                    simpleView.style.display = 'block';
                    techView.style.display = 'none';
                }
            };
        }

        // Sustainability Score Calculation
        let score = 100;
        let breakdown = "Base: 100";
        const chem = cp.chemical_treatment || '';
        if (chem && !chem.toLowerCase().includes('no chemical') && !chem.toLowerCase().includes('none')) {
            score -= 40;
            breakdown += "\nChemical Penalty: -40";
        }
        if (top.severity === 'critical') { score -= 20; breakdown += "\nSeverity Penalty: -20"; }
        else if (top.severity === 'high') { score -= 10; breakdown += "\nSeverity Penalty: -10"; }
        else if (top.severity !== 'none') { score -= 5; breakdown += "\nSeverity Penalty: -5"; }
        
        const org = cp.organic_treatment || '';
        if (org && org.trim() !== '') {
            score += 10;
            breakdown += "\nOrganic Bonus: +10";
        }
        
        score = Math.max(0, Math.min(100, score));
        breakdown += `\nTotal Eco Score: ${score}/100`;

        const susBadge = document.getElementById('sustainabilityBadge');
        if (susBadge) {
            susBadge.innerHTML = icon('<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>') + ` Eco Score: ${score}/100`;
            susBadge.title = breakdown;
            susBadge.style.backgroundColor = score > 75 ? '#f0fdf4' : (score > 40 ? '#fffbeb' : '#fef2f2');
            susBadge.style.color = score > 75 ? '#166534' : (score > 40 ? '#92400e' : '#991b1b');
            susBadge.style.borderColor = score > 75 ? '#bbf7d0' : (score > 40 ? '#fde68a' : '#fecaca');
            susBadge.style.display = 'inline-flex';
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
    const altGrid = document.getElementById('altPredictions');
    altGrid.innerHTML = '';
    
    // Filter by MIN_ALT threshold
    const minAlt = window.AGRI_CONFIG ? window.AGRI_CONFIG.CONFIDENCE.MIN_ALT : 2;
    const alts = data.predictions.slice(1).filter(a => a.confidence >= minAlt);
    
    if (alts.length > 0) {
        alts.forEach(a => {
            let colorClass = '';
            if (window.AGRI_CONFIG) {
                if (a.confidence < window.AGRI_CONFIG.CONFIDENCE.MODERATE) colorClass = 'red';
                else if (a.confidence < window.AGRI_CONFIG.CONFIDENCE.HIGH) colorClass = 'amber';
            }
            const el = document.createElement('div');
            el.className = 'alt-card';
            el.innerHTML = `
                <div class="alt-crop">${a.plant}</div>
                <div class="alt-disease">${a.condition}</div>
                <div class="alt-conf">${a.confidence}% match</div>
                <div class="alt-track"><div class="alt-fill ${colorClass}" style="width:${a.confidence}%"></div></div>
            `;
            altGrid.appendChild(el);
        });
    } else {
        altGrid.innerHTML = '<div style="color:var(--text-soft); font-size:0.8rem; padding: 0.5rem;">No other significant possibilities detected.</div>';
    }

    // Set chatbot context
    currentDiagnosisContext = {
        disease_name: top.predicted_class || top.condition,
        crop: top.plant
    };
    setChatContext(top.condition, top.plant);
    document.getElementById('chatBubble').style.display = 'flex';
    document.getElementById('openChatFromResult').style.display = 'block';
    
    // Share button setup
    const shareBtn = document.getElementById('shareResultBtn');
    shareBtn.style.display = 'block';
    shareBtn.onclick = () => {
        const text = `AgriSmart AI Diagnosis:\nCrop: ${top.plant}\nDisease: ${top.condition}\nConfidence: ${top.confidence}%\nTreatment: ${top.treatment.substring(0, 100)}...`;
        if (navigator.share) {
            navigator.share({ title: 'Diagnosis Result', text: text }).catch(console.error);
        } else {
            const url = `https://wa.me/?text=${encodeURIComponent(text)}`;
            window.open(url, '_blank');
        }
    };

    // Show results & hide educational content
    resultsSection.style.display = 'block';
    const edu = ['howItWorks', 'diseasesSection', 'tipsSection'];
    edu.forEach(id => { const el = document.getElementById(id); if (el) el.style.display = 'none'; });
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Fetch Weather (non-blocking)
    if (top.severity !== 'none') fetchWeatherAdvice();
}

async function fetchWeatherAdvice() {
    const weatherEl = document.getElementById('weatherAdvice');
    if (!weatherEl || !navigator.geolocation) return;
    
    navigator.geolocation.getCurrentPosition(async (pos) => {
        try {
            const { latitude, longitude } = pos.coords;
            const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current_weather=true`);
            const data = await res.json();
            if (data && data.current_weather) {
                const w = data.current_weather;
                let advice = `🌡️ Local Weather: ${w.temperature}°C.`;
                if (w.weathercode >= 51 && w.weathercode <= 67) {
                    advice += " Rain detected. Delay spraying treatments until clear to prevent runoff.";
                } else if (w.temperature > 32) {
                    advice += " High heat. Avoid spraying chemicals during peak afternoon hours.";
                } else if (w.windspeed > 25) {
                    advice += ` High wind (${w.windspeed} km/h). Avoid spraying to prevent drift.`;
                } else {
                    advice += " Conditions are currently optimal for applying any necessary treatments.";
                }
                weatherEl.innerHTML = `${advice} <span style="opacity: 0.7; margin-left: 0.25rem;">(Powered by <a href="https://open-meteo.com" target="_blank" style="color: inherit; text-decoration: underline;">Open-Meteo</a>)</span>`;
                weatherEl.style.display = 'block';
            }
        } catch (e) {
            console.error("Weather fetch failed:", e);
        }
    }, () => {});
}

// Export a robust updateTranslations function
function updateTranslations() {
    const lang = document.getElementById('languageSelect') ? document.getElementById('languageSelect').value : 'en';
    const dict = window.AGRI_I18N ? window.AGRI_I18N[lang] : null;
    if (!dict) return;

    // Helper to safely replace text while preserving icons
    const replaceText = (id, key) => {
        const el = document.getElementById(id);
        if (el && dict[key]) {
            // If it has SVG, replace the last text node
            let hasSvg = false;
            for (let node of el.childNodes) {
                if (node.nodeName.toLowerCase() === 'svg') hasSvg = true;
            }
            if (hasSvg) {
                // Remove all text nodes
                for (let i = el.childNodes.length - 1; i >= 0; i--) {
                    if (el.childNodes[i].nodeType === 3) el.removeChild(el.childNodes[i]);
                }
                el.appendChild(document.createTextNode(' ' + dict[key]));
            } else {
                el.innerHTML = dict[key];
            }
        }
    };

    // Replace straight HTML if no SVG
    const replaceHtml = (id, key) => {
        const el = document.getElementById(id);
        if (el && dict[key]) el.innerHTML = dict[key];
    };

    replaceHtml('footerText1', 'footer_text1');
    replaceHtml('footerText2', 'footer_text2');
    replaceText('analyzeBtnText', 'btn_analyze');
    replaceText('openChatFromResult', 'btn_ask_bot');
    replaceText('shareResultBtn', 'btn_share');
    replaceHtml('labelOtherPoss', 'label_other_possibilities');
    replaceHtml('otherPossDesc', 'other_possibilities_desc');
    replaceHtml('uncertainText', 'uncertain_disclaimer');
    
    replaceHtml('statDiseaseLbl', 'stat_disease');
    replaceHtml('statCropLbl', 'stat_crop');
    replaceHtml('statPredLbl', 'stat_pred');
    replaceHtml('statBotLbl', 'stat_bot');
    
    const input = document.getElementById('chatInput');
    if (input && dict['chat_placeholder']) {
        input.placeholder = dict['chat_placeholder'];
    }
}

