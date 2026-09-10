const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export async function api(path, options={}) {
  const token = localStorage.getItem('token');
  const headers = {'Content-Type':'application/json', ...(options.headers||{})};
  if(token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, {...options, headers});
  if(!res.ok){ const body=await res.json().catch(()=>({})); throw new Error(body.detail || `Erreur HTTP ${res.status}`); }
  return res.status===204 ? null : res.json();
}
