// Prices are rendered in INR with Indian digit grouping (lakh/crore). Raw values
// from the dataset are whole-rupee integers, so we suppress fractional paise.
const currencyFmt = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const numberFmt = new Intl.NumberFormat("en-IN");

const dateFmt = new Intl.DateTimeFormat("en-IN", {
  dateStyle: "medium",
  timeStyle: "short",
});

export const formatCurrency = (n: number) => currencyFmt.format(n);
export const formatNumber = (n: number) => numberFmt.format(n);
export const formatDate = (iso: string) => dateFmt.format(new Date(iso));
