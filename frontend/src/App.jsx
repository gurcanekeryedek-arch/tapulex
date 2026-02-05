import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, createContext } from 'react'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import Chat from './pages/Chat'
import './index.css'

export const AuthContext = createContext()

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)

  const login = (userData) => {
    setIsAuthenticated(true)
    setUser(userData)
  }

  const logout = () => {
    setIsAuthenticated(false)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      <Router>
        <Routes>
          <Route path="/login" element={
            isAuthenticated ? <Navigate to="/" replace /> : <Login />
          } />
          <Route path="/" element={
            isAuthenticated ? <Layout /> : <Navigate to="/login" replace />
          }>
            <Route index element={<Dashboard />} />
            <Route path="documents" element={<Documents />} />
            <Route path="chat" element={<Chat />} />
          </Route>
        </Routes>
      </Router>
    </AuthContext.Provider>
  )
}

export default App
