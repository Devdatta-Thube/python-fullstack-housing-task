import { type EstimateResponse, featureLabels } from "@/lib/schemas";
import { formatCurrency, formatDate, formatNumber } from "@/lib/format";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const featureKeys = Object.keys(featureLabels) as (keyof typeof featureLabels)[];

export function CompareView({ a, b }: { a: EstimateResponse; b: EstimateResponse }) {
  const priceDiff = b.predicted_price - a.predicted_price;
  const pctDiff = (priceDiff / a.predicted_price) * 100;

  return (
    <Card>
      <CardTitle>Compare</CardTitle>
      <CardDescription>
        {a.label ?? "A"} vs {b.label ?? "B"}
      </CardDescription>

      <div className="mt-4 grid grid-cols-3 gap-2 text-sm">
        <div />
        <div className="text-xs font-medium text-muted">{a.label ?? "A"}</div>
        <div className="text-xs font-medium text-muted">{b.label ?? "B"}</div>

        <div className="font-medium">Predicted price</div>
        <div className="tabular-nums">{formatCurrency(a.predicted_price)}</div>
        <div
          className={cn(
            "tabular-nums",
            priceDiff > 0
              ? "text-emerald-600"
              : priceDiff < 0
                ? "text-red-600"
                : "",
          )}
        >
          {formatCurrency(b.predicted_price)}
          <span className="ml-1 text-xs">
            ({priceDiff >= 0 ? "+" : ""}
            {pctDiff.toFixed(1)}%)
          </span>
        </div>

        <div className="font-medium">Created</div>
        <div className="text-muted">{formatDate(a.created_at)}</div>
        <div className="text-muted">{formatDate(b.created_at)}</div>

        {featureKeys.map((key) => {
          const av = a.features[key];
          const bv = b.features[key];
          const same = av === bv;
          return (
            <div key={key} className="contents">
              <div className="text-xs text-muted">{featureLabels[key]}</div>
              <div className="tabular-nums">{formatNumber(av)}</div>
              <div
                className={cn(
                  "tabular-nums",
                  !same && "font-medium text-foreground",
                )}
              >
                {formatNumber(bv)}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
