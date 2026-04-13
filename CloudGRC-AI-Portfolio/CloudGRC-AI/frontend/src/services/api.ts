import axios from "axios";
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// ── Attach JWT on every request ──
api.interceptors.request.use((config) => {
  const token = Cookies.get("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Auto-refresh token on 401 ──
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = Cookies.get("refresh_token");
        const res = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refresh });
        Cookies.set("access_token", res.data.access_token, { expires: 1 });
        original.headers.Authorization = `Bearer ${res.data.access_token}`;
        return api(original);
      } catch {
        Cookies.remove("access_token");
        Cookies.remove("refresh_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth ──
export const authAPI = {
  register: (data: any) => api.post("/auth/register", data),
  login:    (data: any) => api.post("/auth/login", data),
  me:       ()          => api.get("/auth/me"),
  logout:   ()          => api.post("/auth/logout"),
};

// ── Scans ──
export const scansAPI = {
  create:     (data: any)            => api.post("/scans", data),
  list:       (skip = 0, limit = 20) => api.get(`/scans?skip=${skip}&limit=${limit}`),
  get:        (id: string)           => api.get(`/scans/${id}`),
  download:   (id: string)           => api.get(`/scans/${id}/download`),
  delete:     (id: string)           => api.delete(`/scans/${id}`),
};

// ── Credentials ──
export const credentialsAPI = {
  save:   (data: any)  => api.post("/credentials", data),
  list:   ()           => api.get("/credentials"),
  delete: (id: string) => api.delete(`/credentials/${id}`),
};

// ── Dashboard ──
export const dashboardAPI = {
  stats: () => api.get("/dashboard/stats"),
};

// ── Billing ──
export const billingAPI = {
  plans:  ()           => api.get("/billing/plans"),
  status: ()           => api.get("/billing/status"),
  order:  (plan: string) => api.post("/billing/order", { plan }),
  verify: (data: any)  => api.post("/billing/verify", data),
};

export default api;
