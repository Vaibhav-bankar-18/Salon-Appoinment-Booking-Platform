const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export const getTokens = () => JSON.parse(localStorage.getItem("tokens") || "null");
export const setTokens = (t) =>
  t ? localStorage.setItem("tokens", JSON.stringify(t)) : localStorage.removeItem("tokens");

export function errorText(data) {
  if (!data) return "Something went wrong. Try again.";
  if (typeof data === "string") return data;
  if (data.detail) return data.detail;
  const first = Object.values(data)[0];
  return Array.isArray(first) ? first[0] : String(first);
}

async function refresh() {
  const t = getTokens();
  if (!t?.refresh) return false;
  const res = await fetch(`${BASE}/auth/refresh/`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: t.refresh }),
  });
  if (!res.ok) return false;
  setTokens({ ...t, access: (await res.json()).access });
  return true;
}

export async function api(path, { method = "GET", body, retry = true } = {}) {
  const t = getTokens();
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json", ...(t ? { Authorization: `Bearer ${t.access}` } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401 && retry && t && (await refresh())) return api(path, { method, body, retry: false });
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) throw new Error(errorText(data));
  return data;
}

export const fmt = (iso) =>
  new Date(iso).toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
