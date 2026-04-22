"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Download, FileText } from "lucide-react";
import {
  csvExportUrl,
  getRows,
  getStats,
  pdfExportUrl,
  postWhatIf,
  type MarketRow,
  type MarketStats,
  type WhatIfResponse,
} from "@/lib/market-client";
import type { HousingFeatures } from "@/lib/schemas";
import { formatCurrency, formatNumber } from "@/lib/format";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { Field, Input } from "@/components/ui/input";
import { EstimatorForm } from "@/components/estimator/estimator-form";

export function MarketShell() {
  const [stats, setStats] = useState<MarketStats | null>(null);
  const [rows, setRows] = useState<MarketRow[]>([]);
  const [rowsTotal, setRowsTotal] = useState(0);
  const [bedroomFilter, setBedroomFilter] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("id");
  const [desc, setDesc] = useState(false);
  const [whatIf, setWhatIf] = useState<WhatIfResponse | null>(null);
  const [baselineId, setBaselineId] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const s = await getStats();
        setStats(s);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load stats");
      }
    })();
  }, []);

  const loadRows = useCallback(async () => {
    try {
      const r = await getRows({
        limit: 50,
        sort_by: sortBy,
        desc,
        bedrooms:
          bedroomFilter === "" ? undefined : Number(bedroomFilter),
      });
      setRows(r.items);
      setRowsTotal(r.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load rows");
    }
  }, [sortBy, desc, bedroomFilter]);

  useEffect(() => {
    loadRows();
  }, [loadRows]);

  const handleWhatIf = useCallback(
    async ({ features }: { features: HousingFeatures }) => {
      setPending(true);
      setError(null);
      try {
        const res = await postWhatIf({
          features,
          baseline_id:
            baselineId === "" ? null : Number(baselineId),
        });
        setWhatIf(res);
      } catch (e) {
        setError(e instanceof Error ? e.message : "What-if failed");
      } finally {
        setPending(false);
      }
    },
    [baselineId],
  );

  const histogramMax = useMemo(
    () => Math.max(1, ...(stats?.price.histogram ?? []).map((b) => b.count)),
    [stats],
  );

  return (
    <div className="grid gap-6">
      {error ? (
        <Card className="border-red-300 bg-red-50 dark:bg-red-950/30">
          <CardTitle className="text-red-700 dark:text-red-400">
            Something went wrong
          </CardTitle>
          <CardDescription>{error}</CardDescription>
        </Card>
      ) : null}

      {/* Summary cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Properties" value={stats ? String(stats.count) : "…"} />
        <StatCard
          label="Median price"
          value={stats ? formatCurrency(stats.price.median) : "…"}
        />
        <StatCard
          label="Mean price"
          value={stats ? formatCurrency(stats.price.mean) : "…"}
        />
        <StatCard
          label="Price range"
          value={
            stats
              ? `${formatCurrency(stats.price.min)} – ${formatCurrency(stats.price.max)}`
              : "…"
          }
        />
      </div>

      {/* Histogram + bedrooms */}
      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <Card>
          <CardTitle>Price distribution</CardTitle>
          <CardDescription>8 equal-width buckets across the dataset.</CardDescription>
          <div className="mt-4 flex h-40 items-end gap-2">
            {(stats?.price.histogram ?? []).map((bucket, i) => (
              <div
                key={i}
                className="flex flex-1 flex-col items-center gap-1"
                title={`${bucket.range}: ${bucket.count}`}
              >
                <div
                  className="w-full rounded-t bg-accent/70 transition-colors hover:bg-accent"
                  style={{
                    height: `${(bucket.count / histogramMax) * 100}%`,
                    minHeight: bucket.count > 0 ? "4px" : 0,
                  }}
                />
                <div className="text-[10px] text-muted">{bucket.count}</div>
              </div>
            ))}
          </div>
          <div className="mt-1 grid grid-cols-8 gap-2 text-[10px] text-muted">
            {(stats?.price.histogram ?? []).map((b, i) => (
              <div key={i} className="text-center break-words">
                {b.range}
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <CardTitle>Bedrooms</CardTitle>
          <CardDescription>How many of each in the dataset.</CardDescription>
          <ul className="mt-4 space-y-2">
            {(stats?.bedrooms ?? []).map((b) => (
              <li key={b.value} className="flex items-center gap-3">
                <span className="w-6 text-sm font-medium">{b.value}</span>
                <div className="h-3 flex-1 rounded-full bg-border">
                  <div
                    className="h-full rounded-full bg-accent"
                    style={{
                      width: `${(b.count / (stats?.count || 1)) * 100}%`,
                    }}
                  />
                </div>
                <span className="w-8 text-right text-xs tabular-nums text-muted">
                  {b.count}
                </span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {/* What-if */}
      <Card>
        <CardTitle>What-if analysis</CardTitle>
        <CardDescription>
          Enter features to see the model&apos;s price and compare against any
          dataset row.
        </CardDescription>
        <div className="mt-4 grid gap-4">
          <Field
            label="Compare against dataset id (optional)"
            hint="1–50. Leave blank to just predict."
          >
            <Input
              type="number"
              min={1}
              max={50}
              value={baselineId}
              onChange={(e) => setBaselineId(e.target.value)}
              placeholder="e.g. 1"
            />
          </Field>
          <EstimatorForm onSubmit={handleWhatIf} pending={pending} />
          {whatIf ? (
            <div className="rounded-md border border-border bg-background p-4 text-sm">
              <div className="flex items-baseline justify-between">
                <span className="font-medium">Predicted</span>
                <span className="text-xl font-semibold text-accent">
                  {formatCurrency(whatIf.predicted_price)}
                </span>
              </div>
              {whatIf.baseline ? (
                <div className="mt-3 space-y-1">
                  <div className="flex justify-between">
                    <span className="text-muted">
                      Actual (id #{whatIf.baseline.id})
                    </span>
                    <span className="tabular-nums">
                      {formatCurrency(whatIf.baseline.price)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted">Delta</span>
                    <span
                      className={
                        (whatIf.delta_from_actual ?? 0) >= 0
                          ? "tabular-nums text-emerald-600"
                          : "tabular-nums text-red-600"
                      }
                    >
                      {(whatIf.delta_from_actual ?? 0) >= 0 ? "+" : ""}
                      {formatCurrency(whatIf.delta_from_actual ?? 0)}
                    </span>
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}
        </div>
      </Card>

      {/* Rows table + filters + exports */}
      <Card className="p-0">
        <div className="flex flex-wrap items-end gap-3 border-b border-border px-6 py-4">
          <div className="flex-1">
            <CardTitle>Dataset</CardTitle>
            <CardDescription>
              {rowsTotal} matching row{rowsTotal === 1 ? "" : "s"}
            </CardDescription>
          </div>
          <Field label="Bedrooms">
            <select
              className="h-10 rounded-md border border-border bg-surface px-3 text-sm"
              value={bedroomFilter}
              onChange={(e) => setBedroomFilter(e.target.value)}
            >
              <option value="">All</option>
              {(stats?.bedrooms ?? []).map((b) => (
                <option key={b.value} value={b.value}>
                  {b.value}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Sort by">
            <select
              className="h-10 rounded-md border border-border bg-surface px-3 text-sm"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              {[
                "id",
                "price",
                "square_footage",
                "bedrooms",
                "bathrooms",
                "year_built",
                "lot_size",
                "distance_to_city_center",
                "school_rating",
              ].map((k) => (
                <option key={k} value={k}>
                  {k.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Order">
            <select
              className="h-10 rounded-md border border-border bg-surface px-3 text-sm"
              value={desc ? "desc" : "asc"}
              onChange={(e) => setDesc(e.target.value === "desc")}
            >
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </select>
          </Field>
          <div className="flex gap-2">
            <a
              href={csvExportUrl()}
              download
              className="inline-flex h-10 items-center justify-center rounded-md border border-border bg-surface px-4 text-sm font-medium hover:bg-background"
            >
              <Download className="mr-2 h-4 w-4" /> CSV
            </a>
            <a
              href={pdfExportUrl()}
              download
              className="inline-flex h-10 items-center justify-center rounded-md border border-border bg-surface px-4 text-sm font-medium hover:bg-background"
            >
              <FileText className="mr-2 h-4 w-4" /> PDF
            </a>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-background text-left text-xs text-muted">
              <tr>
                <th className="px-6 py-2">ID</th>
                <th className="px-3 py-2">Sqft</th>
                <th className="px-3 py-2">Beds</th>
                <th className="px-3 py-2">Baths</th>
                <th className="px-3 py-2">Year</th>
                <th className="px-3 py-2">Lot</th>
                <th className="px-3 py-2">Dist (km)</th>
                <th className="px-3 py-2">School</th>
                <th className="px-6 py-2 text-right">Price</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border tabular-nums">
              {rows.map((r) => (
                <tr key={r.id} className="hover:bg-accent/5">
                  <td className="px-6 py-2">{r.id}</td>
                  <td className="px-3 py-2">{formatNumber(r.square_footage)}</td>
                  <td className="px-3 py-2">{r.bedrooms}</td>
                  <td className="px-3 py-2">{r.bathrooms}</td>
                  <td className="px-3 py-2">{r.year_built}</td>
                  <td className="px-3 py-2">{formatNumber(r.lot_size)}</td>
                  <td className="px-3 py-2">{r.distance_to_city_center}</td>
                  <td className="px-3 py-2">{r.school_rating}</td>
                  <td className="px-6 py-2 text-right font-medium text-accent">
                    {formatCurrency(r.price)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <div className="text-xs font-medium uppercase tracking-wide text-muted">
        {label}
      </div>
      <div className="mt-1 text-2xl font-semibold tabular-nums">{value}</div>
    </Card>
  );
}
