import { Container } from "@/components/ui/container";
import { EstimatorShell } from "@/components/estimator/estimator-shell";

export default function EstimatorPage() {
  return (
    <Container className="py-10">
      <header className="max-w-2xl">
        <h1 className="text-3xl font-semibold tracking-tight">
          Price Estimator
        </h1>
        <p className="mt-2 text-muted">
          Enter property features to get a predicted price from the ML model.
          Submissions are saved to history so you can compare two at a time.
        </p>
      </header>

      <div className="mt-8">
        <EstimatorShell />
      </div>
    </Container>
  );
}
