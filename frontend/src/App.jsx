import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth.jsx'
import Auth from './pages/Auth.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Builder from './pages/Builder.jsx'
import Trips from './pages/Trips.jsx'
import TripView from './pages/TripView.jsx'
import Explore from './pages/Explore.jsx'

export function TriporaLogo({ size = 30 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <rect width="32" height="32" rx="8" fill="#245C48" />
      <path d="M7 23 L16 8 L25 23" fill="none" stroke="#F8F7F2" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M12 23 L16 15 L20 23" fill="#E7EEE8" />
      <circle cx="16" cy="11.5" r="2" fill="#C88D2A" />
    </svg>
  )
}

function Shell({ children }) {
  const { user, logout } = useAuth()
  return (
    <div className="shell">
      <aside className="side">
        <div className="brand">
          <TriporaLogo size={32} />
          <span>Tripora</span>
          <span className="brand-badge">Planner</span>
        </div>
        <nav className="nav">
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/plan">Plan a trip</NavLink>
          <NavLink to="/trips">My trips</NavLink>
          <NavLink to="/explore">Explore</NavLink>
        </nav>
        <div className="side-foot">
          <div className="who">{user.name}</div>
          <div className="mail">{user.email}</div>
          <button
            className="btn ghost sm"
            style={{ marginTop: 12, width: '100%', justifyContent: 'center', color: '#cad8ce', borderColor: 'rgba(255, 255, 255, 0.15)' }}
            onClick={logout}
          >
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
  if (loading) return <div className="center">Loading Tripora...</div>
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
