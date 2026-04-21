import Link from "next/link";
import { ArrowRight, Calculator, LineChart } from "lucide-react";
import { Container } from "@/components/ui/container";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";

const apps = [
  {
    href: "/estimator",
    title: "Price Estimator",
    description:
      "Enter property features and get a predicted price plus a history of past estimates.",
    icon: Calculator,
  },
  {
    href: "/market",
    title: "Market Insights",
    description:
      "Aggregated stats, price trends, and what-if analysis over the full dataset.",
    icon: LineChart,
  },
];

export default function Home() {
  return (
    <Container className="py-16">
      <section className="max-w-2xl">
        <h1 className="text-4xl font-semibold tracking-tight">
          Housing Portal
        </h1>
        <p className="mt-4 text-lg text-muted">
          Two small apps sharing one ML model. Estimate prices for individual
          properties, or browse aggregate market insights.
        </p>
      </section>

      <section className="mt-12 grid gap-4 sm:grid-cols-2">
        {apps.map(({ href, title, description, icon: Icon }) => (
          <Link key={href} href={href} className="group">
            <Card className="h-full transition-colors group-hover:border-accent">
              <div className="flex items-start gap-3">
                <div className="rounded-md bg-accent/10 p-2 text-accent">
                  <Icon className="h-5 w-5" aria-hidden />
                </div>
                <div className="flex-1">
                  <CardTitle>{title}</CardTitle>
                  <CardDescription>{description}</CardDescription>
                </div>
                <ArrowRight
                  className="h-4 w-4 text-muted transition-transform group-hover:translate-x-0.5 group-hover:text-accent"
                  aria-hidden
                />
              </div>
            </Card>
          </Link>
        ))}
      </section>
    </Container>
  );
}
