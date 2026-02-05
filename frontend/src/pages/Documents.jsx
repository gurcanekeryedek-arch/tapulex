import { useState, useRef, useEffect } from 'react'
import {
    Upload,
    FileText,
    File,
    Trash2,
    Search,
    Filter,
    Grid,
    List,
    Clock,
    CheckCircle2,
    AlertCircle,
    Loader2,
    X,
    CloudUpload
} from 'lucide-react'
import './Documents.css'
import { getDocuments, uploadDocument, deleteDocument } from '../services/api'

function Documents() {
    const [documents, setDocuments] = useState([])
    const [searchQuery, setSearchQuery] = useState('')
    const [viewMode, setViewMode] = useState('grid')
    const [isDragging, setIsDragging] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(null)
    const [loading, setLoading] = useState(true)
    const fileInputRef = useRef(null)

    // Load documents from API on mount
    useEffect(() => {
        fetchDocuments()
    }, [])

    const fetchDocuments = async () => {
        try {
            const data = await getDocuments()
            if (data.success && data.documents) {
                setDocuments(data.documents.map(doc => ({
                    id: doc.id,
                    name: doc.filename,
                    type: doc.filename.split('.').pop(),
                    size: formatSize(doc.size_bytes),
                    status: doc.status,
                    date: doc.created_at?.split('T')[0] || new Date().toISOString().split('T')[0],
                    chunks: doc.chunk_count || 0
                })))
            }
        } catch (error) {
            console.error('Failed to fetch documents:', error)
        } finally {
            setLoading(false)
        }
    }

    const formatSize = (bytes) => {
        if (!bytes) return '0 KB'
        if (bytes < 1024) return bytes + ' B'
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
        return (bytes / 1024 / 1024).toFixed(2) + ' MB'
    }

    const handleDragOver = (e) => {
        e.preventDefault()
        setIsDragging(true)
    }

    const handleDragLeave = () => {
        setIsDragging(false)
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setIsDragging(false)
        const files = e.dataTransfer.files
        handleFiles(files)
    }

    const handleFileSelect = (e) => {
        const files = e.target.files
        handleFiles(files)
    }

    const handleFiles = async (files) => {
        if (!files || files.length === 0) return

        const fileList = Array.from(files)

        for (let i = 0; i < fileList.length; i++) {
            const file = fileList[i]
            const fileInfo = `(${i + 1}/${fileList.length}) ${file.name}`

            setUploadProgress({ name: fileInfo, progress: 0 })

            try {
                // Simulate progress
                const progressInterval = setInterval(() => {
                    setUploadProgress(prev => {
                        if (!prev || prev.progress >= 90) return prev
                        return { ...prev, progress: prev.progress + 10 }
                    })
                }, 150)

                // Upload to backend
                const data = await uploadDocument(file)

                clearInterval(progressInterval)
                setUploadProgress(prev => prev ? { ...prev, progress: 100 } : null)

                if (data.success) {
                    // Update state with new doc
                    setDocuments(prev => [{
                        id: data.document?.id || Date.now(),
                        name: file.name,
                        type: file.name.split('.').pop(),
                        size: formatSize(file.size),
                        status: data.document?.status || 'indexed',
                        date: new Date().toISOString().split('T')[0],
                        chunks: 0
                    }, ...prev])
                } else {
                    console.error(`Upload failed for ${file.name}:`, data.detail)
                }
            } catch (error) {
                console.error(`Upload error for ${file.name}:`, error)
            }
        }

        setUploadProgress(null)
        setTimeout(fetchDocuments, 1000)
    }

    const handleDelete = async (docId) => {
        if (!confirm('Bu dokümanı silmek istediğinize emin misiniz?')) return

        try {
            const data = await deleteDocument(docId)
            if (data.success) {
                setDocuments(prev => prev.filter(d => d.id !== docId))
            }
        } catch (error) {
            console.error('Delete error:', error)
        }
    }

    const getStatusBadge = (status) => {
        switch (status) {
            case 'indexed':
                return <span className="badge badge-success"><CheckCircle2 size={12} /> İndekslendi</span>
            case 'processing':
                return <span className="badge badge-processing"><Loader2 size={12} className="animate-spin" /> İşleniyor</span>
            case 'failed':
                return <span className="badge badge-error"><AlertCircle size={12} /> Hata</span>
            case 'uploaded':
                return <span className="badge badge-info"><Clock size={12} /> Yüklendi</span>
            default:
                return <span className="badge badge-info">{status}</span>
        }
    }

    const getFileIcon = (type) => {
        switch (type) {
            case 'pdf':
                return <FileText size={24} className="icon-pdf" />
            case 'docx':
                return <FileText size={24} className="icon-docx" />
            default:
                return <File size={24} />
        }
    }

    const filteredDocs = documents.filter(doc =>
        doc.name.toLowerCase().includes(searchQuery.toLowerCase())
    )

    return (
        <div className="documents-page animate-fade-in">
            {/* Upload Section */}
            <section
                className={`upload-zone glass-card ${isDragging ? 'dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
            >
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    accept=".pdf,.docx,.txt"
                    multiple
                    hidden
                />
                <div className="upload-content">
                    <div className="upload-icon">
                        <CloudUpload size={40} />
                    </div>
                    <h3>Doküman Yükle</h3>
                    <p>Dosyaları sürükleyip bırakın veya <span className="upload-link">gözat</span></p>
                    <span className="upload-hint">PDF, DOCX, TXT desteklenir • Maks. 50MB</span>
                </div>

                {/* Upload Progress */}
                {uploadProgress && (
                    <div className="upload-progress glass-card" onClick={e => e.stopPropagation()}>
                        <div className="progress-info">
                            <FileText size={20} />
                            <span>{uploadProgress.name}</span>
                            <span className="progress-percent">{uploadProgress.progress}%</span>
                        </div>
                        <div className="progress-bar">
                            <div
                                className="progress-fill"
                                style={{ width: `${uploadProgress.progress}%` }}
                            ></div>
                        </div>
                    </div>
                )}
            </section>

            {/* Toolbar */}
            <div className="documents-toolbar">
                <div className="search-wrapper">
                    <Search size={18} className="search-icon" />
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Dokümanlarda ara..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
                <div className="toolbar-actions">
                    <button className="btn btn-secondary" onClick={fetchDocuments}>
                        <Loader2 size={18} className={loading ? 'animate-spin' : ''} />
                        Yenile
                    </button>
                    <div className="view-toggle">
                        <button
                            className={`toggle-btn ${viewMode === 'grid' ? 'active' : ''}`}
                            onClick={() => setViewMode('grid')}
                        >
                            <Grid size={18} />
                        </button>
                        <button
                            className={`toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
                            onClick={() => setViewMode('list')}
                        >
                            <List size={18} />
                        </button>
                    </div>
                </div>
            </div>

            {/* Documents Grid/List */}
            {loading ? (
                <div className="empty-state glass-card">
                    <Loader2 size={48} className="animate-spin" />
                    <h3>Yükleniyor...</h3>
                </div>
            ) : (
                <div className={`documents-container ${viewMode}`}>
                    {filteredDocs.map((doc, index) => (
                        <div
                            key={doc.id}
                            className="doc-card glass-card"
                            style={{ animationDelay: `${index * 0.05}s` }}
                        >
                            <div className="doc-icon-wrapper">
                                {getFileIcon(doc.type)}
                            </div>
                            <div className="doc-details">
                                <h4 className="doc-title">{doc.name}</h4>
                                <div className="doc-meta">
                                    <span><Clock size={12} /> {doc.date}</span>
                                    <span>{doc.size}</span>
                                    {doc.chunks > 0 && <span>{doc.chunks} chunk</span>}
                                </div>
                            </div>
                            <div className="doc-actions">
                                {getStatusBadge(doc.status)}
                                <button
                                    className="btn btn-ghost delete-btn"
                                    onClick={() => handleDelete(doc.id)}
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {!loading && filteredDocs.length === 0 && (
                <div className="empty-state glass-card">
                    <FileText size={48} />
                    <h3>Doküman bulunamadı</h3>
                    <p>Henüz doküman yüklenmemiş veya arama kriterlerinize uygun doküman yok.</p>
                </div>
            )}
        </div>
    )
}

export default Documents
