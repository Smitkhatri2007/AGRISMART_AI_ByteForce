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
}

function closeChat() {
    chatPanel.classList.remove('open');
    chatBubble.classList.remove('hidden');
    chatOpen = false;
}

function appendMessage(role, text, isTyping = false) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble-msg';

    if (isTyping) {
        bubble.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        div.id = 'typingIndicator';
    } else {
        if (typeof marked !== 'undefined') {
            bubble.innerHTML = marked.parse(text);
        } else {
            bubble.innerHTML = text.replace(/\n/g, '<br>');
        }
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

    if (!currentDiagnosisContext) {
        appendMessage('bot', '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:4px; vertical-align:-2px;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg> Please <strong>analyze a plant image first</strong>, then I can answer follow-up questions with full disease context!');
        return;
    }

    chatInput.value = '';
    chatSendBtn.disabled = true;
    appendMessage('user', message);

    const typingEl = appendMessage('bot', '', true);

    try {
        const result = await sendChatMessage(
            message,
            currentDiagnosisContext.disease_name,
            currentDiagnosisContext.crop,
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
chatCloseBtn.addEventListener('click', closeChat);

document.getElementById('openChatFromResult').addEventListener('click', () => {
    openChat();
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

chatSendBtn.addEventListener('click', handleSendMessage);

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
});
