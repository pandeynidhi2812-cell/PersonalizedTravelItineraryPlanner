const envBase = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '')
const BASE = envBase ? (envBase.endsWith('/api') ? envBase : `${envBase}/api`) : '/api'

export const getToken = () => localStorage.getItem('token')
export const setToken = (t) => (t ? localStorage.setItem('token', t) : localStorage.removeItem('token'))

async function request(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (getToken()) headers.Authorization = `Bearer ${getToken()}`
  let res
  try {
    res = await fetch(BASE + path, { method, headers, body: body ? JSON.stringify(body) : undefined })
  } catch {
    throw new Error('Cannot reach the server. Is the backend running on port 8000?')
  }
  let data = null
  try { data = await res.json() } catch { /* empty body */ }
  if (res.status === 401 && !path.startsWith('/auth/login')) {
    setToken(null)
    window.dispatchEvent(new Event('auth-expired'))
  }
  if (!res.ok) {
    const d = data && data.detail
    const msg = typeof d === 'string' ? d : Array.isArray(d) ? d.map((x) => x.msg).join(', ') : 'Something went wrong'
    throw new Error(msg)
  }
  return data
}

export const api = {
  get: (p) => request(p),
  post: (p, body) => request(p, { method: 'POST', body: body || {} }),
  put: (p, body) => request(p, { method: 'PUT', body }),
  del: (p) => request(p, { method: 'DELETE' }),
}
