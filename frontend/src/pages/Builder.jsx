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
          <h1>Plan a trip</h1>
          <p>Pick a destination and your preferences. The plan is generated in a moment and you can edit any part of it.</p>
        </div>
      </div>

      <section className="card stack">
        <h2>Where to?</h2>
        <div className="dest-pick">
          {dests.map((d) => (
            <button type="button" key={d.id} className={f.destination_id === d.id ? 'on' : ''} onClick={() => setF({ ...f, destination_id: d.id })}>
              <b>{d.name}</b>
              <small>{d.state}</small>
              <div className="small muted" style={{ marginTop: 6 }}>about {inr(d.avg_daily_budget)} per person per day</div>
            </button>
          ))}
        </div>
      </section>

      <section className="card">
        <h2 style={{ marginBottom: 16 }}>When and who</h2>
        <div className="grid g4">
          <label className="field"><span>Trip name</span><input value={f.title} onChange={set('title')} placeholder="Optional" maxLength={120} /></label>
          <label className="field"><span>Start date</span><input type="date" required value={f.start_date} onChange={set('start_date')} /></label>
          <label className="field"><span>End date</span><input type="date" required min={f.start_date} value={f.end_date} onChange={set('end_date')} /></label>
          <label className="field"><span>Travellers</span><input type="number" min={1} max={20} required value={f.travelers} onChange={set('travelers')} /></label>
        </div>
        <p className="small muted" style={{ marginTop: 10 }}>{days} day{days === 1 ? '' : 's'}{days > 14 ? ' (maximum is 14)' : ''}</p>
      </section>

      <section className="card stack">
        <h2>Budget and style</h2>
        <div className="grid g3">
          <label className="field">
            <span>Total budget (INR)</span>
            <input type="number" min={500} step={500} required value={f.budget} onChange={set('budget')} />
            {hint > 0 && <small className="muted">A typical trip like this costs around {inr(hint)}.</small>}
          </label>
          <div>
            <div className="field"><span style={{ display: 'block', marginBottom: 6 }}>Stay and dining</span></div>
            <div className="seg">
              {['budget', 'mid', 'premium'].map((s) => (
                <button type="button" key={s} className={f.style === s ? 'on' : ''} onClick={() => setF({ ...f, style: s })}>{cap(s)}</button>
              ))}
            </div>
          </div>
          <div>
            <div className="field"><span style={{ display: 'block', marginBottom: 6 }}>Pace</span></div>
            <div className="seg">
              {['relaxed', 'balanced', 'packed'].map((s) => (
                <button type="button" key={s} className={f.pace === s ? 'on' : ''} onClick={() => setF({ ...f, pace: s })}>{cap(s)}</button>
              ))}
            </div>
          </div>
        </div>
        <p className="small muted">If the plan costs more than your budget, Wayfare steps the stay and dining down a tier automatically and tells you what changed.</p>
      </section>

      <section className="card stack">
        <h2>What do you enjoy?</h2>
        <div className="chips">
          {INTERESTS.map((i) => (
            <button type="button" key={i} className={`chip ${f.interests.includes(i) ? 'on' : ''}`} aria-pressed={f.interests.includes(i)} onClick={() => toggle(i)}>
              {cap(i)}
            </button>
          ))}
        </div>
      </section>

      {error && <div className="alert" role="alert">{error}</div>}
      <div className="row">
        <button className="btn accent" disabled={busy || !f.destination_id || days < 1 || days > 14}>
          {busy ? 'Building your itinerary...' : 'Generate itinerary'}
        </button>
      </div>
    </form>
  )
}
