// ==========================================================================
// AgriSmart AI - Camera Capture & WebRTC Stream
// ==========================================================================

async function startCamera() {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        cameraVideo.srcObject = cameraStream;
        cameraModal.classList.add('open');
    } catch (err) {
        alert('Camera not available: ' + err.message);
    }
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach((t) => t.stop());
        cameraStream = null;
    }
    cameraModal.classList.remove('open');
}

function captureCameraPhoto(onCaptureCallback) {
    cameraCanvas.width = cameraVideo.videoWidth;
    cameraCanvas.height = cameraVideo.videoHeight;
    cameraCanvas.getContext('2d').drawImage(cameraVideo, 0, 0);
    cameraCanvas.toBlob((blob) => {
        const file = new File([blob], 'camera_capture.jpg', { type: 'image/jpeg' });
        if (onCaptureCallback) {
            onCaptureCallback(file);
        }
        stopCamera();
    }, 'image/jpeg', 0.9);
}
