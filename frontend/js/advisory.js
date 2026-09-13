// ==========================================================================
// AgriSmart AI - Smart Advisory Engine (Bonus C: Weather & Bonus B: Irrigation)
// ==========================================================================

const REGION_COORDINATES = {
    "ahmedabad": { name: "Ahmedabad / Anand, Gujarat", lat: 23.0225, lon: 72.5714 },
    "nashik": { name: "Nashik, Maharashtra (Horticulture)", lat: 19.9975, lon: 73.7898 },
    "ludhiana": { name: "Ludhiana, Punjab (Wheat/Paddy)", lat: 30.9010, lon: 75.8573 },
    "bengaluru": { name: "Bengaluru Rural, Karnataka", lat: 12.9716, lon: 77.5946 },
    "coimbatore": { name: "Coimbatore, Tamil Nadu", lat: 11.0168, lon: 76.9558 },
    "varanasi": { name: "Varanasi, Uttar Pradesh", lat: 25.3176, lon: 82.9739 }
};

let currentFarmLocation = {
    lat: 23.0225,
    lon: 72.5714,
    name: "Ahmedabad, Gujarat (Default)"
};

let latestWeatherData = null;

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    initLocationPreferences();
    initIrrigationForm();
    initCropRecommendation();
    loadWeatherAdvisory();
});

function initLocationPreferences() {
    // Check localStorage
    const saved = localStorage.getItem('agrismart_farm_location');
    if (saved) {
        try {
            currentFarmLocation = JSON.parse(saved);
        } catch (_) {}
    }

    const locText = document.getElementById('activeLocationText');
    if (locText) {
        locText.textContent = currentFarmLocation.name || `${currentFarmLocation.lat.toFixed(2)}°, ${currentFarmLocation.lon.toFixed(2)}°`;
    }

    const geoBtn = document.getElementById('btnGetLocation');
    if (geoBtn) {
        geoBtn.addEventListener('click', requestUserLocation);
    }

    const regionSelect = document.getElementById('regionFallbackSelect');
    if (regionSelect) {
        regionSelect.addEventListener('change', (e) => {
            const val = e.target.value;
            if (REGION_COORDINATES[val]) {
                const reg = REGION_COORDINATES[val];
                currentFarmLocation = { lat: reg.lat, lon: reg.lon, name: reg.name };
                localStorage.setItem('agrismart_farm_location', JSON.stringify(currentFarmLocation));
                if (locText) locText.textContent = reg.name;
                loadWeatherAdvisory();
            }
        });
    }
}

function requestUserLocation() {
    const locText = document.getElementById('activeLocationText');
    const geoBtn = document.getElementById('btnGetLocation');
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser. Please select a region from the list.");
        return;
    }

    if (geoBtn) geoBtn.disabled = true;
    if (locText) locText.textContent = "Detecting GPS location...";

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const { latitude, longitude } = pos.coords;
            currentFarmLocation = {
                lat: latitude,
                lon: longitude,
                name: `GPS: ${latitude.toFixed(2)}° N, ${longitude.toFixed(2)}° E`
            };
            localStorage.setItem('agrismart_farm_location', JSON.stringify(currentFarmLocation));
            if (locText) locText.textContent = currentFarmLocation.name;
            if (geoBtn) geoBtn.disabled = false;
            loadWeatherAdvisory();
        },
        (err) => {
            console.warn("Location permission denied or error:", err);
            if (locText) locText.textContent = currentFarmLocation.name;
            if (geoBtn) geoBtn.disabled = false;
            alert("Location access was not granted. Using selected agro-region coordinates.");
        },
        { timeout: 8000, enableHighAccuracy: true }
    );
}

async function loadWeatherAdvisory() {
    const loader = document.getElementById('weatherLoader');
    const content = document.getElementById('weatherContent');
    if (loader) loader.style.display = 'flex';
    if (content) content.style.opacity = '0.5';

    try {
        const data = await fetchWeatherIntelligence(currentFarmLocation.lat, currentFarmLocation.lon);
        latestWeatherData = data;
        renderWeatherAdvisory(data);
    } catch (e) {
        console.error("Failed to load weather advisory:", e);
    } finally {
        if (loader) loader.style.display = 'none';
        if (content) content.style.opacity = '1';
    }
}

function renderWeatherAdvisory(data) {
    if (!data || !data.current) return;

    // Current Temp & Condition
    const tempEl = document.getElementById('weatherCurrentTemp');
    const condEl = document.getElementById('weatherCurrentCond');
    const iconEl = document.getElementById('weatherCurrentIcon');
    const humEl = document.getElementById('weatherCurrentHum');
    const windEl = document.getElementById('weatherCurrentWind');

    if (tempEl) tempEl.textContent = `${Math.round(data.current.temperature)}°C`;
    if (condEl) condEl.textContent = data.current.condition;
    if (iconEl) iconEl.textContent = data.current.icon;
    if (humEl) humEl.textContent = `${data.current.humidity}%`;
    if (windEl) windEl.textContent = `${Math.round(data.current.wind_speed)} km/h`;

    // 1. Rain Delay Irrigation Card (Bonus C)
    const irrBadge = document.getElementById('advisoryRainBadge');
    const irrTitle = document.getElementById('advisoryRainTitle');
    const irrDetail = document.getElementById('advisoryRainDetail');
    if (data.irrigation_action) {
        const act = data.irrigation_action;
        if (irrBadge) {
            irrBadge.textContent = act.delay_recommended ? "DELAY RECOMMENDED" : "NORMAL SCHEDULE";
            irrBadge.className = `status-pill pill-${act.delay_recommended ? 'amber' : 'green'}`;
        }
        if (irrTitle) irrTitle.textContent = act.title;
        if (irrDetail) irrDetail.textContent = act.detail;
    }

    // 2. Spray Window Card (Bonus C)
    const sprayBadge = document.getElementById('advisorySprayBadge');
    const sprayTitle = document.getElementById('advisorySprayTitle');
    const sprayDetail = document.getElementById('advisorySprayDetail');
    if (data.spray_window) {
        const sw = data.spray_window;
        if (sprayBadge) {
            sprayBadge.textContent = sw.status;
            sprayBadge.className = `status-pill pill-${sw.badge_color || 'green'}`;
        }
        if (sprayTitle) sprayTitle.textContent = sw.title;
        if (sprayDetail) sprayDetail.textContent = sw.reason;
    }

    // 3. Fungal Blight Risk Index (Bonus C)
    const riskBadge = document.getElementById('advisoryRiskBadge');
    const riskScore = document.getElementById('advisoryRiskScore');
    const riskAdvice = document.getElementById('advisoryRiskAdvice');
    const riskBar = document.getElementById('advisoryRiskBar');
    if (data.disease_risk) {
        const dr = data.disease_risk;
        if (riskBadge) {
            riskBadge.textContent = `${dr.level} RISK`;
            riskBadge.className = `status-pill pill-${dr.badge_color || 'green'}`;
        }
        if (riskScore) riskScore.textContent = `${dr.score}/100`;
        if (riskAdvice) riskAdvice.textContent = dr.advice;
        if (riskBar) {
            riskBar.style.width = `${dr.score}%`;
            riskBar.style.backgroundColor = dr.level === 'CRITICAL' ? '#dc2626' : (dr.level === 'HIGH' ? '#ea580c' : (dr.level === 'MODERATE' ? '#f59e0b' : '#16a34a'));
        }
    }

    // 5-Day Forecast Carousel
    const forecastContainer = document.getElementById('forecastRow');
    if (forecastContainer && data.forecast_days) {
        forecastContainer.innerHTML = data.forecast_days.map(d => {
            const dateObj = new Date(d.date);
            const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
            return `
                <div class="forecast-day-chip">
                    <span class="f-day">${dayName}</span>
                    <span class="f-icon">${d.icon}</span>
                    <span class="f-temp">${Math.round(d.temp_max)}° / ${Math.round(d.temp_min)}°</span>
                    <span class="f-rain">💧 ${d.rain_prob_pct}%</span>
                </div>
            `;
        }).join('');
    }
}

function initIrrigationForm() {
    const slider = document.getElementById('moistureSlider');
    const valDisplay = document.getElementById('moistureValDisplay');
    const stateDisplay = document.getElementById('moistureStateLabel');

    if (slider && valDisplay && stateDisplay) {
        const updateSliderUI = (val) => {
            valDisplay.textContent = `${val}%`;
            let stateText = "Dry & Dusty (Soil Cracks)";
            let color = "#dc2626";
            if (val > 75) {
                stateText = "Saturated / Waterlogged";
                color = "#2563eb";
            } else if (val > 45) {
                stateText = "Optimal Moist Loam";
                color = "#16a34a";
            } else if (val > 25) {
                stateText = "Slightly Dry (Faint subsurface moisture)";
                color = "#f59e0b";
            }
            stateDisplay.textContent = stateText;
            stateDisplay.style.color = color;
        };

        slider.addEventListener('input', (e) => updateSliderUI(e.target.value));
        updateSliderUI(slider.value);
    }

    // Stage Selection Chips
    const stageChips = document.querySelectorAll('.stage-chip');
    stageChips.forEach(chip => {
        chip.addEventListener('click', () => {
            stageChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
        });
    });

    // Calculate Button
    const calcBtn = document.getElementById('btnCalculateIrrigation');
    if (calcBtn) {
        calcBtn.addEventListener('click', handleCalculateIrrigation);
    }
}

async function handleCalculateIrrigation() {
    const cropSelect = document.getElementById('irrigationCropSelect');
    const soilSelect = document.getElementById('irrigationSoilSelect');
    const slider = document.getElementById('moistureSlider');
    const activeChip = document.querySelector('.stage-chip.active');

    const crop = cropSelect ? cropSelect.value : "Tomato";
    const soil = soilSelect ? soilSelect.value : "Loamy";
    const moisture = slider ? slider.value : 30;
    const stage = activeChip ? activeChip.dataset.stage : "Flowering";

    const calcBtn = document.getElementById('btnCalculateIrrigation');
    const resultBox = document.getElementById('irrigationResultBox');

    if (calcBtn) calcBtn.disabled = true;

    try {
        const plan = await fetchIrrigationPlan(
            crop,
            stage,
            moisture,
            soil,
            currentFarmLocation.lat,
            currentFarmLocation.lon
        );

        if (resultBox) {
            resultBox.style.display = 'block';
            document.getElementById('irrResultTitle').textContent = plan.title;
            document.getElementById('irrResultBadge').textContent = plan.action.replace('_', ' ');
            document.getElementById('irrResultBadge').className = `status-pill pill-${plan.badge_color || 'green'}`;
            document.getElementById('irrResultVolume').textContent = plan.recommended_volume_liters_m2 > 0 
                ? `${plan.recommended_volume_liters_m2} L/m² (~${plan.drip_runtime_minutes} mins drip)` 
                : `0 L/m² (No watering needed)`;
            document.getElementById('irrResultDetail').textContent = plan.explanation;
            document.getElementById('irrResultFactor').textContent = `🌦️ Weather Integration: ${plan.weather_forecast_factor}`;
            
            resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    } catch (e) {
        console.error("Irrigation calculation error:", e);
        alert("Failed to calculate irrigation schedule. Please try again.");
    } finally {
        if (calcBtn) calcBtn.disabled = false;
    }
}

// ==========================================================================
// Crop Recommendation Matrix Engine (Bonus Module A)
// ==========================================================================

function initCropRecommendation() {
    const phSlider = document.getElementById('cropRecPhSlider');
    const phDisplay = document.getElementById('phValDisplay');
    if (phSlider && phDisplay) {
        phSlider.addEventListener('input', (e) => {
            phDisplay.textContent = parseFloat(e.target.value).toFixed(1);
        });
    }

    const btn = document.getElementById('btnRecommendCrops');
    if (btn) {
        btn.addEventListener('click', handleCropRecommendation);
    }
}

async function handleCropRecommendation() {
    const soilSelect = document.getElementById('cropRecSoilSelect');
    const phSlider = document.getElementById('cropRecPhSlider');
    const seasonSelect = document.getElementById('cropRecSeasonSelect');
    const prevCropSelect = document.getElementById('cropRecPrevCropSelect');
    const grid = document.getElementById('cropRecResultsGrid');
    const btn = document.getElementById('btnRecommendCrops');

    const soil = soilSelect ? soilSelect.value : 'loamy';
    const ph = phSlider ? parseFloat(phSlider.value) : 6.5;
    const season = seasonSelect ? seasonSelect.value : 'Kharif';
    const prev = prevCropSelect ? prevCropSelect.value : 'None';

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳ Evaluating ICAR Agro-Ecological Matrix...</span>';
    }

    try {
        const res = await window.fetchCropRecommendations({
            soil_type: soil,
            ph: ph,
            season: season,
            previous_crop: prev,
            latitude: currentFarmLocation.lat,
            longitude: currentFarmLocation.lon
        });

        const recList = (res && (res.recommendations || res.recommended_crops)) || [];
        if (grid && recList.length > 0) {
            grid.style.display = 'grid';
            grid.innerHTML = '';

            recList.forEach((item, idx) => {
                const card = document.createElement('div');
                card.className = 'crop-rec-card';
                const matchPct = item.suitability_pct || item.suitability_score || 85;
                const duration = item.duration || item.growing_duration_days || '90-110 days';
                const waterReq = item.water_requirement_mm ? `${item.water_requirement_mm} mm` : 'Medium (350-500mm)';

                card.innerHTML = `
                    <div class="crop-rec-header">
                        <div>
                            <span style="font-size:0.7rem; font-weight:800; color:var(--green-700); letter-spacing:0.05em; text-transform:uppercase;">Rank #${idx + 1} Recommendation</span>
                            <div class="crop-rec-title">${item.crop}</div>
                        </div>
                        <span class="crop-rec-badge">${matchPct}% Match</span>
                    </div>

                    <p style="font-size:0.8rem; color:var(--text); margin:0; line-height:1.4;">
                        ${item.primary_rationale}
                    </p>

                    <div class="crop-rec-stats">
                        <div class="crop-stat-item">
                            <span class="crop-stat-lbl">OPTIMAL pH RANGE</span>
                            <span class="crop-stat-val">${item.optimal_ph_range || '6.0 - 7.5'}</span>
                        </div>
                        <div class="crop-stat-item">
                            <span class="crop-stat-lbl">WATER DEMAND</span>
                            <span class="crop-stat-val">${waterReq}</span>
                        </div>
                        <div class="crop-stat-item">
                            <span class="crop-stat-lbl">CROP DURATION</span>
                            <span class="crop-stat-val">${duration}</span>
                        </div>
                        <div class="crop-stat-item">
                            <span class="crop-stat-lbl">SUITABLE SEASON</span>
                            <span class="crop-stat-val">${item.season || season}</span>
                        </div>
                    </div>

                    ${item.rotation_benefit ? `
                        <div class="crop-rotation-banner">
                            <strong>🔄 Crop Rotation Benefit (After ${prev}):</strong><br>
                            ${item.rotation_benefit}
                        </div>
                    ` : ''}
                `;
                grid.appendChild(card);
            });

            grid.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    } catch (err) {
        console.error("Crop recommendation failed:", err);
        alert("Failed to compute crop recommendations. Please check inputs and retry.");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<span>🌾 Recommend Best Crops (Bonus A)</span>';
        }
    }
}

