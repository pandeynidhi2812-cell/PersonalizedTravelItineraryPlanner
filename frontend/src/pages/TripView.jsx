import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api.js'
import { INTERESTS, cap, fmtDate, fmtRange, inr, recompute } from '../format.js'

const COLORS = { stay: '#202824', food: '#c88d2a', attractions: '#245c48', transport: '#727a74' }
const LABELS = { stay: 'Stay', food: 'Food', attractions: 'Activities', transport: 'Transport' }
const TYPE_LABEL = { attraction: 'Activity', meal: 'Meal', transport: 'Transport', stay: 'Stay', free: 'Free time', custom: 'Custom' }

export default function TripView() {
  const { id } = useParams()
  const nav = useNavigate()
  const [trip, setTrip] = useState(null)
  const [itin, setItin] = useState(null)
  const [dirty, setDirty] = useState(false)
  const [day, setDay] = useState(1)
  const [editing, setEditing] = useState(null)
  const [busy, setBusy] = useState('')
  const [msg, setMsg] = useState(null)
  const [draft, setDraft] = useState({ time: '12:00', title: '', cost: 0 })
  const [member, setMember] = useState({ email: '', interests: [] })

  const load = (t) => { setTrip(t); setItin(t.itinerary); setDirty(false) }

  useEffect(() => {
    api.get(`/trips/${id}`).then(load).catch((e) => setMsg({ bad: true, text: e.message }))
  }, [id])

  const flash = (text, bad = false) => { setMsg({ text, bad }); window.scrollTo({ top: 0, behavior: 'smooth' }) }

  const edit = (fn) => {
    setItin((cur) => recompute(fn(cur), trip.budget, trip.travelers))
    setDirty(true)
  }

  const run = async (label, fn, okText) => {
    setBusy(label)
    setMsg(null)
    try {
      const t = await fn()
      if (t) load(t)
      if (okText) flash(okText)
    } catch (e) {
      flash(e.message, true)
    } finally {
      setBusy('')
    }
  }

  const save = () => run('save', () => api.put(`/trips/${id}`, { itinerary: itin }), 'Changes saved.')
  const saveFirst = async () => { if (dirty) await api.put(`/trips/${id}`, { itinerary: itin }) }

  const regenDay = (n) =>
    run('day' + n, async () => { await saveFirst(); return api.post(`/trips/${id}/days/${n}/regenerate`) }, `Day ${n} regenerated.`)
  const regenAll = () => {
    if (dirty && !window.confirm('Regenerating replaces your unsaved and saved edits. Continue?')) return
    run('all', () => api.post(`/trips/${id}/regenerate`), 'A fresh itinerary was generated.')
  }
  const remove = async () => {
    if (!window.confirm('Delete this trip permanently?')) return
    try { await api.del(`/trips/${id}`); nav('/trips') } catch (e) { flash(e.message, true) }
  }
  const addMember = (e) => {
    e.preventDefault()
    run('member', () => api.post(`/trips/${id}/members`, member), 'Traveller added. Regenerate to blend their interests into the plan.')
      .then(() => setMember({ email: '', interests: [] }))
  }
  const removeMember = (uid) => run('member', () => api.del(`/trips/${id}/members/${uid}`))

  const total = itin?.total_cost || 0
  const pct = useMemo(() => (trip ? Math.min(100, Math.round((total / Math.max(1, trip.budget)) * 100)) : 0), [total, trip])

  if (!trip) return msg ? <div className="alert">{msg.text}</div> : <div className="muted">Loading trip...</div>
  const over = itin.budget_status === 'over'
  const owner = trip.role === 'owner'

  const updateAct = (aid, patch) =>
    edit((cur) => ({ ...cur, days: cur.days.map((d) => d.day !== day ? d : { ...d, activities: d.activities.map((a) => a.id === aid ? { ...a, ...patch } : a) }) }))
  const removeAct = (aid) =>
    edit((cur) => ({ ...cur, days: cur.days.map((d) => d.day !== day ? d : { ...d, activities: d.activities.filter((a) => a.id !== aid) }) }))
  const addAct = (e) => {
    e.preventDefault()
    if (!draft.title.trim()) return
    const a = { id: Math.random().toString(16).slice(2, 10), time: draft.time, type: 'custom', title: draft.title.trim(), description: 'Added by you', cost: Number(draft.cost) || 0, duration_min: 60, location: '' }
    edit((cur) => ({ ...cur, days: cur.days.map((d) => d.day !== day ? d : { ...d, activities: [...d.activities, a] }) }))
    setDraft({ time: '12:00', title: '', cost: 0 })
  }

  return (
    <div className="stack">
      <div className="no-print">
        <Link to="/trips" className="small" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontWeight: 600 }}>
          ← Back to my trips
        </Link>
      </div>

      {msg && <div className={`alert ${msg.bad ? '' : 'ok'}`} role="status">{msg.text}</div>}

      <section className="hero">
        <div>
          <div className="row wrap" style={{ marginBottom: 12 }}>
            <span className="tag gold" style={{ background: 'var(--amber)', color: '#ffffff', fontWeight: 700 }}>
              {trip.destination_name}, {trip.destination_state}
            </span>
            {!owner && <span className="tag" style={{ background: 'rgba(255,255,255,0.15)', color: '#ffffff' }}>Shared by {trip.owner_name}</span>}
          </div>
          <h1>{trip.title}</h1>
          <p className="sub">
            {fmtRange(trip.start_date, trip.end_date)} · {trip.days} days · {trip.travelers} traveller{trip.travelers > 1 ? 's' : ''} · {cap(trip.pace)} pace
          </p>
          <div className={`meter ${over ? 'over' : ''}`} role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label="Budget used">
            <i style={{ width: `${pct}%` }} />
          </div>
          <p className="sub small" style={{ marginTop: 8 }}>
            {over ? `${inr(itin.budget_delta)} over your ${inr(trip.budget)} budget` : `${inr(itin.budget_delta)} remaining of your ${inr(trip.budget)} budget`}
            {' · '}{inr(itin.per_person)} per person
          </p>
        </div>
        <div className="cost-big num">
          {inr(total)}
          <small>estimated total</small>
        </div>
      </section>

      <div className="grid g2">
        <section className="card">
          <h3 style={{ marginBottom: 8, color: 'var(--charcoal)' }}>Journey Overview</h3>
          <p style={{ lineHeight: 1.6, color: 'var(--text)' }}>{itin.overview}</p>
          {itin.applied_style !== itin.requested_style && (
            <p className="small" style={{ marginTop: 12 }}>
              <span className="tag gold" style={{ marginRight: 6 }}>Auto-adjusted</span>
              Stay and dining were stepped down to {itin.applied_style} to honor your budget.
            </p>
          )}
          <div className="small muted" style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid var(--line)' }}>
            Staying at <b style={{ color: 'var(--charcoal)' }}>{itin.hotel.name}</b> ({itin.hotel.tier}, {inr(itin.hotel.price_per_night)} / night) · Transit: {itin.transport.mode}
          </div>
        </section>

        <section className="card">
          <h3 style={{ marginBottom: 12, color: 'var(--charcoal)' }}>Where the budget goes</h3>
          <div className="split" aria-hidden="true">
            {Object.keys(COLORS).map((k) => (
              <i key={k} style={{ width: `${total ? (itin.breakdown[k] / total) * 100 : 0}%`, background: COLORS[k] }} />
            ))}
          </div>
          <div className="legend">
            {Object.keys(COLORS).map((k) => (
              <span key={k}>
                <em style={{ background: COLORS[k] }} />
                {LABELS[k]} <b className="num">{inr(itin.breakdown[k])}</b>
              </span>
            ))}
          </div>
        </section>
      </div>

      <div className="row between wrap no-print" style={{ marginTop: 8 }}>
        <div className="tabs" role="tablist" style={{ maxWidth: '100%' }}>
          {itin.days.map((d) => (
            <button
              key={d.day}
              role="tab"
              aria-selected={day === d.day}
              className={`tab ${day === d.day ? 'on' : ''}`}
              onClick={() => { setDay(d.day); setEditing(null) }}
            >
              <b>Day {d.day}</b>
              <small>{fmtDate(d.date)}</small>
            </button>
          ))}
        </div>
        <div className="row wrap">
          <button className="btn ghost sm" onClick={() => window.print()}>
            🖨️ Print
          </button>
          <button className="btn ghost sm" disabled={!!busy} onClick={regenAll}>
            {busy === 'all' ? 'Regenerating...' : '🔄 Regenerate all'}
          </button>
          {owner && (
            <button className="btn warn sm" onClick={remove}>
              Delete trip
            </button>
          )}
        </div>
      </div>

      {itin.days.map((d) => (
        <section key={d.day} className={`card day-block ${d.day === day ? 'active' : ''}`}>
          <div className="row between wrap" style={{ marginBottom: 8, paddingBottom: 14, borderBottom: '1px solid var(--line)' }}>
            <div>
              <h2>Day {d.day}: {d.theme}</h2>
              <div className="muted small" style={{ marginTop: 2 }}>
                {fmtDate(d.date, { weekday: 'long', day: 'numeric', month: 'long' })} · <b style={{ color: 'var(--forest)' }}>{inr(d.day_cost)}</b> daily cost
              </div>
            </div>
            <button className="btn ghost sm no-print" disabled={!!busy} onClick={() => regenDay(d.day)}>
              {busy === 'day' + d.day ? 'Refreshing...' : '🔄 Regenerate this day'}
            </button>
          </div>

          <ul className="timeline">
            {d.activities.map((a) => (
              <li key={a.id} className={`tl ${a.type}`}>
                <div className="time">{a.time}</div>
                <div className="dot" />
                <div className="body">
                  {editing === a.id && d.day === day ? (
                    <div>
                      <div className="edit-row">
                        <input type="time" aria-label="Time" value={a.time} onChange={(e) => updateAct(a.id, { time: e.target.value })} />
                        <input aria-label="Title" value={a.title} maxLength={120} onChange={(e) => updateAct(a.id, { title: e.target.value })} />
                        <input type="number" min={0} aria-label="Cost" value={a.cost} onChange={(e) => updateAct(a.id, { cost: e.target.value })} />
                      </div>
                      <div className="acts">
                        <button className="btn sm" onClick={() => setEditing(null)}>Done</button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="top">
                        <div>
                          <div className="title">{a.title}</div>
                          <div className="desc">{a.description}</div>
                          <div className="row" style={{ marginTop: 6, gap: 8 }}>
                            <span className="tag">{TYPE_LABEL[a.type] || 'Activity'}</span>
                            {a.location && <span className="small muted">{a.location}</span>}
                            {a.duration_min > 0 && <span className="small muted">{a.duration_min} min</span>}
                          </div>
                        </div>
                        <div className="price">{a.cost ? inr(a.cost) : 'Included'}</div>
                      </div>
                      <div className="acts no-print">
                        <button className="btn ghost sm" onClick={() => setEditing(a.id)}>Edit</button>
                        <button className="btn warn sm" onClick={() => removeAct(a.id)}>Remove</button>
                      </div>
                    </>
                  )}
                </div>
              </li>
            ))}
          </ul>

          <form className="add-row no-print" onSubmit={addAct}>
            <label className="field">
              <span>Time</span>
              <input type="time" value={draft.time} onChange={(e) => setDraft({ ...draft, time: e.target.value })} />
            </label>
            <label className="field">
              <span>Custom activity</span>
              <input value={draft.title} maxLength={120} placeholder="e.g. Sunset drinks by the cliff" onChange={(e) => setDraft({ ...draft, title: e.target.value })} />
            </label>
            <label className="field">
              <span>Cost (INR)</span>
              <input type="number" min={0} value={draft.cost} onChange={(e) => setDraft({ ...draft, cost: e.target.value })} />
            </label>
            <button className="btn ghost">Add activity</button>
          </form>
        </section>
      ))}

      <div className="grid g2">
        <section className="card">
          <h3 style={{ marginBottom: 10 }}>Local Travel Tips</h3>
          <ul className="tips">
            {itin.tips.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </section>

        <section className="card no-print">
          <h3 style={{ marginBottom: 10 }}>Co-Planners</h3>
          <div className="member">
            <div>
              <b>{trip.owner_name}</b>
              <div className="small muted">{trip.owner_email}</div>
            </div>
            <span className="tag good">Owner</span>
          </div>
          {trip.members.map((m) => (
            <div className="member" key={m.id}>
              <div>
                <b>{m.name}</b>
                <div className="small muted">{m.interests.length ? m.interests.join(', ') : 'No interests specified'}</div>
              </div>
              {owner ? (
                <button className="btn ghost sm" onClick={() => removeMember(m.id)}>Remove</button>
              ) : (
                <span className="tag">Co-Editor</span>
              )}
            </div>
          ))}
          {owner ? (
            <form onSubmit={addMember} className="stack" style={{ marginTop: 16 }}>
              <label className="field">
                <span>Invite co-planner by email</span>
                <input
                  type="email"
                  required
                  value={member.email}
                  onChange={(e) => setMember({ ...member, email: e.target.value })}
                  placeholder="collaborator@example.com"
                />
              </label>
              <div>
                <div className="small muted" style={{ marginBottom: 6 }}>Their travel interests (blended on next regeneration):</div>
                <div className="chips">
                  {INTERESTS.map((i) => (
                    <button
                      type="button"
                      key={i}
                      className={`chip ${member.interests.includes(i) ? 'on' : ''}`}
                      onClick={() =>
                        setMember({
                          ...member,
                          interests: member.interests.includes(i) ? member.interests.filter((x) => x !== i) : [...member.interests, i],
                        })
                      }
                    >
                      {cap(i)}
                    </button>
                  ))}
                </div>
              </div>
              <button className="btn" disabled={busy === 'member'}>
                Add co-planner
              </button>
            </form>
          ) : (
            <p className="small muted" style={{ marginTop: 12 }}>
              You are invited as an editor. You can edit activities and save changes. Only the trip owner can add/remove collaborators.
            </p>
          )}
        </section>
      </div>

      {dirty && (
        <div className="savebar no-print" role="status">
          <span style={{ fontWeight: 600 }}>⚠️ You have unsaved changes to this itinerary</span>
          <div className="row">
            <button className="btn ghost sm" style={{ color: '#ffffff', borderColor: 'rgba(255, 255, 255, 0.25)' }} onClick={() => load(trip)}>
              Discard
            </button>
            <button className="btn accent sm" disabled={busy === 'save'} onClick={save}>
              {busy === 'save' ? 'Saving...' : 'Save changes'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
