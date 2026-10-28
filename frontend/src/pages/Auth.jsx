import { useState } from 'react'
import { useAuth } from '../auth.jsx'
import { TriporaLogo } from '../App.jsx'

const DEMO = [
  { name: 'Admin User', email: 'admin@travelplanner.com', pw: 'Admin@123', note: 'Admin access' },
  { name: 'Aarav Sharma', email: 'aarav@example.com', pw: 'Aarav@123', note: 'Solo weekend' },
  { name: 'Priya Nair', email: 'priya@example.com', pw: 'Priya@123', note: 'Couple trip' },
  { name: 'Rohan Mehta', email: 'rohan@example.com', pw: 'Rohan@123', note: 'Partner and group' },
  { name: 'Meera Iyer', email: 'meera@example.com', pw: 'Meera@123', note: 'Group organiser' },
  { name: 'Karan Singh', email: 'karan@example.com', pw: 'Karan@123', note: 'City break' },
  { name: 'Sneha Reddy', email: 'sneha@example.com', pw: 'Sneha@123', note: 'Scenic retreat' },
]

export default function Auth() {
  const { login, register } = useAuth()
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ name: '', email: '', password: '', home_city: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      if (mode === 'login') await login(form.email, form.password)
      else await register(form)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth">
      <section className="auth-art">
        <div className="brand">
          <TriporaLogo size={36} />
          <span>Tripora</span>
          <span className="brand-badge">Travel Platform</span>
        </div>
        <div>
          <div className="auth-badge">
            <span style={{ display: 'inline-block', width: 6, height: 6, borderRadius: '50%', background: '#c88d2a' }} />
            Intelligent Itinerary Design
          </div>
          <h1>Plan the journey, not the logistics.</h1>
          <p>
            Tell us where, when, and what you love. Tripora crafts a day-by-day itinerary with attractions,
            handpicked dining, accommodation, and local transport, precision-fitted to your budget.
          </p>
          <div className="auth-features">
            <div className="auth-feat-item">
              <span className="dot" />
              <span>Clustered daily geographic routing to minimize travel time</span>
            </div>
            <div className="auth-feat-item">
              <span className="dot" />
              <span>Smart tier-based budget balancing with zero guesswork</span>
            </div>
            <div className="auth-feat-item">
              <span className="dot" />
              <span>Collaborative multi-traveler interest blending</span>
            </div>
          </div>
        </div>
        <svg className="route" viewBox="0 0 400 220" fill="none" aria-hidden="true">
          <path d="M10 200 C 90 190, 80 110, 160 120 S 250 40, 330 70 S 380 20, 392 12" stroke="#245C48" strokeWidth="3" strokeDasharray="3 8" strokeLinecap="round" />
          <circle cx="10" cy="200" r="7" fill="#245C48" />
          <circle cx="160" cy="120" r="6" fill="#F8F7F2" stroke="#245C48" strokeWidth="2" />
          <circle cx="330" cy="70" r="6" fill="#F8F7F2" stroke="#245C48" strokeWidth="2" />
          <circle cx="392" cy="12" r="8" fill="#C88D2A" />
        </svg>
      </section>

      <section className="auth-form">
        <div className="auth-card">
          <h2 style={{ fontSize: 26, letterSpacing: '-0.02em' }}>
            {mode === 'login' ? 'Welcome back to Tripora' : 'Create your account'}
          </h2>
          <p className="muted small" style={{ margin: '6px 0 22px' }}>
            {mode === 'login' ? 'Sign in to access your curated itineraries.' : 'Get started with personalized travel planning.'}
          </p>

          <form className="stack" onSubmit={submit} style={{ gap: 14 }}>
            {mode === 'register' && (
              <>
                <label className="field">
                  <span>Full name</span>
                  <input required minLength={2} value={form.name} onChange={set('name')} placeholder="e.g. Priya Nair" />
                </label>
                <label className="field">
                  <span>Home city (optional)</span>
                  <input value={form.home_city} onChange={set('home_city')} placeholder="e.g. Mumbai" />
                </label>
              </>
            )}
            <label className="field">
              <span>Email address</span>
              <input required type="email" value={form.email} onChange={set('email')} autoComplete="email" placeholder="name@example.com" />
            </label>
            <label className="field">
              <span>Password</span>
              <input required type="password" minLength={6} value={form.password} onChange={set('password')} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} />
            </label>

            {error && <div className="alert" role="alert">{error}</div>}

            <button className="btn" disabled={busy} style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}>
              {busy ? 'Connecting...' : mode === 'login' ? 'Sign in' : 'Create account'}
            </button>
          </form>

          <p className="small muted" style={{ marginTop: 18, textAlign: 'center' }}>
            {mode === 'login' ? "Don't have an account yet? " : 'Already registered? '}
            <a href="#" onClick={(e) => { e.preventDefault(); setError(''); setMode(mode === 'login' ? 'register' : 'login') }}>
              {mode === 'login' ? 'Create an account' : 'Sign in'}
            </a>
          </p>

          {mode === 'login' && (
            <div style={{ marginTop: 26, paddingTop: 20, borderTop: '1px solid var(--line)' }}>
              <div className="small muted" style={{ fontWeight: 600 }}>Demo accounts (click to fill):</div>
              <div className="demo-list">
                {DEMO.map((d) => (
                  <button type="button" key={d.email} className="demo" onClick={() => setForm({ ...form, email: d.email, password: d.pw })}>
                    <b>{d.name}</b>
                    <small>{d.note}</small>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
