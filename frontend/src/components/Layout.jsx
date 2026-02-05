import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import './Layout.css'

function Layout() {
    return (
        <div className="app-layout">
            <Sidebar />
            <div className="layout-content">
                <Header />
                <main className="main-content">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}

export default Layout
