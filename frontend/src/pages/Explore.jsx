import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api.js'
import { cap, inr } from '../format.js'

export default function Explore() {
  const nav = useNavigate()
  const [dests, setDests] = useState([])
  const [sel, setSel] = useState(null)
  const [detail, setDetail] = useState(null)
  const [error, setError] = useState('')
  const [review, setReview] = useState({ rating: 5, comment: '' })
  const [ok, setOk] = useState('')

  useEffect(() => {
    api.get('/destinations').then((d) => { setDests(d); setSel(d[0]?.id) }).catch((e) => setError(e.message))
  }, [])

  const loadDetail = (id) => api.get(`/destinations/${id}`).then(setDetail).catch((e) => setError(e.message))
  useEffect(() => { if (sel) loadDetail(sel) }, [sel])

  const submitReview = async (e) => {
    e.preventDefault()
    setError(''); setOk('')
    try {
      await api.post('/reviews', { destination_id: sel, rating: Number(review.rating), comment: review.comment })
      setReview({ rating: 5, comment: '' })
      setOk('Thanks, your review was added.')
      loadDetail(sel)
    } catch (err) { setError(err.message) }
  }

  const avg = detail && detail.reviews.length ? (detail.reviews.reduce((s, r) => s + r.rating, 0) / detail.reviews.length).toFixed(1) : null

  return (
    <div className="stack">
      <div className="page-head">
        <div>
          <h1>Explore destinations</h1>
          <p>Browse the places, food, stays and local transport that feed the planner.</p>
        </div>
      </div>
      {error && <div className="alert" role="alert">{error}</div>}

      <div className="chips">
        {dests.map((d) => <button key={d.id} className={`chip ${sel === d.id ? 'on' : ''}`} onClick={() => setSel(d.id)}>{d.name}</button>)}
      </div>

      {detail && (
        <>
          <section className="card">
            <div className="row between wrap">
              <div>
                <div className="small muted">{detail.state} | Best time: {detail.best_season}</div>
                <h2 style={{ fontSize: 28, margin: '4px 0' }}>{detail.name}: {detail.tagline}</h2>
                <p className="muted" style={{ maxWidth: '70ch' }}>{detail.description}</p>
                <div className="row wrap" style={{ marginTop: 10 }}>
                  {(detail.tags || []).map((t) => <span className="tag" key={t}>{t}</span>)}
                  <span className="tag gold">about {inr(detail.avg_daily_budget)} per person per day</span>
                  {avg && <span className="rating">{avg} / 5 from {detail.reviews.length} reviews</span>}
                </div>
              </div>
              <button className="btn accent" onClick={() => nav('/plan', { state: { destination_id: detail.id } })}>Plan a trip here</button>
            </div>
          </section>

          <div className="grid g2">
            <section className="card">
              <h3>Things to do</h3>
              {detail.attractions.map((a) => (
                <div className="list-item" key={a.id}>
                  <div><b>{a.name}</b><div className="small muted">{a.description}</div>
                    <div className="row wrap" style={{ marginTop: 4, gap: 6 }}>{a.tags.map((t) => <span className="tag" key={t}>{t}</span>)}<span className="small muted">{a.area} | {a.duration_min} min | best in the {a.best_slot}</span></div></div>
                  <b className="num">{a.entry_fee ? inr(a.entry_fee) : 'Free'}</b>
                </div>
              ))}
            </section>
            <section className="card">
              <h3>Where to eat</h3>
              {detail.restaurants.map((r) => (
                <div className="list-item" key={r.id}>
                  <div><b>{r.name}</b><div className="small muted">{r.cuisine}. {r.description}</div>
                    <div className="row" style={{ marginTop: 4 }}><span className="tag">{cap(r.tier)}</span><span className="rating small">{r.rating}</span></div></div>
                  <b className="num">{inr(r.cost_per_person)}</b>
                </div>
              ))}
            </section>
            <section className="card">
              <h3>Where to stay</h3>
              {detail.hotels.map((h) => (
                <div className="list-item" key={h.id}>
                  <div><b>{h.name}</b><div className="small muted">{h.amenities.join(', ')}</div>
                    <div className="row" style={{ marginTop: 4 }}><span className="tag">{cap(h.tier)}</span><span className="rating small">{h.rating}</span></div></div>
                  <b className="num">{inr(h.price_per_night)}<div className="small muted" style={{ fontWeight: 400 }}>per night</div></b>
                </div>
              ))}
            </section>
            <section className="card">
              <h3>Getting around</h3>
              {detail.transports.map((t) => (
                <div className="list-item" key={t.id}>
                  <div><b>{t.mode}</b><div className="small muted">{t.notes}</div></div>
                  <b className="num">{inr(t.cost_per_day)}<div className="small muted" style={{ fontWeight: 400 }}>{t.unit === 'per_person' ? 'per person per day' : 'per cab per day'}</div></b>
                </div>
              ))}
            </section>
          </div>

          <section className="card">
            <h3>Traveller reviews</h3>
            {detail.reviews.length === 0 && <p className="muted" style={{ marginTop: 8 }}>No reviews yet. Be the first.</p>}
            {detail.reviews.map((r) => (
              <div className="list-item" key={r.id}>
                <div><b>{r.user_name}</b><div className="small muted">{r.comment}</div></div>
                <span className="rating">{r.rating} / 5</span>
              </div>
            ))}
            <form className="add-row" style={{ gridTemplateColumns: '110px 1fr auto' }} onSubmit={submitReview}>
              <label className="field"><span>Rating</span>
                <select value={review.rating} onChange={(e) => setReview({ ...review, rating: e.target.value })}>
                  {[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{n} / 5</option>)}
                </select>
              </label>
              <label className="field"><span>Your review</span><input value={review.comment} maxLength={500} onChange={(e) => setReview({ ...review, comment: e.target.value })} /></label>
              <button className="btn">Post</button>
            </form>
            {ok && <div className="alert ok" style={{ marginTop: 10 }}>{ok}</div>}
          </section>
        </>
      )}
    </div>
  )
}
