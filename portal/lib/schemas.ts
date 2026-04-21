import { z } from "zod";

export const housingFeaturesSchema = z.object({
  square_footage: z.coerce
    .number()
    .positive("Must be greater than 0")
    .max(20000, "Max 20,000"),
  bedrooms: z.coerce
    .number()
    .int("Whole number only")
    .min(0, "Cannot be negative")
    .max(20, "Max 20"),
  bathrooms: z.coerce
    .number()
    .min(0, "Cannot be negative")
    .max(20, "Max 20"),
  year_built: z.coerce
    .number()
    .int("Whole number only")
    .min(1800, "Must be 1800 or later")
    .max(2100, "Max 2100"),
  lot_size: z.coerce
    .number()
    .positive("Must be greater than 0")
    .max(500000, "Max 500,000"),
  distance_to_city_center: z.coerce
    .number()
    .min(0, "Cannot be negative")
    .max(500, "Max 500"),
  school_rating: z.coerce
    .number()
    .min(0, "Min 0")
    .max(10, "Max 10"),
});

export type HousingFeatures = z.infer<typeof housingFeaturesSchema>;

export const estimateRequestSchema = z.object({
  features: housingFeaturesSchema,
  label: z
    .string()
    .max(100, "Max 100 characters")
    .optional()
    .or(z.literal("").transform(() => undefined)),
});

// Input = what the form binds to (strings from <input type="number">), output = coerced numbers.
export type EstimateRequestInput = z.input<typeof estimateRequestSchema>;
export type EstimateRequest = z.output<typeof estimateRequestSchema>;

export interface EstimateResponse {
  id: string;
  features: HousingFeatures;
  predicted_price: number;
  label: string | null;
  created_at: string;
}

export interface HistoryListResponse {
  items: EstimateResponse[];
  total: number;
}

export const featureLabels: Record<keyof HousingFeatures, string> = {
  square_footage: "Square footage",
  bedrooms: "Bedrooms",
  bathrooms: "Bathrooms",
  year_built: "Year built",
  lot_size: "Lot size (sq ft)",
  distance_to_city_center: "Distance to city (km)",
  school_rating: "School rating (0–10)",
};
