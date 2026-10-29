const API_BASE = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001').replace(/\/+$/, '')

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`)
  if (!res.ok) {
    throw new Error(`Health check failed (HTTP ${res.status})`)
  }
  return res.json()
}

export async function ask(query, conversationId) {
  const t0 = performance.now()
  const res = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      conversation_id: conversationId,
    }),
  })
  const latencyMs = Math.round(performance.now() - t0)
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const errBody = await res.json()
      if (errBody?.detail) {
        detail = typeof errBody.detail === 'string' ? errBody.detail : JSON.stringify(errBody.detail)
      }
    } catch {
      // ignore parse errors
    }
    throw new Error(detail)
  }
  const data = await res.json()
  return { ...data, latencyMs }
}

export async function addDocument({ docId, title, text }) {
  const res = await fetch(`${API_BASE}/add-document`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      doc_id: docId,
      title,
      text,
    }),
  })
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const errBody = await res.json()
      if (errBody?.detail) {
        detail = typeof errBody.detail === 'string' ? errBody.detail : JSON.stringify(errBody.detail)
      }
    } catch {
      // ignore parse errors
    }
    throw new Error(detail)
  }
  return res.json()
}
