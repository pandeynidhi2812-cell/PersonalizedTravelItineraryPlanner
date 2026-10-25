export const inr = (n) => '\u20B9' + Math.round(n || 0).toLocaleString('en-IN')

export const fmtDate = (iso, opts = { day: 'numeric', month: 'short' }) =>
  new Date(iso + 'T00:00:00').toLocaleDateString('en-IN', opts)

export const fmtRange = (a, b) => `${fmtDate(a)} to ${fmtDate(b, { day: 'numeric', month: 'short', year: 'numeric' })}`

export const INTERESTS = ['sightseeing', 'food', 'culture', 'adventure', 'nature', 'relaxation', 'romantic', 'shopping', 'nightlife']

export const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : '')

// Mirrors backend planner.recompute so totals update instantly while editing.
export function recompute(itin, budget, travelers) {
  const breakdown = { stay: 0, food: 0, attractions: 0, transport: 0 }
  const map = { stay: 'stay', meal: 'food', attraction: 'attractions', transport: 'transport' }
  let total = 0
  const days = itin.days.map((d) => {
    const activities = [...d.activities].sort((a, b) => (a.time || '').localeCompare(b.time || ''))
    let day_cost = 0
    activities.forEach((a) => {
      const c = Math.max(0, parseInt(a.cost || 0, 10) || 0)
      day_cost += c
      breakdown[map[a.type] || 'attractions'] += c
    })
    total += day_cost
    return { ...d, activities, day_cost }
  })
  return {
    ...itin, days, breakdown, total_cost: total, budget,
    per_person: Math.round(total / Math.max(1, travelers)),
    budget_status: total <= budget ? 'within' : 'over',
    budget_delta: Math.abs(budget - total),
  }
}
