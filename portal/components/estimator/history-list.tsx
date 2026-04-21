"use client";

import { Trash2 } from "lucide-react";
import { type EstimateResponse } from "@/lib/schemas";
import { formatCurrency, formatDate } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export function HistoryList({
  items,
  selectedIds,
  onToggleSelect,
  onDelete,
  onClear,
  busy,
}: {
  items: EstimateResponse[];
  selectedIds: string[];
  onToggleSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onClear: () => void;
  busy: boolean;
}) {
  if (items.length === 0) {
    return (
      <Card>
        <CardTitle>History</CardTitle>
        <CardDescription>No estimates yet — submit the form to start.</CardDescription>
      </Card>
    );
  }

  return (
    <Card className="p-0">
      <div className="flex items-center justify-between border-b border-border px-6 py-4">
        <div>
          <CardTitle>History</CardTitle>
          <CardDescription>
            {items.length} estimate{items.length === 1 ? "" : "s"} · select 2 to compare
          </CardDescription>
        </div>
        <Button
          variant="secondary"
          onClick={onClear}
          disabled={busy}
          aria-label="Clear all history"
        >
          Clear all
        </Button>
      </div>
      <ul className="divide-y divide-border">
        {items.map((item) => {
          const selected = selectedIds.includes(item.id);
          const disabled =
            !selected && selectedIds.length >= 2;
          return (
            <li
              key={item.id}
              className={cn(
                "flex items-center gap-3 px-6 py-3 text-sm",
                selected && "bg-accent/5",
              )}
            >
              <input
                type="checkbox"
                className="h-4 w-4 accent-[var(--accent)] disabled:opacity-30"
                checked={selected}
                disabled={disabled}
                onChange={() => onToggleSelect(item.id)}
                aria-label={`Select ${item.label ?? item.id} for comparison`}
              />
              <div className="flex-1 min-w-0">
                <div className="truncate font-medium">
                  {item.label ?? <span className="text-muted">Untitled</span>}
                </div>
                <div className="text-xs text-muted">
                  {formatDate(item.created_at)} · {item.features.bedrooms} bd ·{" "}
                  {item.features.bathrooms} ba ·{" "}
                  {item.features.square_footage.toLocaleString()} sqft
                </div>
              </div>
              <div className="tabular-nums font-medium text-accent">
                {formatCurrency(item.predicted_price)}
              </div>
              <Button
                variant="ghost"
                aria-label={`Delete ${item.label ?? item.id}`}
                onClick={() => onDelete(item.id)}
                disabled={busy}
                className="h-8 w-8 p-0"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </li>
          );
        })}
      </ul>
    </Card>
  );
}
