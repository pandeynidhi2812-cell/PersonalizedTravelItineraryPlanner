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
  if (!trips) return <div className="muted">Loading trips...</div>
  const shown = trips.filter((t) => filter === 'all' || (filter === 'mine' ? t.role === 'owner' : t.role !== 'owner'))

  return (
    <div className="stack">
      <div className="page-head">
        <div>
          <h1>My trips</h1>
          <p>Everything you own or have been invited to edit.</p>
        </div>
        <div className="seg" role="tablist">
          {[['all', 'All'], ['mine', 'Owned'], ['shared', 'Shared']].map(([k, label]) => (
            <button key={k} className={filter === k ? 'on' : ''} onClick={() => setFilter(k)}>{label}</button>
          ))}
        </div>
      </div>

      {shown.length === 0 && (
        <div className="card">
          <p className="muted">No trips here yet.</p>
          <Link className="btn" style={{ marginTop: 12 }} to="/plan">Plan one</Link>
        </div>
      )}

      <div className="grid g3">
        {shown.map((t) => (
          <Link key={t.id} to={`/trips/${t.id}`} className="card trip-card" style={{ color: 'inherit', textDecoration: 'none' }}>
            <div className="dest">{t.destination_name}, {t.destination_state}</div>
            <h3 style={{ fontSize: 19 }}>{t.title}</h3>
            <div className="muted small">{fmtRange(t.start_date, t.end_date)}</div>
            <div className="row wrap">
              <span className="tag">{t.days} days</span>
              <span className="tag">{t.travelers} traveller{t.travelers > 1 ? 's' : ''}</span>
              <span className="tag">{cap(t.pace)}</span>
              {t.role !== 'owner' && <span className="tag gold">Shared by {t.owner_name.split(' ')[0]}</span>}
            </div>
            <div className="row between" style={{ marginTop: 'auto', paddingTop: 8 }}>
              <span className="cost num">{inr(t.total_cost)}</span>
              <span className={`tag ${t.budget_status === 'over' ? 'bad' : 'good'}`}>{t.budget_status === 'over' ? 'Over budget' : 'Within budget'}</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
