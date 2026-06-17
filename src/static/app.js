document.addEventListener('DOMContentLoaded', () => {
    // Selectors
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');
    const sessionIdInput = document.getElementById('session-id');
    const clearMemoryBtn = document.getElementById('clear-memory-btn');
    const thoughtLogs = document.getElementById('thought-logs');
    const dbVariables = document.getElementById('db-variables');
    const sampleBtns = document.querySelectorAll('.sample-btn');

    // State
    let isGenerating = false;

    // Helper: Scroll chat to bottom
    const scrollToBottom = () => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Helper: Formats basic markdown elements (bold, bullet lists, sections) into HTML
    const formatResponseText = (text) => {
        if (!text) return '';
        let html = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
        
        // Headers
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');
        
        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Lists
        html = html.replace(/^\s*[\-\*]\s+(.*$)/gim, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
        html = html.replace(/<\/ul>\s*<ul>/g, ''); // Join adjacent lists
        
        // Linebreaks (preserve double breaks, convert single breaks)
        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/\n/g, '<br>');
        
        return `<p>${html}</p>`;
    };

    // Load active session memory
    const loadSessionMemory = async () => {
        const sessionId = sessionIdInput.value.trim() || 'default';
        try {
            const response = await fetch(`/memory?session_id=${encodeURIComponent(sessionId)}`);
            const data = await response.json();
            if (response.ok) {
                renderMemory(data.memory);
            }
        } catch (error) {
            console.error('Failed to load session memory:', error);
        }
    };

    // Render SQLite Memory items
    const renderMemory = (memory) => {
        if (!memory || Object.keys(memory).length === 0) {
            dbVariables.innerHTML = `
                <div class="empty-state-db">
                    <p>No variables saved in SQLite yet. As you audit, the auditor agent will call <code>store_fact()</code> to remember things.</p>
                </div>
            `;
            return;
        }

        let html = '<div class="db-grid">';
        for (const [key, val] of Object.entries(memory)) {
            html += `
                <div class="db-row">
                    <span class="db-key"><i class="fa-solid fa-tag"></i> ${key}</span>
                    <span class="db-val" title="${val}">${val}</span>
                </div>
            `;
        }
        html += '</div>';
        dbVariables.innerHTML = html;
    };

    // Render step-by-step trace logs
    const renderTraceLogs = (trace) => {
        if (!trace || trace.length === 0) {
            thoughtLogs.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-spinner"></i>
                    <p>Send a message to see agent routing, collaborative thought logs, and local tool executions in real-time.</p>
                </div>
            `;
            return;
        }

        thoughtLogs.innerHTML = '';
        trace.forEach(entry => {
            const entryDiv = document.createElement('div');
            
            // Assign class based on the executing agent
            const agentClass = entry.agent === 'LegalAnalystAgent' ? 'analyst' : 'auditor';
            entryDiv.className = `trace-entry ${agentClass}`;
            
            let contentHtml = '';
            
            // Parse different action types
            if (entry.action === 'received_query') {
                contentHtml = `
                    <div class="trace-header">
                        <span class="agent-tag"><i class="fa-solid fa-user-gear"></i> ${entry.agent}</span>
                        <span class="action-tag">Receive</span>
                    </div>
                    <div class="trace-desc">${entry.message}</div>
                `;
            } else if (entry.action === 'call_tool') {
                contentHtml = `
                    <div class="trace-header">
                        <span class="agent-tag"><i class="fa-solid fa-gears"></i> ${entry.agent}</span>
                        <span class="action-tag">Call Tool</span>
                    </div>
                    <div class="trace-desc">Invoked <strong>${entry.tool}</strong>:</div>
                    <div class="trace-code">${JSON.stringify(entry.args, null, 2)}</div>
                `;
            } else if (entry.action === 'tool_output') {
                contentHtml = `
                    <div class="trace-header">
                        <span class="agent-tag"><i class="fa-solid fa-database"></i> ${entry.agent}</span>
                        <span class="action-tag">Tool Result</span>
                    </div>
                    <div class="trace-desc">Returned data from local system:</div>
                    <div class="trace-code">${entry.output}</div>
                `;
            } else if (entry.action === 'final_response') {
                contentHtml = `
                    <div class="trace-header">
                        <span class="agent-tag"><i class="fa-solid fa-circle-check"></i> ${entry.agent}</span>
                        <span class="action-tag">Output</span>
                    </div>
                    <div class="trace-desc">${entry.message.substring(0, 150)}${entry.message.length > 150 ? '...' : ''}</div>
                `;
            }
            
            entryDiv.innerHTML = contentHtml;
            thoughtLogs.appendChild(entryDiv);
        });
        
        // Scroll trace to bottom
        thoughtLogs.scrollTop = thoughtLogs.scrollHeight;
    };

    // Send chat query to server
    const sendQuery = async (queryText) => {
        if (!queryText.trim() || isGenerating) return;
        
        isGenerating = true;
        chatInput.value = '';
        chatInput.style.height = 'auto'; // Reset size
        sendBtn.disabled = true;

        // 1. Add User Message
        const userDiv = document.createElement('div');
        userDiv.className = 'message user-message';
        userDiv.textContent = queryText;
        chatMessages.appendChild(userDiv);
        scrollToBottom();

        // 2. Add Typing Indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message agent-message typing-indicator-container';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        scrollToBottom();

        // Reset thought stream for current run
        thoughtLogs.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner" style="animation: rotate 1s linear infinite;"></i>
                <p>Executing agents in Vertex AI and scanning SQLite schema...</p>
            </div>
        `;

        const sessionId = sessionIdInput.value.trim() || 'default';

        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: queryText, session_id: sessionId })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            typingDiv.remove();
            
            if (response.ok) {
                // 3. Render Agent Reply
                const agentDiv = document.createElement('div');
                agentDiv.className = 'message agent-message';
                agentDiv.innerHTML = formatResponseText(data.response);
                chatMessages.appendChild(agentDiv);
                
                // 4. Update Trace Logs and Database Variables
                renderTraceLogs(data.trace);
                renderMemory(data.memory);
            } else {
                // Render Error
                const errorDiv = document.createElement('div');
                errorDiv.className = 'message agent-message system-message';
                errorDiv.style.borderLeft = '3px solid var(--danger-color)';
                errorDiv.innerHTML = `<p><strong>Error:</strong> ${data.error || 'Server error occurred.'}</p>`;
                chatMessages.appendChild(errorDiv);
                
                thoughtLogs.innerHTML = `
                    <div class="empty-state" style="color: var(--danger-color);">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <p>Execution failed. Please make sure you authenticated using GCP application-default login.</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('API Error:', error);
            typingDiv.remove();
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message agent-message system-message';
            errorDiv.style.borderLeft = '3px solid var(--danger-color)';
            errorDiv.innerHTML = `<p><strong>Network Error:</strong> Failed to communicate with the Flask API server.</p>`;
            chatMessages.appendChild(errorDiv);
        } finally {
            isGenerating = false;
            sendBtn.disabled = false;
            scrollToBottom();
        }
    };

    // Event Listeners
    sendBtn.addEventListener('click', () => {
        sendQuery(chatInput.value);
    });

    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuery(chatInput.value);
        }
    });

    // Textarea Auto-grow
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = (chatInput.scrollHeight) + 'px';
    });

    // Session Change triggers memory load
    sessionIdInput.addEventListener('change', () => {
        loadSessionMemory();
        thoughtLogs.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner"></i>
                <p>Switched session. Send a message to trace agent interactions.</p>
            </div>
        `;
    });

    // Clear session memory
    clearMemoryBtn.addEventListener('click', async () => {
        const sessionId = sessionIdInput.value.trim() || 'default';
        if (confirm(`Are you sure you want to clear the SQLite session memory for: "${sessionId}"?`)) {
            try {
                const response = await fetch('/clear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId })
                });
                const data = await response.json();
                if (response.ok) {
                    alert(data.message);
                    renderMemory({});
                    
                    // Add system note to chat
                    const sysDiv = document.createElement('div');
                    sysDiv.className = 'message system-message';
                    sysDiv.innerHTML = `<p><i class="fa-solid fa-circle-info"></i> Session memory wiped in database for <strong>${sessionId}</strong>.</p>`;
                    chatMessages.appendChild(sysDiv);
                    scrollToBottom();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (err) {
                console.error(err);
                alert('Failed to clear memory');
            }
        }
    });

    // Sample prompts trigger
    sampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const qText = btn.getAttribute('data-query');
            sendQuery(qText);
        });
    });

    // Initial Load
    loadSessionMemory();
});
