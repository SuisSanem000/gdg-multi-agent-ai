/**
 * File Name: src/static/app.ts
 * Purpose: Interactive frontend driver for the Smart Contact Notebook.
 * Relation to Project: Acts as the client-side controller. It handles user inputs from the web UI,
 *   sends asynchronous API query requests to the Flask backend, renders the real-time agent execution 
 *   thought traces, and dynamically populates the SQLite session memory panel.
 * Responsibilities:
 *   - Captures user chat interactions and handles textarea resizing.
 *   - Dispatches AJAX POST requests to `/query` with the active session ID.
 *   - Parses and formats markdown response strings from the agent.
 *   - Dynamically updates the "Live Agent Thought Stream" log tracing routing and tool calls.
 *   - Automatically synchronizes and inspects SQLite database key-value memories.
 */

// Define structures for TypeScript types
interface TraceEntry {
    agent: string;
    action: 'received_query' | 'call_tool' | 'tool_output' | 'final_response' | string;
    message?: string;
    tool?: string;
    args?: Record<string, any>;
    output?: any;
}

interface QueryResponseData {
    query: string;
    response: string;
    trace: TraceEntry[];
    memory: Record<string, string>;
    error?: string;
}

interface MemoryData {
    session_id: string;
    memory: Record<string, string>;
    error?: string;
}

interface ClearResponseData {
    status: string;
    message: string;
    error?: string;
}

document.addEventListener('DOMContentLoaded', () => {
    // Selectors typed to standard HTML element interfaces
    const chatInput = document.getElementById('chat-input') as HTMLTextAreaElement | null;
    const sendBtn = document.getElementById('send-btn') as HTMLButtonElement | null;
    const chatMessages = document.getElementById('chat-messages') as HTMLDivElement | null;
    const sessionIdInput = document.getElementById('session-id') as HTMLInputElement | null;
    const clearMemoryBtn = document.getElementById('clear-memory-btn') as HTMLButtonElement | null;
    const thoughtLogs = document.getElementById('thought-logs') as HTMLDivElement | null;
    const dbVariables = document.getElementById('db-variables') as HTMLDivElement | null;
    const sampleBtns = document.querySelectorAll('.sample-btn') as NodeListOf<HTMLButtonElement>;

    // State indicating if an agent response generation is currently in progress
    let isGenerating: boolean = false;

    // Helper: Scroll chat window to the bottom for new messages
    const scrollToBottom = (): void => {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    };

    // Helper: Formats basic markdown elements (bold, bullet lists, sections) into HTML markup
    const formatResponseText = (text: string): string => {
        if (!text) return '';
        
        // Escape special HTML tags to prevent cross-site scripting (XSS)
        let html: string = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
        
        // Convert headers (## or ###) to styled inline header tags
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');
        
        // Convert markdown bold (**word**) to HTML strong tags
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert markdown lists (- or *) to HTML bulleted lists
        html = html.replace(/^\s*[\-\*]\s+(.*$)/gim, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
        html = html.replace(/<\/ul>\s*<ul>/g, ''); // Concatenate adjacent list blocks
        
        // Handle newlines: preserve double-breaks as paragraphs, single breaks as normal breaks
        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/\n/g, '<br>');
        
        return `<p>${html}</p>`;
    };

    // Load and render SQLite persistent session memories on page load or session ID switch
    const loadSessionMemory = async (): Promise<void> => {
        if (!sessionIdInput || !dbVariables) return;
        const sessionId: string = sessionIdInput.value.trim() || 'default';
        try {
            const response: Response = await fetch(`/memory?session_id=${encodeURIComponent(sessionId)}`);
            const data: MemoryData = await response.json();
            if (response.ok) {
                renderMemory(data.memory);
            }
        } catch (error) {
            console.error('Failed to load session memory:', error);
        }
    };

    // Renders the SQLite memory key-value properties into the CRM database inspector panel
    const renderMemory = (memory: Record<string, string>): void => {
        if (!dbVariables) return;
        if (!memory || Object.keys(memory).length === 0) {
            dbVariables.innerHTML = `
                <div class="empty-state-db">
                    <p>No variables saved in SQLite yet. As you converse, the coach agent will call <code>store_fact()</code> to remember things.</p>
                </div>
            `;
            return;
        }

        let html: string = '<div class="db-grid">';
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

    // Renders real-time multi-agent routing traces and local function executions (thought stream logs)
    const renderTraceLogs = (trace: TraceEntry[]): void => {
        if (!thoughtLogs) return;
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
        trace.forEach((entry: TraceEntry) => {
            const entryDiv: HTMLDivElement = document.createElement('div');
            
            // Assign class highlight color depending on the micro-agent executing the action
            const agentClass: string = entry.agent === 'ContactAnalystAgent' ? 'analyst' : 'auditor';
            entryDiv.className = `trace-entry ${agentClass}`;
            
            let contentHtml: string = '';
            
            // Parse and format visual trace items based on logging actions
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
                const previewMsg: string = entry.message || '';
                contentHtml = `
                    <div class="trace-header">
                        <span class="agent-tag"><i class="fa-solid fa-circle-check"></i> ${entry.agent}</span>
                        <span class="action-tag">Output</span>
                    </div>
                    <div class="trace-desc">${previewMsg.substring(0, 150)}${previewMsg.length > 150 ? '...' : ''}</div>
                `;
            }
            
            entryDiv.innerHTML = contentHtml;
            thoughtLogs.appendChild(entryDiv);
        });
        
        // Scroll the thought trace container to show the latest routing logs
        thoughtLogs.scrollTop = thoughtLogs.scrollHeight;
    };

    // Submits the chat query asynchronously to the Flask API endpoint
    const sendQuery = async (queryText: string): Promise<void> => {
        if (!queryText.trim() || isGenerating) return;
        if (!chatInput || !sendBtn || !chatMessages || !sessionIdInput || !thoughtLogs) return;
        
        isGenerating = true;
        chatInput.value = '';
        chatInput.style.height = 'auto'; // Reset textbox size
        sendBtn.disabled = true;

        // 1. Render User message block
        const userDiv: HTMLDivElement = document.createElement('div');
        userDiv.className = 'message user-message';
        userDiv.textContent = queryText;
        chatMessages.appendChild(userDiv);
        scrollToBottom();

        // 2. Render typing indicator bubble
        const typingDiv: HTMLDivElement = document.createElement('div');
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

        // Show execution startup label in thought log panel
        thoughtLogs.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner" style="animation: rotate 1s linear infinite;"></i>
                <p>Executing agents in Vertex AI and scanning SQLite schema...</p>
            </div>
        `;

        const sessionId: string = sessionIdInput.value.trim() || 'default';

        try {
            const response: Response = await fetch('/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: queryText, session_id: sessionId })
            });
            
            const data: QueryResponseData = await response.json();
            
            // Remove typing indicator bubble
            typingDiv.remove();
            
            if (response.ok) {
                // 3. Render final agent reply
                const agentDiv: HTMLDivElement = document.createElement('div');
                agentDiv.className = 'message agent-message';
                agentDiv.innerHTML = formatResponseText(data.response);
                chatMessages.appendChild(agentDiv);
                
                // 4. Update logs traces and SQLite memories
                renderTraceLogs(data.trace);
                renderMemory(data.memory);
            } else {
                // Render Backend/Vertex API connection error
                const errorDiv: HTMLDivElement = document.createElement('div');
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
            
            const errorDiv: HTMLDivElement = document.createElement('div');
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

    // Event Listeners for action events
    if (sendBtn && chatInput) {
        sendBtn.addEventListener('click', () => {
            sendQuery(chatInput.value);
        });

        chatInput.addEventListener('keydown', (e: KeyboardEvent) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendQuery(chatInput.value);
            }
        });

        // Textarea auto-grow dynamically based on scrollHeight
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = (chatInput.scrollHeight) + 'px';
        });
    }

    // Load clean memories and state when switching Session IDs
    if (sessionIdInput && thoughtLogs) {
        sessionIdInput.addEventListener('change', () => {
            loadSessionMemory();
            thoughtLogs.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-spinner"></i>
                    <p>Switched session. Send a message to trace agent interactions.</p>
                </div>
            `;
        });
    }

    // Handles wiping SQLite database persistent facts for the current session
    if (clearMemoryBtn && sessionIdInput && chatMessages) {
        clearMemoryBtn.addEventListener('click', async () => {
            const sessionId: string = sessionIdInput.value.trim() || 'default';
            if (confirm(`Are you sure you want to clear the SQLite session memory for: "${sessionId}"?`)) {
                try {
                    const response: Response = await fetch('/clear', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ session_id: sessionId })
                    });
                    const data: ClearResponseData = await response.json();
                    if (response.ok) {
                        alert(data.message);
                        renderMemory({});
                        
                        const sysDiv: HTMLDivElement = document.createElement('div');
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
    }

    // Wire up prompt clicks to dispatch queries instantly
    sampleBtns.forEach((btn: HTMLButtonElement) => {
        btn.addEventListener('click', () => {
            const qText: string | null = btn.getAttribute('data-query');
            if (qText) {
                sendQuery(qText);
            }
        });
    });

    // Fetch session variables on page load
    loadSessionMemory();
});
