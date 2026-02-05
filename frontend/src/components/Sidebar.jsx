import { NavLink, useLocation } from 'react-router-dom'
import {
    LayoutDashboard,
    FileText,
    MessageSquare,
    Settings,
    LogOut,
    Sparkles
} from 'lucide-react'
import { useContext } from 'react'
import { AuthContext } from '../App'
import './Sidebar.css'

const menuItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/documents', icon: FileText, label: 'Dokümanlar' },
    { path: '/chat', icon: MessageSquare, label: 'Sohbet' },
]

function Sidebar() {
    const { logout, user } = useContext(AuthContext)
    const location = useLocation()

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="logo">
                    <div className="logo-icon">
                        <Sparkles size={24} />
                    </div>
                    <span className="logo-text">Tapu<span className="logo-accent">Lex</span></span>
                </div>
            </div>

            <nav className="sidebar-nav">
                <div className="nav-section">
                    <span className="nav-section-title">Menü</span>
                    {menuItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `nav-item ${isActive ? 'active' : ''}`
                            }
                        >
                            <item.icon size={20} />
                            <span>{item.label}</span>
                            {item.path === '/chat' && (
                                <span className="nav-badge">AI</span>
                            )}
                        </NavLink>
                    ))}
                </div>
            </nav>

            <div className="sidebar-footer">
                <div className="user-info glass-card">
                    <div className="user-avatar">
                        {user?.name?.charAt(0) || 'U'}
                    </div>
                    <div className="user-details">
                        <span className="user-name">{user?.name || 'Kullanıcı'}</span>
                        <span className="user-role">{user?.role || 'Admin'}</span>
                    </div>
                </div>
                <button className="btn btn-ghost logout-btn" onClick={logout}>
                    <LogOut size={18} />
                    <span>Çıkış</span>
                </button>
            </div>
        </aside>
    )
}

export default Sidebar
