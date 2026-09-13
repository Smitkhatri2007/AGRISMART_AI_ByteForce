// ==========================================================================
// AgriSmart AI - Universal Multi-App Sharing & Kisan Diagnosis Card
// ==========================================================================

let latestDiagnosisForShare = null;

function setShareData(topResult, weatherContext) {
    latestDiagnosisForShare = {
        plant: topResult.plant,
        condition: topResult.condition,
        confidence: topResult.confidence,
        severity: topResult.severity,
        treatment: topResult.treatment || '',
        prevention: topResult.prevention || '',
        cure_plan: topResult.cure_plan || null,
        weather: weatherContext || null,
        timestamp: new Date().toLocaleString()
    };
}

function generateShareText() {
    if (!latestDiagnosisForShare) {
        return "AgriSmart AI — Intelligent Crop Disease Diagnostics and Advisory for Farmers.";
    }
    const d = latestDiagnosisForShare;
    const lines = [
        `🌱 *AgriSmart AI — Field Diagnosis Card*`,
        `━━━━━━━━━━━━━━━━━━━━━━`,
        `📅 *Date:* ${d.timestamp}`,
        `🌾 *Crop:* ${d.plant}`,
        `🦠 *Diagnosis:* ${d.condition}`,
        `🎯 *Confidence:* ${d.confidence}%`,
        `⚠️ *Severity:* ${(d.severity || 'Moderate').toUpperCase()}`,
        `━━━━━━━━━━━━━━━━━━━━━━`,
        `💊 *Recommended Treatment:*`,
        d.cure_plan && d.cure_plan.organic_treatment 
            ? `• Organic: ${d.cure_plan.organic_treatment.replace(/[*#]/g, '').substring(0, 120)}...`
            : `• ${d.treatment.substring(0, 120)}...`,
        d.cure_plan && d.cure_plan.chemical_treatment 
            ? `• Chemical: ${d.cure_plan.chemical_treatment.replace(/[*#]/g, '').substring(0, 120)}...`
            : '',
        `━━━━━━━━━━━━━━━━━━━━━━`,
        `🌦️ *Agri-Weather Advisory:*`,
        d.weather && d.weather.spray_window 
            ? `• Spray Window: ${d.weather.spray_window.verdict} (Wind: ${d.weather.current ? d.weather.current.wind_speed_kmh : 'Normal'} km/h)`
            : `• Check local weather conditions before chemical application.`,
        `━━━━━━━━━━━━━━━━━━━━━━`,
        `🔍 Verified with AgriSmart AI`
    ];
    return lines.filter(Boolean).join('\n');
}

/**
 * Universal share function - uses native Web Share API to send to ANY app
 * (WhatsApp, Telegram, SMS, Gmail, Signal, Notes, etc.)
 */
async function universalShare() {
    const text = generateShareText();
    const title = latestDiagnosisForShare 
        ? `AgriSmart Diagnosis: ${latestDiagnosisForShare.plant} - ${latestDiagnosisForShare.condition}` 
        : 'AgriSmart AI Diagnosis Report';

    // 1. Try Native Web Share API (Supported on Android, iOS, Windows, Mac Chrome/Edge/Safari)
    if (navigator.share) {
        try {
            await navigator.share({
                title: title,
                text: text,
                url: window.location.href
            });
            return;
        } catch (err) {
            // If user cancelled, do nothing; if error, fall back to share modal
            if (err.name === 'AbortError') return;
        }
    }

    // 2. Fallback: Open Universal Share Modal
    openShareModal(text);
}

function openShareModal(text) {
    let modal = document.getElementById('shareModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'shareModal';
        modal.className = 'modal-backdrop';
        modal.innerHTML = `
            <div class="modal-box" style="max-width: 440px;">
                <div class="modal-header">
                    <span>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:6px; vertical-align:-3px;"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
                        Share Diagnosis Report
                    </span>
                    <button class="modal-close-btn" onclick="document.getElementById('shareModal').classList.remove('open')">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    </button>
                </div>
                <p style="font-size:0.83rem; color:var(--text-muted); margin-bottom:1rem;">
                    Send this diagnosis card to your local agronomist, pesticide dealer, or farming group:
                </p>
                <div style="display:flex; flex-direction:column; gap:0.6rem;">
                    <a id="shareWhatsAppBtn" href="#" target="_blank" class="btn-share-channel whatsapp">
                        <span>💬 Share via WhatsApp</span>
                    </a>
                    <a id="shareTelegramBtn" href="#" target="_blank" class="btn-share-channel telegram">
                        <span>✈️ Share via Telegram</span>
                    </a>
                    <a id="shareSmsBtn" href="#" class="btn-share-channel sms">
                        <span>📱 Send as SMS / Text</span>
                    </a>
                    <button id="copyShareTextBtn" type="button" class="btn-share-channel copy">
                        <span>📋 Copy Report to Clipboard</span>
                    </button>
                </div>
            </div>`;
        document.body.appendChild(modal);
    }

    const encoded = encodeURIComponent(text);
    const waBtn = document.getElementById('shareWhatsAppBtn');
    if (waBtn) waBtn.href = `https://api.whatsapp.com/send?text=${encoded}`;

    const tgBtn = document.getElementById('shareTelegramBtn');
    if (tgBtn) tgBtn.href = `https://t.me/share/url?url=${encodeURIComponent(window.location.href)}&text=${encoded}`;

    const smsBtn = document.getElementById('shareSmsBtn');
    if (smsBtn) smsBtn.href = `sms:?body=${encoded}`;

    const copyBtn = document.getElementById('copyShareTextBtn');
    if (copyBtn) {
        copyBtn.onclick = () => {
            navigator.clipboard.writeText(text).then(() => {
                copyBtn.innerHTML = '<span>✅ Copied to Clipboard!</span>';
                setTimeout(() => {
                    copyBtn.innerHTML = '<span>📋 Copy Report to Clipboard</span>';
                    modal.classList.remove('open');
                }, 1500);
            });
        };
    }

    modal.classList.add('open');
}

/**
 * Print / Save 1-Page Kisan Diagnosis Card
 */
function printKisanCard() {
    window.print();
}

// Expose globally
window.setShareData = setShareData;
window.universalShare = universalShare;
window.printKisanCard = printKisanCard;
