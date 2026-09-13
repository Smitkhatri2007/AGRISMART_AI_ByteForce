// ==========================================================================
// AgriSmart AI - API Communication & Response Normalization
// ==========================================================================

const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000'
    : 'https://agrismart-ai-byteforce.onrender.com';

/**
 * Normalizes backend's DiseasePredictionResponse into the UI prediction model.
 */
function normalizePredictionResponse(raw) {
    if (raw.predictions && Array.isArray(raw.predictions)) {
        return raw;
    }

    const confPct = Math.round(raw.confidence > 1 ? raw.confidence : raw.confidence * 100);

    const rawSev = (raw.severity || '').toLowerCase();
    let severity = 'moderate';
    if (raw.is_healthy || rawSev === 'none') {
        severity = 'none';
    } else if (rawSev.includes('crit')) {
        severity = 'critical';
    } else if (rawSev.includes('high')) {
        severity = 'high';
    } else {
        severity = 'moderate';
    }

    let description = 'No disease description available.';
    if (raw.disease_description && raw.disease_description.description) {
        description = raw.disease_description.description;
    }

    let treatment = 'Maintain standard crop management and monitor foliage.';
    let prevention = 'Ensure proper plant spacing, balanced watering, and good air circulation.';

    if (raw.cure_plan) {
        const cure = raw.cure_plan;
        const org = cure.organic_treatment ? `🌱 Organic: ${cure.organic_treatment}` : '';
        const chem = cure.chemical_treatment ? `🧪 Chemical: ${cure.chemical_treatment}` : '';
        const timeline = cure.recovery_timeline ? `⏱️ Timeline: ${cure.recovery_timeline}` : '';
        treatment = [org, chem, timeline].filter(Boolean).join('\n\n');
        prevention = cure.containment_action || cure.cultural_management || prevention;
    } else if (raw.is_healthy) {
        treatment = 'Plant is healthy! No chemical fungicides or bactericides required.';
        prevention = 'Maintain routine scouting, balanced nutrient application, and preventative neem oil sprays.';
    }

    const primary = {
        plant: raw.crop || 'Crop',
        condition: raw.disease_name || raw.predicted_class || 'Unknown Condition',
        confidence: confPct,
        severity: severity,
        description: description,
        treatment: treatment,
        prevention: prevention,
        cure_plan: raw.cure_plan || null,
        predicted_class: raw.predicted_class || ''
    };

    const alts = (raw.top_k || []).slice(1).map((item) => {
        const probPct = Math.round(item.probability > 1 ? item.probability : item.probability * 100);
        const nameParts = (item.class || '').split(' ');
        const plant = nameParts[0] || 'Plant';
        const cond = nameParts.slice(1).join(' ') || item.class;
        return { plant, condition: cond, confidence: probPct };
    });

    return { predictions: [primary, ...alts], raw };
}

/**
 * Sends the selected leaf image to the AgriSmart backend for diagnosis.
 */
async function fetchPrediction(file) {
    const lang = languageSelect ? languageSelect.value : 'en';
    
    // 2.4 Client-Side Image Compression
    let compressedFile = file;
    try {
        compressedFile = await compressImage(file);
    } catch (e) {
        console.warn("Image compression failed, using original file", e);
    }

    const formData = new FormData();
    formData.append('image', compressedFile);
    formData.append('include_cure', 'true');
    formData.append('growth_stage', 'Growing');
    formData.append('language', lang);

    const resp = await fetch(`${API_BASE_URL}/api/v1/disease/predict`, {
        method: 'POST',
        body: formData
    });

    if (!resp.ok) {
        let errMessage = 'Server error';
        try {
            const err = await resp.json();
            errMessage = err.detail || err.error || errMessage;
        } catch (_) {}
        throw new Error(errMessage);
    }

    const rawData = await resp.json();
    return normalizePredictionResponse(rawData);
}

/**
 * Sends a chat message to the AgriBot chatbot endpoint.
 */
async function sendChatMessage(message, diseaseName, crop, history) {
    const lang = languageSelect ? languageSelect.value : 'en';
    const resp = await fetch(`${API_BASE_URL}/api/v1/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message,
            disease_name: diseaseName,
            crop: crop,
            conversation_history: history,
            language: lang
        })
    });

    if (!resp.ok) {
        let err = 'Chat server error';
        try { err = (await resp.json()).detail || err; } catch (_) {}
        throw new Error(err);
    }

    return await resp.json();
}

/**
 * Client-Side Image Compression helper
 */
function compressImage(file, maxWidth = 1000, quality = 0.8) {
    return new Promise((resolve, reject) => {
        if (!file.type.startsWith('image/')) {
            resolve(file); // Don't try to compress non-images
            return;
        }
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = event => {
            const img = new Image();
            img.src = event.target.result;
            img.onload = () => {
                let width = img.width;
                let height = img.height;

                if (width > maxWidth) {
                    height = Math.round((height * maxWidth) / width);
                    width = maxWidth;
                }

                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);

                canvas.toBlob(blob => {
                    if (!blob) {
                        reject(new Error('Canvas is empty'));
                        return;
                    }
                    const compressedFile = new File([blob], file.name, {
                        type: 'image/jpeg',
                        lastModified: Date.now()
                    });
                    resolve(compressedFile);
                }, 'image/jpeg', quality);
            };
            img.onerror = error => reject(error);
        };
        reader.onerror = error => reject(error);
    });
}
