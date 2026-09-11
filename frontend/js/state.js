// ==========================================================================
// AgriSmart AI - Application State & DOM References
// ==========================================================================

let selectedFile = null;
let scanHistory = [];
let cameraStream = null;

// Core DOM Elements
const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');
const previewContainer = document.getElementById('previewContainer');
const previewImg = document.getElementById('previewImg');
const clearBtn = document.getElementById('clearPreview');
const analyzeBtn = document.getElementById('analyzeBtn');
const analyzeBtnText = document.getElementById('analyzeBtnText');
const resultsSection = document.getElementById('resultsSection');
const historySection = document.getElementById('historySection');
const historyGrid = document.getElementById('historyGrid');

// Camera Modal Elements
const cameraModal = document.getElementById('cameraModal');
const cameraVideo = document.getElementById('cameraVideo');
const cameraCanvas = document.getElementById('cameraCanvas');
const cameraBtn = document.getElementById('cameraBtn');
const closeCamera = document.getElementById('closeCamera');
const closeCameraBtn = document.getElementById('closeCameraBtn');
const captureBtn = document.getElementById('captureBtn');
