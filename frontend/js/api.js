// ==========================================================================
// AgriSmart AI - API Communication & Response Normalization
// ==========================================================================

// Base URL configuration:
// - Local development: points to local FastAPI backend on port 8000
// - Production (Vercel): points to your deployed Render backend
const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000'
    : 'https://agrismart-ai-byteforce.onrender.com';

/**
 * Normalizes backend's DiseasePredictionResponse into the UI prediction model.
 */
function normalizePredictionResponse(raw) {
    // If backend already returned normalized predictions format
    if (raw.predictions && Array.isArray(raw.predictions)) {
        return raw;
    }

    const confPct = Math.round(raw.confidence > 1 ? raw.confidence : raw.confidence * 100);

    // Map severity to match UI badge styles: 'none', 'moderate', 'high', 'critical'
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

    // Description text from Gemini Pro or expert fallback
    let description = 'No disease description available.';
    if (raw.disease_description && raw.disease_description.description) {
        description = raw.disease_description.description;
    }

    // Treatment & Prevention from Gemini cure plan or defaults
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
        prevention: prevention
    };

    // Alternative predictions from top_k candidates
    const alts = (raw.top_k || []).slice(1).map((item) => {
        const probPct = Math.round(item.probability > 1 ? item.probability : item.probability * 100);
        const nameParts = (item.class || '').split(' ');
        const plant = nameParts[0] || 'Plant';
        const cond = nameParts.slice(1).join(' ') || item.class;
        return {
            plant: plant,
            condition: cond,
            confidence: probPct
        };
    });

    return {
        predictions: [primary, ...alts],
        raw: raw
    };
}

/**
 * Sends the selected leaf image to the AgriSmart backend for diagnosis.
 */
async function fetchPrediction(file) {
    const formData = new FormData();
    // Backend expects field 'image' (UploadFile)
    formData.append('image', file);
    formData.append('include_cure', 'true');
    formData.append('growth_stage', 'Growing');
    formData.append('language', 'en');

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
