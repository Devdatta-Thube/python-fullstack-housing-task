const currencyFmt = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const numberFmt = new Intl.NumberFormat("en-US");

const dateFmt = new Intl.DateTimeFormat("en-US", {
  dateStyle: "medium",
  timeStyle: "short",
});

export const formatCurrency = (n: number) => currencyFmt.format(n);
export const formatNumber = (n: number) => numberFmt.format(n);
export const formatDate = (iso: string) => dateFmt.format(new Date(iso));
