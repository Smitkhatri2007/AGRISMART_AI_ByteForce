// ==========================================================================
// AgriSmart AI - Main Application Controller & Event Wiring
// ==========================================================================

// File Selection & Preview Management
function setFile(file) {
    if (!file || !file.type.startsWith('image/')) {
        alert('Please select a valid image file.');
        return;
    }
    selectedFile = file;
    const url = URL.createObjectURL(file);
    previewImg.src = url;
    previewContainer.style.display = 'block';
    analyzeBtn.disabled = false;
    analyzeBtnText.textContent = `🔍 Analyze "${file.name}"`;
}

function clearFile() {
    selectedFile = null;
    previewImg.src = '';
    previewContainer.style.display = 'none';
    analyzeBtn.disabled = true;
    analyzeBtnText.textContent = '🔍 Analyze Plant — Select image first';
    fileInput.value = '';
}

// File Input Listeners
fileInput.addEventListener('change', (e) => {
    if (e.target.files[0]) {
        setFile(e.target.files[0]);
    }
});

clearBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    clearFile();
});

// Drag & Drop Listeners
dropZone.addEventListener('click', (e) => {
    if (!e.target.closest('#previewContainer') && !e.target.closest('.upload-actions')) {
        fileInput.click();
    }
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragging');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragging');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragging');
    if (e.dataTransfer.files[0]) {
        setFile(e.dataTransfer.files[0]);
    }
});

// Camera Event Listeners
if (cameraBtn) {
    cameraBtn.addEventListener('click', startCamera);
}
if (closeCamera) {
    closeCamera.addEventListener('click', stopCamera);
}
if (closeCameraBtn) {
    closeCameraBtn.addEventListener('click', stopCamera);
}
if (captureBtn) {
    captureBtn.addEventListener('click', () => {
        captureCameraPhoto(setFile);
    });
}

// Analyze Plant Event Listener
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    // Show loading spinner
    analyzeBtn.disabled = true;
    analyzeBtnText.innerHTML = '<div class="spinner"></div> Analyzing...';
    resultsSection.style.display = 'none';

    try {
        const data = await fetchPrediction(selectedFile);
        renderResults(data);
        addToHistory(previewImg.src, data.predictions[0]);
    } catch (err) {
        alert('Error: ' + err.message);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtnText.textContent = '🔍 Re-analyze';
    }
});
