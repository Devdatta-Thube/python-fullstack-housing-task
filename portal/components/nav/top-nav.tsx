"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home } from "lucide-react";
import { cn } from "@/lib/utils";
import { Container } from "@/components/ui/container";

const links = [
  { href: "/estimator", label: "Estimator" },
  { href: "/market", label: "Market" },
];

export function TopNav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-10 border-b border-border bg-surface/80 backdrop-blur">
      <Container className="flex h-14 items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <Home className="h-4 w-4" aria-hidden />
          <span>Housing Portal</span>
        </Link>
        <nav className="flex items-center gap-1">
          {links.map((link) => {
            const active =
              pathname === link.href || pathname.startsWith(`${link.href}/`);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "rounded-md px-3 py-1.5 text-sm transition-colors",
                  active
                    ? "bg-accent text-accent-foreground"
                    : "text-muted hover:bg-border/50 hover:text-foreground",
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </Container>
    </header>
  );
}
