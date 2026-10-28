const API = import.meta.env.VITE_API_URL || '';

function errorMessage(detail, fallback) {
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).filter(Boolean).join(', ') || fallback;
  }
  return fallback;
}

export async function api(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = new Headers(options.headers || {});
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) headers.set('Authorization', `Bearer ${token}`);

  let response;
  try {
    response = await fetch(`${API}${path}`, { ...options, headers });
  } catch (error) {
    if (options.signal?.aborted) throw error;
    throw new Error('Impossible de joindre le serveur. Vérifie qu’il est démarré.');
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    if (response.status === 401 && !path.startsWith('/api/auth/')) {
      localStorage.removeItem('token');
      window.dispatchEvent(new Event('auth:expired'));
    }
    throw new Error(errorMessage(body.detail, `Erreur HTTP ${response.status}`));
  }
  if (response.status === 204) return null;
  return response.json();
}
