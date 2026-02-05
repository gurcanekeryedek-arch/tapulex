import { useState, useRef, useEffect } from 'react'
import {
    Send,
    Paperclip,
    Sparkles,
    User,
    FileText,
    ChevronRight,
    Copy,
    ThumbsUp,
    ThumbsDown,
    RefreshCw,
    ExternalLink,
    X
} from 'lucide-react'
import './Chat.css'

const initialMessages = [
    {
        id: 1,
        type: 'assistant',
        content: 'Merhaba! 👋 Ben DocChatAI, şirket dokümanlarınız hakkında sorularınızı yanıtlamak için buradayım. Size nasıl yardımcı olabilirim?',
        timestamp: new Date().toISOString(),
        sources: []
    }
]

const sampleSources = [
    { file: 'Şirket Politikaları 2024.pdf', page: 12, excerpt: '...yıllık izin hakkı 14 iş günüdür...' },
    { file: 'İK Yönetmeliği.docx', page: 5, excerpt: '...izin talepleri en az 3 gün önceden...' }
]

function Chat() {
    const [messages, setMessages] = useState(initialMessages)
    const [inputValue, setInputValue] = useState('')
    const [isTyping, setIsTyping] = useState(false)
    const [showSources, setShowSources] = useState(false)
    const [selectedSources, setSelectedSources] = useState([])
    const [suggestedQuestions, setSuggestedQuestions] = useState([])
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    useEffect(() => {
        fetchSuggestions()
    }, [])

    const fetchSuggestions = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/chat/suggestions')
            const data = await response.json()
            if (data.suggestions) {
                setSuggestedQuestions(data.suggestions)
            }
        } catch (error) {
            console.error('Failed to fetch suggestions:', error)
            setSuggestedQuestions([
                'Yıllık izin hakları nedir?',
                'Evden çalışma politikası',
                'Performans değerlendirme süreci',
                'Yan haklar nelerdir?'
            ])
        }
    }

    const handleSend = async () => {
        if (!inputValue.trim()) return

        const userMessage = {
            id: Date.now(),
            type: 'user',
            content: inputValue,
            timestamp: new Date().toISOString()
        }

        setMessages(prev => [...prev, userMessage])
        setInputValue('')
        setIsTyping(true)

        try {
            // Call real backend API
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage.content,
                    conversation_history: messages.filter(m => m.type !== 'assistant' || m.id !== 1).map(m => ({
                        role: m.type === 'user' ? 'user' : 'assistant',
                        content: m.content
                    }))
                })
            })

            const data = await response.json()

            const aiResponse = {
                id: Date.now() + 1,
                type: 'assistant',
                content: data.answer || 'Bir hata oluştu.',
                timestamp: new Date().toISOString(),
                sources: data.sources?.map(s => ({
                    file: s.filename,
                    page: s.page || '-',
                    excerpt: s.excerpt
                })) || []
            }

            setIsTyping(false)
            setMessages(prev => [...prev, aiResponse])
        } catch (error) {
            console.error('Chat API error:', error)
            setIsTyping(false)
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                type: 'assistant',
                content: 'Bağlantı hatası oluştu. Lütfen tekrar deneyin.',
                timestamp: new Date().toISOString(),
                sources: []
            }])
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const showSourcesPanel = (sources) => {
        setSelectedSources(sources)
        setShowSources(true)
    }



    return (
        <div className="chat-page">
            <div className={`chat-container ${showSources ? 'with-sources' : ''}`}>
                {/* Chat Messages */}
                <div className="chat-messages">
                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`message ${message.type} animate-slide-up`}
                        >
                            <div className="message-avatar">
                                {message.type === 'assistant' ? (
                                    <div className="avatar-ai">
                                        <Sparkles size={18} />
                                    </div>
                                ) : (
                                    <div className="avatar-user">
                                        <User size={18} />
                                    </div>
                                )}
                            </div>
                            <div className="message-content">
                                <div className="message-header">
                                    <span className="message-author">
                                        {message.type === 'assistant' ? 'DocChatAI' : 'Sen'}
                                    </span>
                                    <span className="message-time">
                                        {new Date(message.timestamp).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                                <div className="message-text">
                                    {message.content.split('\n').map((line, i) => (
                                        <p key={i}>{line}</p>
                                    ))}
                                </div>
                                {message.type === 'assistant' && message.sources?.length > 0 && (
                                    <button
                                        className="sources-btn"
                                        onClick={() => showSourcesPanel(message.sources)}
                                    >
                                        <FileText size={14} />
                                        {message.sources.length} kaynak
                                        <ChevronRight size={14} />
                                    </button>
                                )}
                                {message.type === 'assistant' && (
                                    <div className="message-actions">
                                        <button className="action-btn" title="Kopyala">
                                            <Copy size={14} />
                                        </button>
                                        <button className="action-btn" title="Beğen">
                                            <ThumbsUp size={14} />
                                        </button>
                                        <button className="action-btn" title="Beğenme">
                                            <ThumbsDown size={14} />
                                        </button>
                                        <button className="action-btn" title="Yeniden oluştur">
                                            <RefreshCw size={14} />
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {/* Typing Indicator */}
                    {isTyping && (
                        <div className="message assistant animate-fade-in">
                            <div className="message-avatar">
                                <div className="avatar-ai">
                                    <Sparkles size={18} />
                                </div>
                            </div>
                            <div className="message-content">
                                <div className="typing-indicator">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Suggested Questions */}
                {messages.length === 1 && (
                    <div className="suggested-questions animate-fade-in">
                        <span className="suggestions-label">Önerilen sorular:</span>
                        <div className="suggestions-list">
                            {suggestedQuestions.map((q, i) => (
                                <button
                                    key={i}
                                    className="suggestion-chip"
                                    onClick={() => setInputValue(q)}
                                >
                                    {q}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Input Area */}
                <div className="chat-input-wrapper glass-card">
                    <button className="attach-btn">
                        <Paperclip size={20} />
                    </button>
                    <textarea
                        className="chat-input"
                        placeholder="Dokümanlar hakkında bir soru sorun..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        rows={1}
                    />
                    <button
                        className="send-btn"
                        onClick={handleSend}
                        disabled={!inputValue.trim() || isTyping}
                    >
                        <Send size={20} />
                    </button>
                </div>
            </div>

            {/* Sources Panel */}
            <div className={`sources-panel glass-card ${showSources ? 'open' : ''}`}>
                <div className="sources-header">
                    <h3>
                        <FileText size={18} />
                        Kaynaklar
                    </h3>
                    <button className="close-btn" onClick={() => setShowSources(false)}>
                        <X size={18} />
                    </button>
                </div>
                <div className="sources-list">
                    {selectedSources.map((source, i) => (
                        <div key={i} className="source-item">
                            <div className="source-icon">
                                <FileText size={16} />
                            </div>
                            <div className="source-content">
                                <h4>{source.file}</h4>
                                <span className="source-page">Sayfa {source.page}</span>
                                <p className="source-excerpt">"{source.excerpt}"</p>
                            </div>
                            <button className="source-link">
                                <ExternalLink size={14} />
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default Chat
