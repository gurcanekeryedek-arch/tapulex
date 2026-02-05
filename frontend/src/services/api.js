const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Auth
export async function login(email, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    return response.json();
}

export async function logout() {
    const response = await fetch(`${API_BASE}/auth/logout`, { method: 'POST' });
    return response.json();
}

// Documents
export async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        body: formData
    });
    return response.json();
}

export async function getDocuments() {
    const response = await fetch(`${API_BASE}/documents`);
    return response.json();
}

export async function deleteDocument(documentId) {
    const response = await fetch(`${API_BASE}/documents/${documentId}`, {
        method: 'DELETE'
    });
    return response.json();
}

// Chat
export async function sendChatMessage(message, conversationHistory = []) {
    const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, conversation_history: conversationHistory })
    });
    return response.json();
}

export async function getChatSuggestions() {
    const response = await fetch(`${API_BASE}/chat/suggestions`);
    return response.json();
}

// Dashboard
export async function getDashboardStats() {
    const response = await fetch(`${API_BASE}/dashboard/stats`);
    return response.json();
}

export async function getRecentDocuments() {
    const response = await fetch(`${API_BASE}/dashboard/recent-documents`);
    return response.json();
}

export async function getRecentQuestions() {
    const response = await fetch(`${API_BASE}/dashboard/recent-questions`);
    return response.json();
}

// Feedback
export async function submitFeedback(sessionId, score, comment) {
    const response = await fetch(`${API_BASE}/chat/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, score, comment })
    });
    return response.json();
}
