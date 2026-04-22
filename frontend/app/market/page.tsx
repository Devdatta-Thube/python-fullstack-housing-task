import { Container } from "@/components/ui/container";
import { MarketShell } from "@/components/market/market-shell";

export default function MarketPage() {
  return (
    <Container className="py-10">
      <header className="max-w-2xl">
        <h1 className="text-3xl font-semibold tracking-tight">
          Market Insights
        </h1>
        <p className="mt-2 text-muted">
          Aggregated statistics, dataset browser, and what-if analysis.
        </p>
      </header>
      <div className="mt-8">
        <MarketShell />
      </div>
    </Container>
  );
}
