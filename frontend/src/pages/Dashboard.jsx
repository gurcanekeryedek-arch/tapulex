import { useState, useEffect } from 'react'
import {
    FileText,
    MessageSquare,
    TrendingUp,
    Database,
    ArrowUpRight,
    Sparkles,
    Clock,
    CheckCircle2,
    Loader2
} from 'lucide-react'
import './Dashboard.css'

function Dashboard() {
    const [statsData, setStatsData] = useState(null)
    const [recentDocs, setRecentDocs] = useState([])
    const [recentQuestions, setRecentQuestions] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                // Fetch stats, recent docs and questions in parallel
                const [statsRes, docsRes, questionsRes] = await Promise.all([
                    fetch('http://localhost:8000/api/dashboard/stats'),
                    fetch('http://localhost:8000/api/dashboard/recent-documents'),
                    fetch('http://localhost:8000/api/dashboard/recent-questions')
                ])

                const stats = await statsRes.json()
                const docs = await docsRes.json()
                const questions = await questionsRes.json()

                setStatsData(stats)
                setRecentDocs(docs.documents || [])
                setRecentQuestions(questions.questions || [])
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchDashboardData()
    }, [])

    const stats = [
        {
            label: 'Toplam Doküman',
            value: statsData?.total_documents || '0',
            change: `+${statsData?.documents_this_week || 0} bu hafta`,
            icon: FileText,
            color: 'primary'
        },
        {
            label: 'Sohbet Sayısı',
            value: statsData?.total_chats || '0',
            change: `+${statsData?.chats_today || 0} bugün`,
            icon: MessageSquare,
            color: 'secondary'
        },
        {
            label: 'Doğruluk Oranı',
            value: `%${statsData?.accuracy_rate || '0'}`,
            change: '+2.3%',
            icon: TrendingUp,
            color: 'success'
        },
        {
            label: 'Vektör Sayısı',
            value: statsData?.total_chunks || '0',
            change: '+1.2K',
            icon: Database,
            color: 'accent'
        },
    ]

    if (loading) {
        return (
            <div className="dashboard-loading">
                <Loader2 size={48} className="animate-spin" />
                <p>Veriler yükleniyor...</p>
            </div>
        )
    }

    return (
        <div className="dashboard animate-fade-in">
            {/* Welcome Section */}
            <section className="welcome-section glass-card">
                <div className="welcome-content">
                    <div className="welcome-icon">
                        <Sparkles size={28} />
                    </div>
                    <div>
                        <h2>Hoş geldiniz! 👋</h2>
                        <p>TapuLex ile dokümanlarınızı akıllıca sorgulayın.</p>
                    </div>
                </div>
                <button className="btn btn-primary" onClick={() => window.location.href = '/chat'}>
                    <MessageSquare size={18} />
                    Sohbete Başla
                </button>
            </section>

            {/* Stats Grid */}
            <section className="stats-grid">
                {stats.map((stat, index) => (
                    <div
                        key={stat.label}
                        className={`stat-card glass-card color-${stat.color}`}
                        style={{ animationDelay: `${index * 0.1}s` }}
                    >
                        <div className="stat-icon">
                            <stat.icon size={24} />
                        </div>
                        <div className="stat-content">
                            <span className="stat-value">{stat.value}</span>
                            <span className="stat-label">{stat.label}</span>
                        </div>
                        <span className="stat-change">
                            <ArrowUpRight size={14} />
                            {stat.change}
                        </span>
                    </div>
                ))}
            </section>

            {/* Two Column Layout */}
            <div className="dashboard-grid">
                {/* Recent Documents */}
                <section className="dashboard-section glass-card">
                    <div className="section-header">
                        <h3>
                            <FileText size={20} />
                            Son Dokümanlar
                        </h3>
                        <button className="btn btn-ghost" onClick={() => window.location.href = '/documents'}>Tümünü Gör</button>
                    </div>
                    <div className="docs-list">
                        {recentDocs.length > 0 ? (
                            recentDocs.map((doc) => (
                                <div key={doc.id} className="doc-item">
                                    <div className="doc-icon">
                                        <FileText size={18} />
                                    </div>
                                    <div className="doc-info">
                                        <span className="doc-name">{doc.filename}</span>
                                        <span className="doc-date">
                                            <Clock size={12} />
                                            {doc.created_at?.split('T')[0]}
                                        </span>
                                    </div>
                                    <span className={`badge badge-${doc.status === 'indexed' ? 'success' : 'processing'}`}>
                                        {doc.status === 'indexed' ? (
                                            <>
                                                <CheckCircle2 size={12} />
                                                İndekslendi
                                            </>
                                        ) : (
                                            <>
                                                <span className="animate-spin">⟳</span>
                                                {doc.status}
                                            </>
                                        )}
                                    </span>
                                </div>
                            ))
                        ) : (
                            <p className="empty-hint">Henüz doküman yüklenmemiş.</p>
                        )}
                    </div>
                </section>

                {/* Recent Questions */}
                <section className="dashboard-section glass-card">
                    <div className="section-header">
                        <h3>
                            <MessageSquare size={20} />
                            Son Sorular
                        </h3>
                        <button className="btn btn-ghost" onClick={() => window.location.href = '/chat'}>Tümünü Gör</button>
                    </div>
                    <div className="questions-list">
                        {recentQuestions.length > 0 ? (
                            recentQuestions.map((q, i) => (
                                <div key={i} className="question-item">
                                    <div className="question-content">
                                        <p className="question-text">{q.content}</p>
                                    </div>
                                    <span className="question-time">{new Date(q.created_at).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}</span>
                                </div>
                            ))
                        ) : (
                            <p className="empty-hint">Henüz soru sorulmamış.</p>
                        )}
                    </div>
                </section>
            </div>
        </div>
    )
}

export default Dashboard
