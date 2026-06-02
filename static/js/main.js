// Helper to extract CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. DASHBOARD AJAX MODULE PROGRESS TOGGLING ---
    const moduleCheckboxes = document.querySelectorAll('.module-checkbox');
    if (moduleCheckboxes.length > 0) {
        moduleCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', async (e) => {
                const checkboxEl = e.target;
                const moduleId = checkboxEl.dataset.moduleId;
                const isChecked = checkboxEl.checked;
                const status = isChecked ? 'Completed' : 'Not Started';
                const moduleCard = document.getElementById(`module-card-${moduleId}`);
                
                try {
                    const response = await fetch('/api/toggle-module-progress/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: JSON.stringify({
                            module_id: moduleId,
                            status: status
                        })
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        // Update UI Card Class
                        if (status === 'Completed') {
                            moduleCard.classList.add('completed');
                            moduleCard.classList.remove('in-progress');
                        } else {
                            moduleCard.classList.remove('completed');
                        }
                        
                        // Update Progress Fill and Labels
                        const progressFills = document.querySelectorAll('.progress-bar-fill');
                        const progressPercentages = document.querySelectorAll('.progress-percent-val');
                        
                        progressFills.forEach(fill => {
                            fill.style.width = `${data.progress_percentage}%`;
                        });
                        progressPercentages.forEach(span => {
                            span.textContent = `${data.progress_percentage}%`;
                        });
                        
                        // Update Student Points
                        const pointsSpans = document.querySelectorAll('.student-points-val');
                        pointsSpans.forEach(span => {
                            span.textContent = data.points;
                        });
                        
                        // Flash points notification
                        if (data.points_message) {
                            showPointsFlash(checkboxEl, data.points_message);
                        }
                        
                        // Alert Badge Earned
                        if (data.badge_earned) {
                            showBadgeNotification(data.badge_earned);
                        }
                        
                    } else {
                        console.error("Failed to update status:", data.error);
                        checkboxEl.checked = !isChecked; // Revert checkbox
                    }
                } catch (err) {
                    console.error("AJAX Error:", err);
                    checkboxEl.checked = !isChecked; // Revert checkbox
                }
            });
        });
    }

    // Floating Points Flash Animation Helper
    function showPointsFlash(anchorElement, text) {
        const flash = document.createElement('div');
        flash.textContent = text;
        flash.style.position = 'absolute';
        flash.style.color = text.includes('+') ? '#10b981' : '#ef4444';
        flash.style.fontWeight = 'bold';
        flash.style.fontSize = '0.9rem';
        flash.style.pointerEvents = 'none';
        flash.style.zIndex = '1000';
        flash.style.transition = 'all 0.8s ease-out';
        
        const rect = anchorElement.getBoundingClientRect();
        flash.style.left = `${rect.left + window.scrollX + 25}px`;
        flash.style.top = `${rect.top + window.scrollY - 10}px`;
        
        document.body.appendChild(flash);
        
        setTimeout(() => {
            flash.style.transform = 'translateY(-25px)';
            flash.style.opacity = '0';
        }, 50);
        
        setTimeout(() => {
            flash.remove();
        }, 900);
    }
    
    // Custom Badge Earned Toast
    function showBadgeNotification(badgeName) {
        const toast = document.createElement('div');
        toast.className = 'glass-panel';
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.left = '20px';
        toast.style.padding = '1.25rem 2rem';
        toast.style.zIndex = '2000';
        toast.style.borderLeft = '4px solid #8b5cf6';
        toast.style.display = 'flex';
        toast.style.alignItems = 'center';
        toast.style.gap = '1rem';
        toast.style.animation = 'slideInUp 0.5s ease-out';
        
        toast.innerHTML = `
            <div style="font-size: 1.5rem; color: #8b5cf6;"><i class="fa-solid fa-trophy"></i></div>
            <div>
                <div style="font-weight: 700; color: white;">Badge Unlocked!</div>
                <div style="font-size: 0.85rem; color: #d1d5db;">You earned: <strong>${badgeName}</strong></div>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.5s ease-in';
            setTimeout(() => toast.remove(), 450);
        }, 4000);
    }
    
    // --- 2. MULTI-STEP PATH GENERATOR FORM ---
    const stepTabs = document.querySelectorAll('.step-tab');
    const stepNodes = document.querySelectorAll('.step-node');
    const nextBtns = document.querySelectorAll('.next-step-btn');
    const prevBtns = document.querySelectorAll('.prev-step-btn');
    
    let currentStep = 0;
    
    if (stepTabs.length > 0) {
        // Init first tab
        showStep(currentStep);
        
        nextBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                if (validateStep(currentStep)) {
                    currentStep++;
                    showStep(currentStep);
                }
            });
        });
        
        prevBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                currentStep--;
                showStep(currentStep);
            });
        });
        
        // Choice Card Clicking Handler
        // Maps click on choice card to selecting underlying radio/select inputs if present
        const choiceCards = document.querySelectorAll('.choice-card');
        choiceCards.forEach(card => {
            card.addEventListener('click', () => {
                const targetInputId = card.dataset.input;
                const groupName = card.dataset.group;
                
                // Deselect other cards in same group
                document.querySelectorAll(`.choice-card[data-group="${groupName}"]`).forEach(c => {
                    c.classList.remove('selected');
                });
                
                card.classList.add('selected');
                
                // Update actual form input
                const formInput = document.getElementById(targetInputId);
                if (formInput) {
                    if (formInput.type === 'radio' || formInput.tagName === 'SELECT' || formInput.tagName === 'INPUT') {
                        formInput.value = card.dataset.value;
                        // Fire change event
                        const event = new Event('change', { bubbles: true });
                        formInput.dispatchEvent(event);
                    }
                }
            });
        });
    }
    
    function showStep(stepIndex) {
        stepTabs.forEach((tab, index) => {
            tab.classList.toggle('active', index === stepIndex);
        });
        
        stepNodes.forEach((node, index) => {
            node.classList.toggle('active', index === stepIndex);
            node.classList.toggle('completed', index < stepIndex);
        });
    }
    
    function validateStep(stepIndex) {
        // Add simple validation (e.g. check inputs)
        const activeTab = stepTabs[stepIndex];
        const requiredInputs = activeTab.querySelectorAll('[required]');
        let isValid = true;
        
        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.style.borderColor = '#ef4444';
            } else {
                input.style.borderColor = '';
            }
        });
        
        return isValid;
    }
    
    // --- 3. COUNSELOR CHATBOT ASSISTANT ---
    const chatTrigger = document.querySelector('.chat-trigger-btn');
    const chatbotBubble = document.querySelector('.chatbot-bubble');
    const closeChat = document.querySelector('.close-chat-btn');
    const sendChat = document.querySelector('.send-chat-btn');
    const chatInput = document.querySelector('.chat-input');
    const chatMessages = document.querySelector('.chatbot-messages');
    
    if (chatTrigger && chatbotBubble) {
        chatTrigger.addEventListener('click', () => {
            chatbotBubble.classList.add('active');
            chatTrigger.classList.add('hidden');
            chatInput.focus();
            scrollToBottom();
        });
        
        closeChat.addEventListener('click', () => {
            chatbotBubble.classList.remove('active');
            chatTrigger.classList.remove('hidden');
        });
        
        sendChat.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;
        
        // Append user bubble
        appendMessage(text, 'student');
        chatInput.value = '';
        scrollToBottom();
        
        // Append typing placeholder
        const typingId = showTypingIndicator();
        scrollToBottom();
        
        try {
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ message: text })
            });
            
            const data = await response.json();
            removeTypingIndicator(typingId);
            
            if (data.success) {
                appendMessage(data.reply, 'counselor');
            } else {
                appendMessage("Sorry, I encountered an issue. Let's try again.", 'counselor');
            }
            scrollToBottom();
        } catch (err) {
            console.error("Chat error:", err);
            removeTypingIndicator(typingId);
            appendMessage("Sorry, network issues occurred. Please test again.", 'counselor');
            scrollToBottom();
        }
    }
    
    function appendMessage(text, sender) {
        const bubble = document.createElement('div');
        bubble.className = `chat-msg ${sender}`;
        bubble.innerHTML = text; // allow bold highlights
        chatMessages.appendChild(bubble);
    }
    
    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const bubble = document.createElement('div');
        bubble.id = id;
        bubble.className = 'chat-msg counselor';
        bubble.style.fontStyle = 'italic';
        bubble.style.color = '#9ca3af';
        bubble.textContent = 'Counselor is typing...';
        chatMessages.appendChild(bubble);
        return id;
    }
    
    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // --- 4. PRINT ROADMAP TRIGGER ---
    const printBtn = document.getElementById('print-roadmap-btn');
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            window.print();
        });
    }
});
