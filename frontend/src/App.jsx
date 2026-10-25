import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth.jsx'
import Auth from './pages/Auth.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Builder from './pages/Builder.jsx'
import Trips from './pages/Trips.jsx'
import TripView from './pages/TripView.jsx'
import Explore from './pages/Explore.jsx'

function Logo() {
  return (
    <svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true">
      <rect width="32" height="32" rx="8" fill="#1b3c47" />
      <path d="M8 22 L16 8 L24 22 Z" fill="none" stroke="#E3A02B" strokeWidth="2.5" strokeLinejoin="round" />
    </svg>
  )
}

function Shell({ children }) {
  const { user, logout } = useAuth()
  return (
    <div className="shell">
      <aside className="side">
        <div className="brand"><Logo /> Wayfare</div>
        <nav className="nav">
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/plan">Plan a trip</NavLink>
          <NavLink to="/trips">My trips</NavLink>
          <NavLink to="/explore">Explore</NavLink>
        </nav>
        <div className="side-foot">
          <div className="who">{user.name}</div>
          <div className="mail">{user.email}</div>
          <button className="btn ghost sm" style={{ marginTop: 10, color: '#cfe0e0', borderColor: '#2b4c57' }} onClick={logout}>
            Sign out
          </button>
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  )
}

export default function App() {
  const { user, loading } = useAuth()
  if (loading) return <div className="center">Loading...</div>
  if (!user) {
    return (
      <Routes>
        <Route path="*" element={<Auth />} />
      </Routes>
    )
  }
  return (
    <Shell>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/plan" element={<Builder />} />
        <Route path="/trips" element={<Trips />} />
        <Route path="/trips/:id" element={<TripView />} />
        <Route path="/explore" element={<Explore />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  )
}
