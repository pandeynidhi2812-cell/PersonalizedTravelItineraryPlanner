import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api.js'
import { useAuth } from '../auth.jsx'
import { fmtRange, inr } from '../format.js'

const PRESETS = [
  {
    key: 'solo', title: 'Solo weekend getaway', blurb: 'Two or three easy days, street food and the sights worth your time.',
    meta: '1 traveller, 3 days, budget stay',
    values: { title: 'Weekend getaway', travelers: 1, budget: 10000, style: 'budget', pace: 'relaxed', interests: ['food', 'sightseeing'], days: 3 },
  },
  {
    key: 'couple', title: 'Couple escape', blurb: 'Unhurried days, scenic spots and a premium stay.',
    meta: '2 travellers, 4 days, premium stay',
    values: { title: 'Romantic escape', travelers: 2, budget: 85000, style: 'premium', pace: 'relaxed', interests: ['romantic', 'relaxation', 'sightseeing'], days: 4 },
  },
  {
    key: 'group', title: 'Friends group trip', blurb: 'A packed multi-day plan with shared costs and fewer clashes.',
    meta: '5 travellers, 5 days, mid-range stay',
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
  if (!data) return <div className="muted">Loading your dashboard...</div>
  const { stats, next_trip: next, recent } = data

  return (
    <div className="stack" style={{ '--gap': '28px' }}>
      <div className="page-head">
        <div>
          <h1>Hello, {user.name.split(' ')[0]}</h1>
          <p>{next ? `Your next trip is ${next.title}, ${fmtRange(next.start_date, next.end_date)}.` : 'You have no upcoming trips yet. Start one below.'}</p>
        </div>
        <Link className="btn accent" to="/plan">Plan a new trip</Link>
      </div>

      <div className="grid g4">
        <div className="stat"><b>{stats.total_trips}</b><span>Trips in your account</span></div>
        <div className="stat"><b>{stats.upcoming_trips}</b><span>Upcoming</span></div>
        <div className="stat"><b>{inr(stats.estimated_spend)}</b><span>Estimated spend, all trips</span></div>
        <div className="stat"><b>{stats.shared_trips}</b><span>Shared with you</span></div>
      </div>

      <section>
        <h2 style={{ margin: '12px 0 12px' }}>Start from a common scenario</h2>
        <div className="presets">
          {PRESETS.map((p) => (
            <button key={p.key} className="preset" onClick={() => nav('/plan', { state: { preset: p.values } })}>
              <h3>{p.title}</h3>
              <p>{p.blurb}</p>
              <div className="meta">{p.meta}</div>
            </button>
          ))}
        </div>
      </section>

      <section className="card">
        <div className="row between">
          <h2>Recently updated</h2>
          <Link to="/trips" className="small">See all trips</Link>
        </div>
        {recent.length === 0 && <p className="muted" style={{ marginTop: 12 }}>Nothing here yet.</p>}
        {recent.map((t) => (
          <div className="trip-row" key={t.id}>
            <div>
              <h3><Link to={`/trips/${t.id}`}>{t.title}</Link></h3>
              <div className="muted small">{t.destination_name} | {fmtRange(t.start_date, t.end_date)} | {t.travelers} traveller{t.travelers > 1 ? 's' : ''}</div>
            </div>
            <div className="row">
              <span className={`tag ${t.budget_status === 'over' ? 'bad' : 'good'}`}>{t.budget_status === 'over' ? 'Over budget' : 'Within budget'}</span>
              <b className="num">{inr(t.total_cost)}</b>
            </div>
          </div>
        ))}
      </section>
    </div>
  )
}
