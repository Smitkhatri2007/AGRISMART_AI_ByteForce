// ==========================================================================
// AgriSmart AI - Voice Assistant Engine (Bonus Module E)
// Integrates browser Web Speech API for Speech-to-Text (STT) and Text-to-Speech (TTS)
// Supports Indian Regional Accents & Languages: EN, HI, MR, TA, TE, KN, GU
// ==========================================================================

const BROWSER_LANG_CODES = {
    'en': 'en-IN',
    'hi': 'hi-IN',
    'mr': 'mr-IN',
    'ta': 'ta-IN',
    'te': 'te-IN',
    'kn': 'kn-IN',
    'gu': 'gu-IN'
};

class VoiceAssistant {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.synth = window.speechSynthesis || null;
        this.initRecognition();
    }

    initRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn("Speech Recognition not supported in this browser. Voice input disabled.");
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateMicUI(true);
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const chatInput = document.getElementById('chatInput');
            if (chatInput) {
                chatInput.value = transcript;
                // Auto-send or focus
                const sendBtn = document.getElementById('chatSendBtn');
                if (sendBtn) sendBtn.click();
            }
        };

        this.recognition.onerror = (event) => {
            console.warn("Speech recognition error:", event.error);
            this.isListening = false;
            this.updateMicUI(false);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateMicUI(false);
        };
    }

    toggleListen() {
        if (!this.recognition) {
            alert("Speech recognition is not supported by your browser. Please use Chrome, Edge, or Safari.");
            return;
        }

        if (this.isListening) {
            this.recognition.stop();
        } else {
            const langSelect = document.getElementById('languageSelect');
            const chosen = langSelect ? langSelect.value : 'en';
            this.recognition.lang = BROWSER_LANG_CODES[chosen] || 'en-IN';
            try {
                this.recognition.start();
            } catch (e) {
                console.error("Failed to start speech recognition:", e);
            }
        }
    }

    speak(text) {
        if (!this.synth) return;

        // Cancel any ongoing speech
        this.synth.cancel();

        // Strip markdown and HTML tags for clean speech synthesis
        const cleanText = text
            .replace(/[#*_`~[\]()]/g, '')
            .replace(/<[^>]*>/g, '')
            .replace(/https?:\/\/\S+/g, '')
            .trim();

        if (!cleanText) return;

        const utterance = new SpeechSynthesisUtterance(cleanText);
        const langSelect = document.getElementById('languageSelect');
        const chosen = langSelect ? langSelect.value : 'en';
        utterance.lang = BROWSER_LANG_CODES[chosen] || 'en-IN';
        utterance.rate = 0.95; // Slightly slower, clear cadence for accessibility
        utterance.pitch = 1.0;

        this.synth.speak(utterance);
    }

    stopSpeaking() {
        if (this.synth) this.synth.cancel();
    }

    updateMicUI(listening) {
        const micBtn = document.getElementById('chatMicBtn');
        if (!micBtn) return;
        if (listening) {
            micBtn.classList.add('mic-active');
            micBtn.title = "Listening... Speak now";
        } else {
            micBtn.classList.remove('mic-active');
            micBtn.title = "Voice Input (Speak your question)";
        }
    }
}

window.voiceAssistant = new VoiceAssistant();
