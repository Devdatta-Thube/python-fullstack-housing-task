import { type EstimateResponse, featureLabels } from "@/lib/schemas";
import { formatCurrency, formatDate, formatNumber } from "@/lib/format";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";

export function ResultCard({ estimate }: { estimate: EstimateResponse }) {
  return (
    <Card>
      <div className="flex items-baseline justify-between gap-4">
        <div>
          <CardTitle>
            {estimate.label ? estimate.label : "Latest estimate"}
          </CardTitle>
          <CardDescription>{formatDate(estimate.created_at)}</CardDescription>
        </div>
        <div className="text-right">
          <div className="text-3xl font-semibold tabular-nums text-accent">
            {formatCurrency(estimate.predicted_price)}
          </div>
          <div className="text-xs text-muted">predicted price</div>
        </div>
      </div>

      <dl className="mt-5 grid grid-cols-2 gap-x-4 gap-y-2 text-sm sm:grid-cols-3">
        {(Object.keys(featureLabels) as (keyof typeof featureLabels)[]).map(
          (key) => (
            <div key={key}>
              <dt className="text-xs text-muted">{featureLabels[key]}</dt>
              <dd className="tabular-nums">
                {formatNumber(estimate.features[key])}
              </dd>
            </div>
          ),
        )}
      </dl>
    </Card>
  );
}
