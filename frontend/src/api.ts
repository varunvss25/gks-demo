export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function getTopCFR(params: Record<string,string>) {
  const qs = new URLSearchParams(params).toString();
  return fetch(`${API_BASE}/top-cfr?${qs}`).then(r=>r.json());
}
export async function getIssuingOffices(params: Record<string,string>) {
  const qs = new URLSearchParams(params).toString();
  return fetch(`${API_BASE}/issuing-offices?${qs}`).then(r=>r.json());
}
export async function getLetters(params: Record<string,string>) {
  const qs = new URLSearchParams(params).toString();
  return fetch(`${API_BASE}/letters?${qs}`).then(r=>r.json());
}
export async function getLineage() { return fetch(`${API_BASE}/lineage?limit=20`).then(r=>r.json()); }
export async function getTopCFRTrend(params: Record<string,string>) {
  const qs = new URLSearchParams(params).toString();
  return fetch(`${API_BASE}/top-cfr-trend?${qs}`).then(r=>r.json());
}
