// ==========================================================================
// AgriSmart AI v3.0 - Main App Controller
// ==========================================================================

let currentThumbnail = null;

function setFile(file) {
    if (!file || !file.type.startsWith('image/')) {
        alert('Please select a valid image file.');
        return;
    }
    selectedFile = file;
    const url = URL.createObjectURL(file);
    previewImg.src = url;
    
    // Generate low-res thumbnail for history
    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const MAX_SIZE = 250;
            let width = img.width, height = img.height;
            if (width > height) { if (width > MAX_SIZE) { height *= MAX_SIZE / width; width = MAX_SIZE; } }
            else { if (height > MAX_SIZE) { width *= MAX_SIZE / height; height = MAX_SIZE; } }
            canvas.width = width; canvas.height = height;
            canvas.getContext('2d').drawImage(img, 0, 0, width, height);
            currentThumbnail = canvas.toDataURL('image/jpeg', 0.7);
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);

    document.getElementById('diagnoseLayout').style.display = 'grid';
    dropZone.style.display = 'block';
    document.getElementById('analyzeLoader').style.display = 'flex';
    resultsSection.style.display = 'none';
    
    // Scroll down to the layout
    setTimeout(() => {
        document.getElementById('diagnoseLayout').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);

    // Auto-analyze!
    analyzeBtn.disabled = false;
    setTimeout(() => analyzeBtn.click(), 400);
}

function clearFile() {
    selectedFile = null;
    previewImg.src = '';
    document.getElementById('diagnoseLayout').style.display = 'none';
    dropZone.style.display = 'none';
    analyzeBtn.disabled = true;
    analyzeBtnText.textContent = '🔍 Select an image to analyze';
    fileInput.value = '';
    resultsSection.style.display = 'none';
    document.getElementById('analyzeLoader').style.display = 'none';
    // Restore educational sections
    ['howItWorks', 'diseasesSection', 'tipsSection'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = '';
    });
}


// File Input
fileInput.addEventListener('change', (e) => { if (e.target.files[0]) setFile(e.target.files[0]); });
clearBtn.addEventListener('click', (e) => { e.stopPropagation(); clearFile(); });

// Camera
if (cameraBtn) cameraBtn.addEventListener('click', startCamera);
if (closeCamera) closeCamera.addEventListener('click', stopCamera);
if (closeCameraBtn) closeCameraBtn.addEventListener('click', stopCamera);
if (captureBtn) captureBtn.addEventListener('click', () => captureCameraPhoto(setFile));


// Analyze
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    analyzeBtn.disabled = true;
    const lang = document.getElementById('languageSelect') ? document.getElementById('languageSelect').value : 'en';
    const dict = window.AGRI_I18N ? window.AGRI_I18N[lang] : window.AGRI_I18N['en'];
    const analyzingText = dict ? dict['btn_analyzing'] : 'Running diagnosis...';
    analyzeBtnText.innerHTML = `<div class="spinner"></div> ${analyzingText}`;
    resultsSection.style.display = 'none';
    document.getElementById('analyzeLoader').style.display = 'flex';

    try {
        const data = await fetchPrediction(selectedFile);
        document.getElementById('analyzeLoader').style.display = 'none';
        
        // Hide educational sections once results are ready
        ['howItWorks', 'diseasesSection', 'tipsSection'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });

        renderResults(data);
        addToHistory(currentThumbnail || previewImg.src, data.predictions[0]);
    } catch (err) {
        // Show user-friendly error with a retry button capability
        analyzeBtnText.innerHTML = `⚠️ Error: ${err.message}. Click to retry.`;
    } finally {
        analyzeBtn.disabled = false;
        if (!analyzeBtnText.innerHTML.includes('Error')) {
            analyzeBtnText.textContent = '🔍 Re-analyze';
        }
    }
});

// Auto-translate on language change
if (typeof languageSelect !== 'undefined' && languageSelect) {
    languageSelect.addEventListener('change', () => {
        if (selectedFile && resultsSection.style.display !== 'none') {
            analyzeBtn.click();
        }
    });
}
