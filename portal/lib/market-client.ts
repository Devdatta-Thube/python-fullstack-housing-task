import { MARKET_API_URL } from "./api";
import type { HousingFeatures } from "./schemas";

export interface Summary {
  min: number;
  max: number;
  mean: number;
  median: number;
}

export interface HistogramBucket {
  range: string;
  count: number;
}

export interface MarketStats {
  count: number;
  price: Summary & { histogram: HistogramBucket[] };
  features: Record<string, Summary>;
  bedrooms: { value: number; count: number }[];
}

export interface MarketRow extends HousingFeatures {
  id: number;
  price: number;
}

export interface RowsResponse {
  total: number;
  items: MarketRow[];
}

export interface WhatIfResponse {
  features: HousingFeatures;
  predicted_price: number;
  baseline?: MarketRow;
  delta_from_actual?: number;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${MARKET_API_URL}${path}`, {
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
      if (body?.detail)
        detail =
          typeof body.detail === "string"
            ? body.detail
            : JSON.stringify(body.detail);
    } catch {}
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const getStats = () => req<MarketStats>("/api/stats/");

export const getRows = (params: {
  limit?: number;
  offset?: number;
  sort_by?: string;
  desc?: boolean;
  min_price?: number;
  max_price?: number;
  bedrooms?: number;
}) => {
  const qs = new URLSearchParams();
  if (params.limit != null) qs.set("limit", String(params.limit));
  if (params.offset != null) qs.set("offset", String(params.offset));
  if (params.sort_by) qs.set("sort_by", params.sort_by);
  if (params.desc) qs.set("desc", "1");
  if (params.min_price != null) qs.set("min_price", String(params.min_price));
  if (params.max_price != null) qs.set("max_price", String(params.max_price));
  if (params.bedrooms != null) qs.set("bedrooms", String(params.bedrooms));
  return req<RowsResponse>(`/api/rows/?${qs.toString()}`);
};

export const postWhatIf = (payload: {
  features: HousingFeatures;
  baseline_id?: number | null;
}) =>
  req<WhatIfResponse>("/api/what-if/", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const csvExportUrl = () => `${MARKET_API_URL}/api/export/csv/`;
export const pdfExportUrl = () => `${MARKET_API_URL}/api/export/pdf/`;
