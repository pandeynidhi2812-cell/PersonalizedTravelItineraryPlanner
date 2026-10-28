import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { fmtRange, inr } from '../format.js'

const PRESETS = [
  {
    key: 'solo',
    title: 'Solo weekend getaway',
    blurb: 'Two or three unhurried days, authentic street food, and sights actually worth your time.',
    meta: '1 traveller · 3 days · Budget stay',
    badge: 'Quick Break',
    values: { title: 'Weekend getaway', travelers: 1, budget: 10000, style: 'budget', pace: 'relaxed', interests: ['food', 'sightseeing'], days: 3 },
  },
  {
    key: 'couple',
    title: 'Romantic couple escape',
    blurb: 'Scenic viewpoints, sunset dinners, and a premium heritage stay.',
    meta: '2 travellers · 4 days · Premium stay',
    badge: 'Popular',
    values: { title: 'Romantic escape', travelers: 2, budget: 85000, style: 'premium', pace: 'relaxed', interests: ['romantic', 'relaxation', 'sightseeing'], days: 4 },
  },
  {
    key: 'group',
    title: 'Friends adventure trip',
    blurb: 'A packed multi-day itinerary with shared transport costs and balanced group activities.',
    meta: '5 travellers · 5 days · Mid-range stay',
    badge: 'Group Plan',
    values: { title: 'Friends trip', travelers: 5, budget: 95000, style: 'mid', pace: 'packed', interests: ['adventure', 'culture', 'nature'], days: 5 },
  },
]

export default function Dashboard() {
  const { user } = useAuth()
  const nav = useNavigate()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/dashboard').then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="alert">{error}</div>
  if (!data) return <div className="muted">Loading your Tripora dashboard...</div>
  const { stats, next_trip: next, recent } = data

  return (
    <div className="stack">
      <div className="page-head">
        <div>
          <div className="small muted" style={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--forest)' }}>
            Tripora Overview
          </div>
          <h1 style={{ marginTop: 2 }}>Welcome back, {user.name.split(' ')[0]}</h1>
          <p>
            {next
              ? `Your upcoming journey is ${next.title} (${fmtRange(next.start_date, next.end_date)}).`
              : 'You have no active trips right now. Pick a preset or craft a new itinerary below.'}
          </p>
        </div>
        <Link className="btn" to="/plan">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Plan a new trip
        </Link>
      </div>

      <div className="grid g4">
        <div className="stat">
          <b>{stats.total_trips}</b>
          <span>Total itineraries</span>
        </div>
        <div className="stat">
          <b>{stats.upcoming_trips}</b>
          <span>Upcoming journeys</span>
        </div>
        <div className="stat">
          <b>{inr(stats.estimated_spend)}</b>
          <span>Estimated total spend</span>
        </div>
        <div className="stat">
          <b>{stats.shared_trips}</b>
          <span>Co-planned trips</span>
        </div>
      </div>

      <section>
        <div className="row between" style={{ marginBottom: 14 }}>
          <div>
            <h2>Start with a curated scenario</h2>
            <p className="small muted">Pre-configured templates tailored to different group sizes and paces.</p>
          </div>
        </div>
        <div className="presets">
          {PRESETS.map((p) => (
            <button key={p.key} className="preset" onClick={() => nav('/plan', { state: { preset: p.values } })}>
              <div className="row between" style={{ marginBottom: 8 }}>
                <span className="tag" style={{ background: 'var(--forest-soft)', color: 'var(--forest-dark)' }}>{p.badge}</span>
                <span className="small muted">→</span>
              </div>
              <h3>{p.title}</h3>
              <p>{p.blurb}</p>
              <div className="meta">{p.meta}</div>
            </button>
          ))}
        </div>
      </section>

      <section className="card">
        <div className="row between" style={{ paddingBottom: 14, borderBottom: '1px solid var(--line)' }}>
          <div>
            <h2>Recently updated itineraries</h2>
            <p className="small muted">Jump back into your recent travel plans</p>
          </div>
          <Link to="/trips" className="btn ghost sm">View all trips ({stats.total_trips})</Link>
        </div>
        {recent.length === 0 && (
          <p className="muted" style={{ padding: '24px 0', textAlign: 'center' }}>
            No trips planned yet. Click "Plan a new trip" to get started!
          </p>
        )}
        {recent.map((t) => (
          <div className="trip-row" key={t.id}>
            <div>
              <h3><Link to={`/trips/${t.id}`}>{t.title}</Link></h3>
              <div className="muted small" style={{ marginTop: 4 }}>
                <span style={{ fontWeight: 600, color: 'var(--forest)' }}>{t.destination_name}</span>
                {' · '}
                {fmtRange(t.start_date, t.end_date)}
                {' · '}
                {t.travelers} traveller{t.travelers > 1 ? 's' : ''}
              </div>
            </div>
            <div className="row">
              <span className="tag">{t.role === 'owner' ? 'Owner' : 'Invited'}</span>
              <Link to={`/trips/${t.id}`} className="btn ghost sm">Open plan</Link>
            </div>
          </div>
        ))}
      </section>
    </div>
  )
}
