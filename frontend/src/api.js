// Small wrapper around fetch for the Flask API.
const BASE = import.meta.env?.VITE_API_URL ?? "";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

export const api = {
  list: ({ status = "all", q = "" } = {}) =>
    request(`/tasks?status=${status}&q=${encodeURIComponent(q)}`),
  create: (task) => request("/tasks", { method: "POST", body: JSON.stringify(task) }),
  update: (id, fields) =>
    request(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify(fields) }),
  remove: (id) => request(`/tasks/${id}`, { method: "DELETE" }),
  clearCompleted: () => request("/tasks/completed", { method: "DELETE" }),
  stats: () => request("/stats"),
};
