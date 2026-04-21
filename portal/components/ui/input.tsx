import { cn } from "@/lib/utils";
import { InputHTMLAttributes, forwardRef } from "react";

export const Input = forwardRef<
  HTMLInputElement,
  InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "h-10 w-full rounded-md border border-border bg-surface px-3 text-sm shadow-sm transition-colors",
      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
      "disabled:cursor-not-allowed disabled:opacity-50",
      "aria-[invalid=true]:border-red-500 aria-[invalid=true]:focus-visible:ring-red-500",
      className,
    )}
    {...props}
  />
));
Input.displayName = "Input";

export function Field({
  label,
  error,
  hint,
  children,
}: {
  label: string;
  error?: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-sm font-medium">{label}</span>
      {children}
      {error ? (
        <span className="text-xs text-red-500">{error}</span>
      ) : hint ? (
        <span className="text-xs text-muted">{hint}</span>
      ) : null}
    </label>
  );
}
