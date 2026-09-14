// ==========================================================================
// AgriSmart AI - Precision Spray Tank & Dilution Calculator
// ==========================================================================

function getDosageSpecs(conditionName) {
    const name = (conditionName || '').toLowerCase();

    // 1. Healthy condition bypass — Do not prescribe synthetic chemicals to healthy crops
    if (name.includes('healthy')) {
        return {
            is_healthy: true,
            chemical_name: 'None required (Plant is healthy)',
            chemical_rate_per_litre: 0,
            chemical_unit: 'g',
            organic_name: 'Optional Organic Bio-Stimulant / Jeevamrit',
            organic_rate_per_litre: 2.0,
            organic_unit: 'ml',
            litres_per_acre: 100
        };
    }

    if (name.includes('blight') || name.includes('black rot') || name.includes('scab')) {
        return {
            is_healthy: false,
            chemical_name: 'Mancozeb 75% WP or Copper Oxychloride',
            chemical_rate_per_litre: 2.5, // grams/litre
            chemical_unit: 'g',
            organic_name: 'Neem Oil (10,000 ppm) + Trichoderma',
            organic_rate_per_litre: 5.0, // ml/litre
            organic_unit: 'ml',
            litres_per_acre: 150
        };
    } else if (name.includes('bacterial') || name.includes('spot')) {
        return {
            is_healthy: false,
            chemical_name: 'Copper Oxychloride 50% WP + Streptocycline',
            chemical_rate_per_litre: 2.5,
            chemical_unit: 'g',
            organic_name: 'Pseudomonas fluorescens Bio-bactericide',
            organic_rate_per_litre: 4.0,
            organic_unit: 'ml',
            litres_per_acre: 140
        };
    } else if (name.includes('rust') || name.includes('mildew') || name.includes('mould')) {
        return {
            is_healthy: false,
            chemical_name: 'Hexaconazole 5% EC or Wettable Sulphur',
            chemical_rate_per_litre: 2.0,
            chemical_unit: 'ml',
            organic_name: 'Baking Soda spray (0.5%) + Neem Extract',
            organic_rate_per_litre: 5.0,
            organic_unit: 'g',
            litres_per_acre: 160
        };
    } else {
        return {
            is_healthy: false,
            chemical_name: 'Broad-Spectrum Protective Fungicide',
            chemical_rate_per_litre: 2.0,
            chemical_unit: 'g',
            organic_name: 'Neem Seed Kernel Extract (NSKE 5%)',
            organic_rate_per_litre: 5.0,
            organic_unit: 'ml',
            litres_per_acre: 150
        };
    }
}

function updateDosageCalculations() {
    const areaInput = document.getElementById('dosagePlotArea');
    const unitSelect = document.getElementById('dosageAreaUnit');
    const tankSelect = document.getElementById('dosageTankSize');

    if (!areaInput || !unitSelect || !tankSelect) return;

    // Guard against negative or zero area
    let rawArea = parseFloat(areaInput.value);
    let area = (!isNaN(rawArea) && rawArea > 0) ? rawArea : 1.0;
    const unit = unitSelect.value;
    
    // Guard against zero or negative tank capacity (prevents division by zero / NaN)
    let rawTank = parseFloat(tankSelect.value);
    const tankLiters = (!isNaN(rawTank) && rawTank > 0) ? rawTank : 15;

    // Convert Bigha to Acres if selected (1 Acre approx 2.5 Bigha)
    let areaInAcres = unit === 'bigha' ? (area / 2.5) : area;

    const conditionName = document.getElementById('resultDisease') ? document.getElementById('resultDisease').textContent : '';
    const specs = getDosageSpecs(conditionName);

    const totalSolutionLiters = Math.round(areaInAcres * specs.litres_per_acre);
    const refills = Math.ceil(totalSolutionLiters / tankLiters);

    // Chemical measure per tank
    const chemPerTank = (specs.chemical_rate_per_litre * tankLiters).toFixed(1);
    const totalChem = (chemPerTank * refills).toFixed(0);

    // Organic measure per tank
    const orgPerTank = (specs.organic_rate_per_litre * tankLiters).toFixed(1);
    const totalOrg = (orgPerTank * refills).toFixed(0);

    // Update UI elements
    const chemPerTankEl = document.getElementById('dosageChemPerTank');
    if (chemPerTankEl) {
        chemPerTankEl.textContent = specs.is_healthy 
            ? '0 g (None needed)' 
            : `${chemPerTank} ${specs.chemical_unit}`;
    }

    const totalChemEl = document.getElementById('dosageTotalChem');
    if (totalChemEl) {
        totalChemEl.textContent = specs.is_healthy 
            ? '0 g (Plant is healthy)' 
            : `${totalChem} ${specs.chemical_unit} (${refills} tank refills)`;
    }

    const orgPerTankEl = document.getElementById('dosageOrgPerTank');
    if (orgPerTankEl) orgPerTankEl.textContent = `${orgPerTank} ${specs.organic_unit}`;

    const totalVolumeEl = document.getElementById('dosageTotalVolume');
    if (totalVolumeEl) totalVolumeEl.textContent = `${totalSolutionLiters} Litres total water`;
}

function setupDosageCalculator() {
    const areaInput = document.getElementById('dosagePlotArea');
    const unitSelect = document.getElementById('dosageAreaUnit');
    const tankSelect = document.getElementById('dosageTankSize');

    if (areaInput) areaInput.addEventListener('input', updateDosageCalculations);
    if (unitSelect) unitSelect.addEventListener('change', updateDosageCalculations);
    if (tankSelect) tankSelect.addEventListener('change', updateDosageCalculations);

    updateDosageCalculations();
}

window.setupDosageCalculator = setupDosageCalculator;
window.updateDosageCalculations = updateDosageCalculations;
