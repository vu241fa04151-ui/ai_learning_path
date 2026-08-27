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
    const statusSelects = document.querySelectorAll('.module-status-select');
    if (statusSelects.length > 0) {
        statusSelects.forEach(select => {
            select.addEventListener('change', async (e) => {
                const selectEl = e.target;
                const moduleId = selectEl.dataset.moduleId;
                const status = selectEl.value;
                const moduleCard = document.getElementById(`module-card-${moduleId}`);
                const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
                
                try {
                    const response = await fetch('/api/toggle-module-progress/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken,
                        },
                        body: JSON.stringify({
                            module_id: moduleId,
                            status: status
                        })
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        // Update UI Card Class
                        moduleCard.classList.remove('completed', 'in-progress');
                        if (status === 'Completed') {
                            moduleCard.classList.add('completed');
                        } else if (status === 'In Progress') {
                            moduleCard.classList.add('in-progress');
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
                            showPointsFlash(selectEl, data.points_message);
                        }
                        
                        // Alert Badge Earned
                        if (data.badge_earned) {
                            showBadgeNotification(data.badge_earned);
                        }
                        
                    } else {
                        console.error("Failed to update status:", data.error);
                    }
                } catch (err) {
                    console.error("AJAX Error:", err);
                }
            });
        });
    }

    // --- 1B. EDUAGENT REVIEW AJAX TRIGGER ---
    const askEduAgentBtn = document.getElementById('ask-eduagent-btn');
    const eduAgentLoading = document.getElementById('eduagent-loading');
    const eduAgentEmptyState = document.getElementById('eduagent-empty-state');
    const eduAgentEmptyText = document.getElementById('eduagent-empty-text');
    const eduAgentReviewResult = document.getElementById('eduagent-review-result');
    
    const logsList = document.getElementById('eduagent-logs-list');
    const reviewProgressRatio = document.getElementById('review-progress-ratio');
    const reviewPerformance = document.getElementById('review-performance');
    const reviewDecision = document.getElementById('review-decision');
    const reviewRecommendation = document.getElementById('review-recommendation');
    
    if (askEduAgentBtn) {
        askEduAgentBtn.addEventListener('click', async () => {
            // UI state: loading
            askEduAgentBtn.disabled = true;
            eduAgentLoading.style.display = 'block';
            if (eduAgentEmptyState) eduAgentEmptyState.style.display = 'none';
            eduAgentReviewResult.style.display = 'none';
            
            const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            
            try {
                const response = await fetch('/api/eduagent-review/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    }
                });
                
                const data = await response.json();
                
                // Add a small delay for a realistic thinking/observation effect
                await new Promise(resolve => setTimeout(resolve, 800));
                
                if (data.success) {
                    // Populate workflow logs sequentially
                    logsList.innerHTML = '';
                    for (let i = 0; i < data.logs.length; i++) {
                        const li = document.createElement('li');
                        li.style.opacity = '0';
                        li.style.transition = 'opacity 0.4s ease';
                        li.innerHTML = `<i class="fa-solid fa-circle-check" style="color: var(--success); margin-right: 0.5rem;"></i> ${data.logs[i]}`;
                        logsList.appendChild(li);
                        
                        // Stagger the logs visualization
                        await new Promise(r => setTimeout(r, 200));
                        li.style.opacity = '1';
                    }
                    
                    // Update advice sections
                    if (reviewProgressRatio) {
                        reviewProgressRatio.textContent = `${data.completed_tasks} / ${data.total_tasks} Completed Tasks`;
                    }
                    if (reviewPerformance) reviewPerformance.textContent = data.performance_analysis;
                    if (reviewDecision) reviewDecision.textContent = data.decision;
                    if (reviewRecommendation) reviewRecommendation.textContent = data.recommendation;
                    
                    // Render Learning Insights
                    const insightsContainer = document.getElementById('eduagent-insights-container');
                    if (insightsContainer) {
                        insightsContainer.innerHTML = '';
                        if (data.insights && data.insights.length > 0) {
                            data.insights.forEach(insight => {
                                let icon = 'fa-hourglass-half';
                                let iconColor = 'var(--accent-purple)';
                                if (insight.type === 'trend') {
                                    icon = 'fa-chart-line';
                                    iconColor = 'var(--accent-pink)';
                                } else if (insight.type === 'consistency') {
                                    icon = 'fa-fire';
                                    iconColor = 'var(--warning)';
                                } else if (insight.type === 'focus') {
                                    icon = 'fa-bullseye';
                                    iconColor = 'var(--accent-cyan)';
                                }
                                
                                const insightDiv = document.createElement('div');
                                insightDiv.className = 'glass-panel';
                                insightDiv.style.padding = '1rem 1.25rem';
                                insightDiv.style.background = 'rgba(17, 24, 39, 0.2)';
                                insightDiv.style.borderColor = 'rgba(99, 102, 241, 0.1)';
                                insightDiv.style.borderRadius = '10px';
                                insightDiv.innerHTML = `
                                    <div style="font-size: 0.85rem; font-weight: 700; color: white; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem; display: flex; align-items: center; gap: 0.35rem;">
                                        <i class="fa-solid ${icon}" style="color: ${iconColor};"></i>
                                        ${insight.title}
                                    </div>
                                    <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.5; margin: 0;">${insight.text}</p>
                                `;
                                insightsContainer.appendChild(insightDiv);
                            });
                        } else {
                            insightsContainer.innerHTML = `
                                <div style="padding: 1.5rem; text-align: center; color: var(--text-secondary); background: rgba(0, 0, 0, 0.15); border: 1px dashed var(--border-color); border-radius: 10px; font-size: 0.9rem;">
                                    <i class="fa-solid fa-circle-info" style="margin-right: 0.35rem; color: var(--accent-purple);"></i> Complete more roadmap tasks so EduAgent can identify your learning patterns.
                                </div>
                            `;
                        }
                    }
                    
                    // Render Previous Reviews Timeline
                    const historyContainer = document.getElementById('eduagent-history-container');
                    if (historyContainer) {
                        historyContainer.innerHTML = '';
                        if (data.past_reviews && data.past_reviews.length > 0) {
                            data.past_reviews.forEach(r => {
                                const revDiv = document.createElement('div');
                                revDiv.className = 'glass-panel';
                                revDiv.style.padding = '1.25rem';
                                revDiv.style.background = 'rgba(17, 24, 39, 0.2)';
                                revDiv.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                                revDiv.style.borderRadius = '10px';
                                revDiv.style.display = 'flex';
                                revDiv.style.justifyContent = 'space-between';
                                revDiv.style.alignItems = 'flex-start';
                                revDiv.style.gap = '1.5rem';
                                revDiv.style.flexWrap = 'wrap';
                                revDiv.innerHTML = `
                                    <div style="flex: 1;">
                                        <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.5rem;">
                                            <i class="fa-regular fa-calendar-check" style="margin-right: 0.35rem;"></i> ${r.created_at}
                                        </div>
                                        <div style="margin-bottom: 0.5rem;">
                                            <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--warning); display: block; margin-bottom: 0.15rem;">Decision</span>
                                            <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0; line-height: 1.4;">${r.decision}</p>
                                        </div>
                                        <div>
                                            <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--success); display: block; margin-bottom: 0.15rem;">Next Action</span>
                                            <p style="font-size: 0.9rem; color: var(--text-primary); margin: 0; line-height: 1.4; font-weight: 500;">${r.recommendation}</p>
                                        </div>
                                    </div>
                                    <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); padding: 0.5rem 0.85rem; border-radius: 8px; font-weight: 700; font-size: 0.9rem; color: var(--accent-cyan); white-space: nowrap; height: fit-content; text-align: center;">
                                        ${r.completed_tasks} / ${r.total_tasks} Tasks
                                    </div>
                                `;
                                historyContainer.appendChild(revDiv);
                            });
                        } else {
                            historyContainer.innerHTML = `
                                <div style="padding: 1.5rem; text-align: center; color: var(--text-secondary); background: rgba(0, 0, 0, 0.15); border: 1px dashed var(--border-color); border-radius: 10px; font-size: 0.9rem;">
                                    <i class="fa-solid fa-history" style="margin-right: 0.35rem; color: var(--accent-purple);"></i> No previous review history found.
                                </div>
                            `;
                        }
                    }
                    
                    // Show result state
                    eduAgentReviewResult.style.display = 'block';
                } else {
                    if (eduAgentEmptyText) {
                        eduAgentEmptyText.textContent = data.error || 'Unknown error occurred.';
                    }
                    if (eduAgentEmptyState) eduAgentEmptyState.style.display = 'block';
                }
            } catch (err) {
                console.error('EduAgent error:', err);
                if (eduAgentEmptyText) {
                    eduAgentEmptyText.textContent = 'Network error analyzing progress.';
                }
                if (eduAgentEmptyState) eduAgentEmptyState.style.display = 'block';
            } finally {
                eduAgentLoading.style.display = 'none';
                askEduAgentBtn.disabled = false;
            }
        });
    }

    // --- 1C. EDUAGENT ADAPTATION AJAX TRIGGER ---
    const adaptPathBtn = document.getElementById('adapt-learning-path-btn');
    const adaptLoading = document.getElementById('eduagent-adapting-loading');
    const adaptResult = document.getElementById('eduagent-adapt-result');
    const adaptActionContainer = document.getElementById('adapt-action-container');
    
    const adaptWhatChanged = document.getElementById('adapt-what-changed');
    const adaptWhy = document.getElementById('adapt-why');
    const adaptNextStep = document.getElementById('adapt-next-step');
    const reloadRoadmapBtn = document.getElementById('reload-roadmap-btn');
    
    if (adaptPathBtn) {
        adaptPathBtn.addEventListener('click', async () => {
            // UI state: loading
            adaptPathBtn.disabled = true;
            if (adaptActionContainer) adaptActionContainer.style.display = 'none';
            if (adaptLoading) adaptLoading.style.display = 'block';
            if (adaptResult) adaptResult.style.display = 'none';
            
            const csrfToken = getCookie('csrftoken') || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            
            try {
                const response = await fetch('/api/eduagent-adapt/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    }
                });
                
                const data = await response.json();
                
                // Add a small delay for a realistic adaptation/write effect
                await new Promise(resolve => setTimeout(resolve, 1200));
                
                if (data.success) {
                    // Update adaptation details
                    if (adaptWhatChanged) adaptWhatChanged.textContent = data.what_changed;
                    if (adaptWhy) adaptWhy.textContent = data.why;
                    if (adaptNextStep) adaptNextStep.textContent = data.next_step;
                    
                    // Show success result state
                    if (adaptResult) adaptResult.style.display = 'block';
                    const adaptError = document.getElementById('eduagent-adapt-error');
                    if (adaptError) adaptError.style.display = 'none';
                } else {
                    const adaptError = document.getElementById('eduagent-adapt-error');
                    const adaptErrorText = document.getElementById('eduagent-adapt-error-text');
                    if (adaptError && adaptErrorText) {
                        adaptErrorText.textContent = 'Adaptation Error: ' + (data.error || 'Unknown error.');
                        adaptError.style.display = 'block';
                    }
                    if (adaptActionContainer) adaptActionContainer.style.display = 'flex';
                }
            } catch (err) {
                console.error('Adaptation error:', err);
                const adaptError = document.getElementById('eduagent-adapt-error');
                const adaptErrorText = document.getElementById('eduagent-adapt-error-text');
                if (adaptError && adaptErrorText) {
                    adaptErrorText.textContent = 'Network error adapting pathway.';
                    adaptError.style.display = 'block';
                }
                if (adaptActionContainer) adaptActionContainer.style.display = 'flex';
            } finally {
                if (adaptLoading) adaptLoading.style.display = 'none';
                adaptPathBtn.disabled = false;
            }
        });
    }
    
    if (reloadRoadmapBtn) {
        reloadRoadmapBtn.addEventListener('click', () => {
            window.location.reload();
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
