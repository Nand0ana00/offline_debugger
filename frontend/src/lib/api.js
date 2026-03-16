// Note: In same-origin environments or when credentials are included, 
// browser/webview handles cookies automatically.

function _handle401(response) {
  if (response.status === 401) {
    window.dispatchEvent(new Event('auth_expired'))
  }
}

function _formatErrorMessage(detail) {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map(err => {
      const field = err.loc ? err.loc[err.loc.length - 1] : ''
      return field ? `${field}: ${err.msg}` : err.msg
    }).join(', ')
  }
  if (detail && typeof detail === 'object') {
    return JSON.stringify(detail)
  }
  return 'Unknown error'
}

export async function fetchJson(url, options = {}) {
  const headers = { ...(options.headers || {}) }
  const response = await fetch(url, { ...options, headers, credentials: 'include' })
  let payload = {}
  try {
    payload = await response.json()
  } catch {
    payload = {}
  }

  _handle401(response)

  if (!response.ok) {
    const message = _formatErrorMessage(payload?.detail) || `Request failed (${response.status})`
    throw new Error(message)
  }

  return payload
}

export async function fetchJsonWithMeta(url, options = {}) {
  const start = performance.now()
  const headers = { ...(options.headers || {}) }
  const response = await fetch(url, { ...options, headers, credentials: 'include' })
  let payload = {}
  try {
    payload = await response.json()
  } catch {
    payload = {}
  }

  const durationMs = Math.round(performance.now() - start)

  _handle401(response)

  if (!response.ok) {
    const message = _formatErrorMessage(payload?.detail) || `Request failed (${response.status})`
    throw new Error(message)
  }

  return { payload, response, durationMs }
}
