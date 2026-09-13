// ==========================================================================
// AgriSmart AI - AgriBot Chat Logic (Multi-turn AI Conversation)
// ==========================================================================

let chatHistory = [];
let chatOpen = false;

function setChatContext(diseaseName, crop) {
    const label = document.getElementById('chatContextLabel');
    if (label) {
        label.textContent = `${diseaseName} · ${crop}`;
    }
}

function openChat() {
    chatPanel.classList.add('open');
    chatBubble.classList.add('hidden');
    chatOpen = true;
    chatInput.focus();
    renderQuickReplies();
}

function renderQuickReplies() {
    const qrContainer = document.getElementById('quickReplies');
    if (!qrContainer) return;
    
    // Only show if we have a context and history is empty (or just start of conversation)
    if (!currentDiagnosisContext || chatHistory.length > 0) {
        qrContainer.style.display = 'none';
        return;
    }

    const lang = document.getElementById('languageSelect') ? document.getElementById('languageSelect').value : 'en';
    const chips = {
        'en': ['What is the exact dosage?', 'Can this spread?', 'Is the fruit safe to eat?'],
        'hi': ['सटीक खुराक क्या है?', 'क्या यह फैल सकता है?', 'क्या फल खाने के लिए सुरक्षित है?']
    };
    
    const options = chips[lang] || chips['en'];
    qrContainer.innerHTML = '';
    options.forEach(text => {
        const btn = document.createElement('button');
        btn.className = 'quick-reply-btn';
        btn.textContent = text;
        btn.onclick = () => {
            chatInput.value = text;
            handleSendMessage();
            qrContainer.style.display = 'none';
        };
        qrContainer.appendChild(btn);
    });
    qrContainer.style.display = 'flex';
}

function closeChat() {
    chatPanel.classList.remove('open');
    chatBubble.classList.remove('hidden');
    chatOpen = false;
}

/**
 * Lightweight HTML sanitizer — strips script/iframe/event-handler attributes.
 * Avoids adding a DOMPurify CDN dependency.
 */
function sanitizeHtml(html) {
    return html
        .replace(/<script[\s\S]*?<\/script>/gi, '')
        .replace(/<iframe[\s\S]*?>/gi, '')
        .replace(/\s+on\w+\s*=\s*(["'])[^"']*\1/gi, '')
        .replace(/javascript:/gi, '');
}

function appendMessage(role, text, isTyping = false) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble-msg';

    if (isTyping) {
        bubble.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        div.id = 'typingIndicator';
    } else if (role === 'user') {
        // User content is plain text — no HTML parsing risk
        bubble.textContent = text;
    } else {
        // Bot content may include markdown; sanitize before injecting
        const rendered = (typeof marked !== 'undefined') ? marked.parse(text) : text.replace(/\n/g, '<br>');
        bubble.innerHTML = sanitizeHtml(rendered);

        // Add Text-to-Speech audio read aloud button (Bonus E)
        const voiceBtn = document.createElement('button');
        voiceBtn.className = 'btn-read-aloud';
        voiceBtn.title = "Read aloud in your language";
        voiceBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>`;
        voiceBtn.onclick = (e) => {
            e.stopPropagation();
            if (window.voiceAssistant) {
                window.voiceAssistant.speak(text);
            }
        };
        bubble.appendChild(voiceBtn);
    }

    div.appendChild(bubble);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

function removeTypingIndicator() {
    const typing = document.getElementById('typingIndicator');
    if (typing) typing.remove();
}

async function handleSendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    chatInput.value = '';
    chatSendBtn.disabled = true;
    const qrContainer = document.getElementById('quickReplies');
    if (qrContainer) qrContainer.style.display = 'none';
    
    appendMessage('user', message);

    const typingEl = appendMessage('bot', '', true);

    const cropContext = currentDiagnosisContext ? currentDiagnosisContext.crop : "Field Crops";
    const diseaseContext = currentDiagnosisContext ? currentDiagnosisContext.disease_name : "General Farm Health";

    try {
        const result = await sendChatMessage(
            message,
            diseaseContext,
            cropContext,
            chatHistory
        );
        removeTypingIndicator();
        appendMessage('bot', result.reply);
        chatHistory = result.conversation_history;
    } catch (err) {
        removeTypingIndicator();
        appendMessage('bot', `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:4px; vertical-align:-2px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg> Sorry, I couldn't connect right now. Please try again in a moment.`);
    } finally {
        chatSendBtn.disabled = false;
        chatInput.focus();
    }
}

// Event Listeners
chatBubble.addEventListener('click', openChat);
chatCloseBtn.addEventListener('click', () => {
    closeChat();
    if (window.voiceAssistant) window.voiceAssistant.stopSpeaking();
});

const openFromResult = document.getElementById('openChatFromResult');
if (openFromResult) {
    openFromResult.addEventListener('click', () => {
        openChat();
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}

chatSendBtn.addEventListener('click', handleSendMessage);

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
});

// Voice Microphone Button Listener (Bonus E)
const micBtn = document.getElementById('chatMicBtn');
if (micBtn) {
    micBtn.addEventListener('click', () => {
        if (window.voiceAssistant) {
            window.voiceAssistant.toggleListen();
        }
    });
}
