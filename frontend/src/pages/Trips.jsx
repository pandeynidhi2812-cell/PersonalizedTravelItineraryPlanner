import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import { cap, fmtRange, inr } from '../format.js'

export default function Trips() {
  const [trips, setTrips] = useState(null)
  const [filter, setFilter] = useState('all')
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/trips').then(setTrips).catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="alert">{error}</div>
  if (!trips) return <div className="muted">Loading your Tripora itineraries...</div>
  const shown = trips.filter((t) => filter === 'all' || (filter === 'mine' ? t.role === 'owner' : t.role !== 'owner'))

  return (
    <div className="stack">
      <div className="page-head">
        <div>
          <div className="small muted" style={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--forest)' }}>
            My Collection
          </div>
          <h1 style={{ marginTop: 2 }}>Curated Journeys</h1>
          <p>Browse all itineraries you've designed or have been invited to collaborate on.</p>
        </div>
        <div className="seg" role="tablist">
          {[['all', 'All Trips'], ['mine', 'Owned'], ['shared', 'Shared with me']].map(([k, label]) => (
            <button key={k} className={filter === k ? 'on' : ''} onClick={() => setFilter(k)}>{label}</button>
          ))}
        </div>
      </div>

      {shown.length === 0 && (
        <div className="card" style={{ textAlign: 'center', padding: '48px 24px' }}>
          <p className="muted" style={{ fontSize: 16 }}>No itineraries found in this filter.</p>
          <Link className="btn" style={{ marginTop: 16 }} to="/plan">Plan a new trip</Link>
        </div>
      )}

      <div className="grid g3">
        {shown.map((t) => (
          <Link key={t.id} to={`/trips/${t.id}`} className="card trip-card" style={{ color: 'inherit', textDecoration: 'none' }}>
            <div className="row between">
              <div className="dest">{t.destination_name}, {t.destination_state}</div>
              <span className="tag" style={{ fontSize: 11 }}>{t.role === 'owner' ? 'Owner' : 'Co-Editor'}</span>
            </div>
            <h3 style={{ fontSize: 19, letterSpacing: '-0.01em' }}>{t.title}</h3>
            <div className="muted small">{fmtRange(t.start_date, t.end_date)}</div>
            <div className="row wrap" style={{ gap: 6, marginTop: 4 }}>
              <span className="tag">{t.days} days</span>
              <span className="tag">{t.travelers} traveller{t.travelers > 1 ? 's' : ''}</span>
              <span className="tag">{cap(t.pace)}</span>
              {t.role !== 'owner' && <span className="tag gold">Shared by {t.owner_name.split(' ')[0]}</span>}
            </div>
            <div className="row between" style={{ marginTop: 'auto', paddingTop: 12, borderTop: '1px solid var(--line)' }}>
              <div className="cost">{inr(t.total_cost || t.budget)}</div>
              <span className="small muted" style={{ fontWeight: 600, color: 'var(--forest)' }}>View itinerary →</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
