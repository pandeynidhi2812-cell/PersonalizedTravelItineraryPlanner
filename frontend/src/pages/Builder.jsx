import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { api } from '../api.js'
import { INTERESTS, cap, inr } from '../format.js'

const iso = (d) => d.toISOString().slice(0, 10)
const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x }

export default function Builder() {
  const nav = useNavigate()
  const { state } = useLocation()
  const preset = state?.preset
  const [dests, setDests] = useState([])
  const start = addDays(new Date(), 14)
  const [f, setF] = useState({
    title: preset?.title || '',
    destination_id: state?.destination_id || null,
    start_date: iso(start),
    end_date: iso(addDays(start, (preset?.days || 3) - 1)),
    travelers: preset?.travelers || 2,
    budget: preset?.budget || 30000,
    style: preset?.style || 'mid',
    pace: preset?.pace || 'balanced',
    interests: preset?.interests || ['sightseeing', 'food'],
  })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/destinations').then((d) => {
      setDests(d)
      setF((cur) => (cur.destination_id ? cur : { ...cur, destination_id: d[0]?.id || null }))
    }).catch((e) => setError(e.message))
  }, [])

  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })
  const toggle = (i) => setF({ ...f, interests: f.interests.includes(i) ? f.interests.filter((x) => x !== i) : [...f.interests, i] })
  const days = Math.max(0, Math.round((new Date(f.end_date) - new Date(f.start_date)) / 86400000) + 1)
  const dest = dests.find((d) => d.id === f.destination_id)
  const hint = dest ? dest.avg_daily_budget * days * f.travelers : 0

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      const trip = await api.post('/trips', {
        ...f,
        destination_id: Number(f.destination_id),
        travelers: Number(f.travelers),
        budget: Number(f.budget),
      })
      nav(`/trips/${trip.id}`)
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <form className="stack" onSubmit={submit}>
      <div className="page-head">
        <div>
          <div className="small muted" style={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--forest)' }}>
            Itinerary Studio
          </div>
          <h1>Craft your journey</h1>
          <p>Configure your destination and preferences. Tripora algorithmically builds an optimized day-by-day plan with attractions, stays, food, and local transit.</p>
        </div>
      </div>

      <section className="card stack">
        <div className="row between">
          <div>
            <h2>1. Where are you heading?</h2>
            <p className="small muted">Select one of our curated Indian destinations</p>
          </div>
          {dest && <span className="tag good">{dest.state}</span>}
        </div>
        <div className="dest-pick">
          {dests.map((d) => (
            <button
              type="button"
              key={d.id}
              className={f.destination_id === d.id ? 'on' : ''}
              onClick={() => setF({ ...f, destination_id: d.id })}
            >
              <b>{d.name}</b>
              <small>{d.state}</small>
              <div className="small muted" style={{ marginTop: 6, fontSize: 11.5 }}>
                ~{inr(d.avg_daily_budget)} / day / person
              </div>
            </button>
          ))}
        </div>
      </section>

      <section className="card">
        <div style={{ marginBottom: 16 }}>
          <h2>2. Dates and travellers</h2>
          <p className="small muted">Tripora clusters each day by geographic area to prevent excessive transit.</p>
        </div>
        <div className="grid g4">
          <label className="field">
            <span>Trip title</span>
            <input value={f.title} onChange={set('title')} placeholder="e.g. Summer in Manali" maxLength={120} />
          </label>
          <label className="field">
            <span>Start date</span>
            <input type="date" required value={f.start_date} onChange={set('start_date')} />
          </label>
          <label className="field">
            <span>End date</span>
            <input type="date" required min={f.start_date} value={f.end_date} onChange={set('end_date')} />
          </label>
          <label className="field">
            <span>Number of travellers</span>
            <input type="number" min={1} max={20} required value={f.travelers} onChange={set('travelers')} />
          </label>
        </div>
        <p className="small muted" style={{ marginTop: 12, fontWeight: 500 }}>
          Journey span: <b style={{ color: 'var(--charcoal)' }}>{days} day{days === 1 ? '' : 's'}</b>
          {days > 14 && <span style={{ color: 'var(--coral)', marginLeft: 8 }}>(maximum supported is 14 days)</span>}
        </p>
      </section>

      <section className="card stack">
        <div>
          <h2>3. Budget, stay tier & pace</h2>
          <p className="small muted">Realistic budgeting calibrated against verified hotel tiers and transport rates.</p>
        </div>
        <div className="grid g3">
          <label className="field">
            <span>Total trip budget (INR)</span>
            <input type="number" min={500} step={500} required value={f.budget} onChange={set('budget')} />
            {hint > 0 && (
              <small className="muted" style={{ display: 'block', marginTop: 4 }}>
                Estimated benchmark for this duration: <b>{inr(hint)}</b>
              </small>
            )}
          </label>
          <div>
            <div className="field"><span style={{ display: 'block', marginBottom: 6 }}>Stay tier</span></div>
            <div className="seg">
              {['budget', 'mid', 'premium'].map((s) => (
                <button type="button" key={s} className={f.style === s ? 'on' : ''} onClick={() => setF({ ...f, style: s })}>
                  {cap(s)}
                </button>
              ))}
            </div>
          </div>
          <div>
            <div className="field"><span style={{ display: 'block', marginBottom: 6 }}>Daily pace</span></div>
            <div className="seg">
              {['relaxed', 'balanced', 'packed'].map((s) => (
                <button type="button" key={s} className={f.pace === s ? 'on' : ''} onClick={() => setF({ ...f, pace: s })}>
                  {cap(s)}
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="small muted" style={{ background: 'var(--cream)', padding: '10px 14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--line)' }}>
          💡 <b>Budget Guarantee:</b> If your chosen plan exceeds your budget, Tripora automatically steps down accommodation and dining tiers to keep you on budget.
        </div>
      </section>

      <section className="card stack">
        <div>
          <h2>4. What interests you?</h2>
          <p className="small muted">Attractions matching your interests are weighted and scheduled at their optimal time of day.</p>
        </div>
        <div className="chips">
          {INTERESTS.map((i) => (
            <button
              type="button"
              key={i}
              className={`chip ${f.interests.includes(i) ? 'on' : ''}`}
              aria-pressed={f.interests.includes(i)}
              onClick={() => toggle(i)}
            >
              {cap(i)}
            </button>
          ))}
        </div>
      </section>

      {error && <div className="alert" role="alert">{error}</div>}

      <div className="row" style={{ paddingTop: 8 }}>
        <button
          className="btn"
          disabled={busy || !f.destination_id || days < 1 || days > 14}
          style={{ padding: '12px 28px', fontSize: 16 }}
        >
          {busy ? 'Building your itinerary...' : '✨ Generate itinerary'}
        </button>
      </div>
    </form>
  )
}
