import { useState } from 'react'
import { useAuth } from '../auth.jsx'

const DEMO = [
  { name: 'Admin User', email: 'admin@travelplanner.com', pw: 'Admin@123', note: 'Admin' },
  { name: 'Aarav Sharma', email: 'aarav@example.com', pw: 'Aarav@123', note: 'Solo weekend' },
  { name: 'Priya Nair', email: 'priya@example.com', pw: 'Priya@123', note: 'Couple trip' },
  { name: 'Rohan Mehta', email: 'rohan@example.com', pw: 'Rohan@123', note: 'Partner and group' },
  { name: 'Meera Iyer', email: 'meera@example.com', pw: 'Meera@123', note: 'Group organiser' },
  { name: 'Karan Singh', email: 'karan@example.com', pw: 'Karan@123', note: 'City break' },
  { name: 'Sneha Reddy', email: 'sneha@example.com', pw: 'Sneha@123', note: 'Retreat' },
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
        <div className="brand" style={{ padding: 0 }}>Wayfare</div>
        <div>
          <h1>Plan the trip, not the research.</h1>
          <p>Tell us where, when and what you enjoy. Wayfare builds a day-by-day plan with places to eat, stay and get around, priced against your budget.</p>
        </div>
        <svg className="route" viewBox="0 0 400 220" fill="none" aria-hidden="true">
          <path d="M10 200 C 90 190, 80 110, 160 120 S 250 40, 330 70 S 380 20, 392 12" stroke="#E3A02B" strokeWidth="3" strokeDasharray="2 9" strokeLinecap="round" />
          <circle cx="10" cy="200" r="7" fill="#1E7F74" />
          <circle cx="160" cy="120" r="7" fill="#fff" />
          <circle cx="330" cy="70" r="7" fill="#fff" />
          <circle cx="392" cy="12" r="9" fill="#E3A02B" />
        </svg>
      </section>
      <section className="auth-form">
        <h2 style={{ fontSize: 28 }}>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
        <p className="muted" style={{ margin: '6px 0 20px' }}>
          {mode === 'login' ? 'Sign in to open your trips.' : 'It takes a few seconds.'}
        </p>
        <form className="stack" onSubmit={submit}>
          {mode === 'register' && (
            <>
              <label className="field"><span>Full name</span><input required minLength={2} value={form.name} onChange={set('name')} /></label>
              <label className="field"><span>Home city (optional)</span><input value={form.home_city} onChange={set('home_city')} /></label>
            </>
          )}
          <label className="field"><span>Email</span><input required type="email" value={form.email} onChange={set('email')} autoComplete="email" /></label>
          <label className="field"><span>Password</span><input required type="password" minLength={6} value={form.password} onChange={set('password')} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} /></label>
          {error && <div className="alert" role="alert">{error}</div>}
          <button className="btn" disabled={busy} style={{ width: '100%', justifyContent: 'center' }}>
            {busy ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>
        <p className="small muted" style={{ marginTop: 14 }}>
          {mode === 'login' ? 'New here? ' : 'Already registered? '}
          <a href="#" onClick={(e) => { e.preventDefault(); setError(''); setMode(mode === 'login' ? 'register' : 'login') }}>
            {mode === 'login' ? 'Create an account' : 'Sign in'}
          </a>
        </p>

        {mode === 'login' && (
          <div style={{ marginTop: 26 }}>
            <div className="small muted">Demo accounts (click to fill)</div>
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
      </section>
    </div>
  )
}
