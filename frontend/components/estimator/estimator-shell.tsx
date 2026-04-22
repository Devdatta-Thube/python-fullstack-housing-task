"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  clearHistory,
  createEstimate,
  deleteHistoryItem,
  listHistory,
} from "@/lib/estimator-client";
import type { EstimateRequest, EstimateResponse } from "@/lib/schemas";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { EstimatorForm } from "./estimator-form";
import { ResultCard } from "./result-card";
import { HistoryList } from "./history-list";
import { CompareView } from "./compare-view";

export function EstimatorShell() {
  const [history, setHistory] = useState<EstimateResponse[]>([]);
  const [latest, setLatest] = useState<EstimateResponse | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [pending, setPending] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await listHistory();
      setHistory(data.items);
      setSelectedIds((prev) =>
        prev.filter((id) => data.items.some((it) => it.id === id)),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load history");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleSubmit = useCallback(
    async (values: EstimateRequest) => {
      setPending(true);
      setError(null);
      try {
        const result = await createEstimate(values);
        setLatest(result);
        await refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to create estimate");
      } finally {
        setPending(false);
      }
    },
    [refresh],
  );

  const handleDelete = useCallback(
    async (id: string) => {
      setBusy(true);
      setError(null);
      try {
        await deleteHistoryItem(id);
        if (latest?.id === id) setLatest(null);
        await refresh();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to delete");
      } finally {
        setBusy(false);
      }
    },
    [latest, refresh],
  );

  const handleClear = useCallback(async () => {
    if (!confirm("Clear all history? This cannot be undone.")) return;
    setBusy(true);
    setError(null);
    try {
      await clearHistory();
      setLatest(null);
      setSelectedIds([]);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to clear");
    } finally {
      setBusy(false);
    }
  }, [refresh]);

  const toggleSelect = useCallback((id: string) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) return prev.filter((i) => i !== id);
      if (prev.length >= 2) return prev;
      return [...prev, id];
    });
  }, []);

  const compared = useMemo(() => {
    if (selectedIds.length !== 2) return null;
    const [a, b] = selectedIds.map((id) =>
      history.find((it) => it.id === id),
    );
    return a && b ? { a, b } : null;
  }, [selectedIds, history]);

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_1.1fr]">
      <Card>
        <CardTitle>Property features</CardTitle>
        <CardDescription>
          Adjust the values, then submit to get a prediction.
        </CardDescription>
        <div className="mt-4">
          <EstimatorForm onSubmit={handleSubmit} pending={pending} />
        </div>
      </Card>

      <div className="flex flex-col gap-6">
        {error ? (
          <Card className="border-red-300 bg-red-50 dark:bg-red-950/30">
            <CardTitle className="text-red-700 dark:text-red-400">
              Something went wrong
            </CardTitle>
            <CardDescription>{error}</CardDescription>
          </Card>
        ) : null}

        {latest ? (
          <ResultCard estimate={latest} />
        ) : (
          <Card>
            <CardTitle>Latest estimate</CardTitle>
            <CardDescription>
              Submit the form to see a price here.
            </CardDescription>
          </Card>
        )}

        {compared ? <CompareView a={compared.a} b={compared.b} /> : null}

        <HistoryList
          items={history}
          selectedIds={selectedIds}
          onToggleSelect={toggleSelect}
          onDelete={handleDelete}
          onClear={handleClear}
          busy={busy}
        />
      </div>
    </div>
  );
}
