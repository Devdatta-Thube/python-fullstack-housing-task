import { ESTIMATOR_API_URL } from "./api";
import type {
  EstimateRequest,
  EstimateResponse,
  HistoryListResponse,
} from "./schemas";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${ESTIMATOR_API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    let detail = `Request failed: ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {}
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const createEstimate = (payload: EstimateRequest) =>
  request<EstimateResponse>("/estimate", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const listHistory = (limit = 50, offset = 0) =>
  request<HistoryListResponse>(`/history?limit=${limit}&offset=${offset}`);

export const deleteHistoryItem = (id: string) =>
  request<void>(`/history/${id}`, { method: "DELETE" });

export const clearHistory = () =>
  request<void>("/history", { method: "DELETE" });
