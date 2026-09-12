// ==========================================================================
// AgriSmart AI v3.0 - Main App Controller
// ==========================================================================

function setFile(file) {
    if (!file || !file.type.startsWith('image/')) {
        alert('Please select a valid image file.');
        return;
    }
    selectedFile = file;
    const url = URL.createObjectURL(file);
    previewImg.src = url;
    document.getElementById('uploadZoneInner').style.display = 'none';
    previewContainer.style.display = 'block';
    analyzeBtn.disabled = false;
    analyzeBtnText.textContent = `🔍 Analyze "${file.name}"`;
}

function clearFile() {
    selectedFile = null;
    previewImg.src = '';
    previewContainer.style.display = 'none';
    document.getElementById('uploadZoneInner').style.display = 'block';
    analyzeBtn.disabled = true;
    analyzeBtnText.textContent = '🔍 Select an image to analyze';
    fileInput.value = '';
    resultsSection.style.display = 'none';
    // Restore educational sections
    ['howItWorks', 'diseasesSection', 'tipsSection'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = '';
    });
}


// File Input
fileInput.addEventListener('change', (e) => { if (e.target.files[0]) setFile(e.target.files[0]); });
clearBtn.addEventListener('click', (e) => { e.stopPropagation(); clearFile(); });

// Drag & Drop
dropZone.addEventListener('click', (e) => {
    if (!e.target.closest('#previewContainer') && !e.target.closest('.upload-btn-row')) {
        fileInput.click();
    }
});
dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragging'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragging'));
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragging');
    if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
});

// Camera
if (cameraBtn) cameraBtn.addEventListener('click', startCamera);
if (closeCamera) closeCamera.addEventListener('click', stopCamera);
if (closeCameraBtn) closeCameraBtn.addEventListener('click', stopCamera);
if (captureBtn) captureBtn.addEventListener('click', () => captureCameraPhoto(setFile));

// Analyze
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    analyzeBtn.disabled = true;
    analyzeBtnText.innerHTML = '<div class="spinner"></div> Analyzing...';
    resultsSection.style.display = 'none';

    try {
        const data = await fetchPrediction(selectedFile);
        renderResults(data);
        addToHistory(previewImg.src, data.predictions[0]);
    } catch (err) {
        alert('Analysis error: ' + err.message);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtnText.textContent = '🔍 Re-analyze';
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
