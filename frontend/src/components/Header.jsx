import { useLocation } from 'react-router-dom'
import { Search, Bell, Moon, Sun } from 'lucide-react'
import { useState } from 'react'
import './Header.css'

const pageTitles = {
    '/': 'Dashboard',
    '/documents': 'Dokümanlar',
    '/chat': 'AI Sohbet',
}

function Header() {
    const location = useLocation()
    const [darkMode, setDarkMode] = useState(true)
    const title = pageTitles[location.pathname] || 'TapuLex'

    return (
        <header className="header glass-card">
            <div className="header-left">
                <h1 className="page-title">{title}</h1>
            </div>

            <div className="header-center">
                <div className="search-wrapper">
                    <Search size={18} className="search-icon" />
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Dokümanlarda ara..."
                    />
                    <span className="search-shortcut">⌘K</span>
                </div>
            </div>

            <div className="header-right">
                <button className="header-btn" onClick={() => setDarkMode(!darkMode)}>
                    {darkMode ? <Sun size={20} /> : <Moon size={20} />}
                </button>
                <button className="header-btn notification-btn">
                    <Bell size={20} />
                    <span className="notification-dot"></span>
                </button>
            </div>
        </header>
    )
}

export default Header
