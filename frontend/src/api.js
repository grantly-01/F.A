import { mockGrants, mockStats } from "./mockData";

const API_URL = "http://127.0.0.1:8000";

async function fetchJson(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getStats() {
  try {
    return await fetchJson(`${API_URL}/stats`);
  } catch {
    return mockStats;
  }
}

export async function getGrants(searchQuery = "") {
  const q = (searchQuery || "").trim();

  try {
    const url = q
      ? `${API_URL}/grants?search=${encodeURIComponent(q)}`
      : `${API_URL}/grants`;
    return await fetchJson(url);
  } catch {
    const active = mockGrants.filter((g) => g.status === "active");
    if (!q) return active;

    const low = q.toLowerCase();
    return active.filter((g) => {
      const text = `${g.title ?? ""} ${g.description ?? ""} ${g.funder ?? ""}`.toLowerCase();
      return text.includes(low);
    });
  }
}

export async function loginAdmin(username = "", password = "") {
  try {
    return await fetchJson(`${API_URL}/login`, { method: "POST" });
  } catch {
    if (username !== "admin" || password !== "admin") {
      throw new Error("Неверный логин или пароль");
    }
    return { access_token: "mock-token", token_type: "bearer" };
  }
}

export async function collectFull() {
  try {
    return await fetchJson(`${API_URL}/collect/full`, { method: "POST" });
  } catch {
    return { status: "ok (mock)" };
  }
}