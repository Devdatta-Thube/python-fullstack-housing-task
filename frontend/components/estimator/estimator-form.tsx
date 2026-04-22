"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  estimateRequestSchema,
  type EstimateRequest,
  type EstimateRequestInput,
} from "@/lib/schemas";
import { Field, Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const sample: EstimateRequestInput = {
  features: {
    square_footage: 1850,
    bedrooms: 3,
    bathrooms: 2,
    year_built: 1998,
    lot_size: 7500,
    distance_to_city_center: 5.6,
    school_rating: 8.2,
  },
  label: "",
};

export function EstimatorForm({
  onSubmit,
  pending,
}: {
  onSubmit: (values: EstimateRequest) => Promise<void>;
  pending: boolean;
}) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<EstimateRequestInput, unknown, EstimateRequest>({
    resolver: zodResolver(estimateRequestSchema),
    defaultValues: sample,
    mode: "onBlur",
  });

  const f = errors.features;

  return (
    <form
      onSubmit={handleSubmit(async (v) => {
        await onSubmit(v);
      })}
      className="grid gap-4"
      noValidate
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Square footage" error={f?.square_footage?.message}>
          <Input
            type="number"
            step="1"
            aria-invalid={!!f?.square_footage}
            {...register("features.square_footage")}
          />
        </Field>
        <Field label="Lot size (sq ft)" error={f?.lot_size?.message}>
          <Input
            type="number"
            step="1"
            aria-invalid={!!f?.lot_size}
            {...register("features.lot_size")}
          />
        </Field>
        <Field label="Bedrooms" error={f?.bedrooms?.message}>
          <Input
            type="number"
            step="1"
            aria-invalid={!!f?.bedrooms}
            {...register("features.bedrooms")}
          />
        </Field>
        <Field label="Bathrooms" error={f?.bathrooms?.message}>
          <Input
            type="number"
            step="0.5"
            aria-invalid={!!f?.bathrooms}
            {...register("features.bathrooms")}
          />
        </Field>
        <Field label="Year built" error={f?.year_built?.message}>
          <Input
            type="number"
            step="1"
            aria-invalid={!!f?.year_built}
            {...register("features.year_built")}
          />
        </Field>
        <Field
          label="Distance to city centre (km)"
          error={f?.distance_to_city_center?.message}
        >
          <Input
            type="number"
            step="0.1"
            aria-invalid={!!f?.distance_to_city_center}
            {...register("features.distance_to_city_center")}
          />
        </Field>
        <Field
          label="School rating (0–10)"
          error={f?.school_rating?.message}
          hint="Higher is better"
        >
          <Input
            type="number"
            step="0.1"
            aria-invalid={!!f?.school_rating}
            {...register("features.school_rating")}
          />
        </Field>
        <Field
          label="Label (optional)"
          error={errors.label?.message}
          hint="A short note to remember this estimate"
        >
          <Input
            type="text"
            maxLength={100}
            placeholder="e.g. Maple St #4"
            {...register("label")}
          />
        </Field>
      </div>

      <div className="flex items-center gap-2">
        <Button type="submit" disabled={pending}>
          {pending ? "Estimating…" : "Get estimate"}
        </Button>
        <Button
          type="button"
          variant="secondary"
          disabled={pending}
          onClick={() => reset(sample)}
        >
          Reset
        </Button>
      </div>
    </form>
  );
}
