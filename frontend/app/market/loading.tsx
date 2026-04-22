import { Container } from "@/components/ui/container";

export default function Loading() {
  return (
    <Container className="py-10">
      <p className="text-muted">Loading market data…</p>
    </Container>
  );
}
