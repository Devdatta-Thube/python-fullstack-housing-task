"use client";

import { useEffect } from "react";
import { Container } from "@/components/ui/container";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";

export default function EstimatorError({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string };
  unstable_retry: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <Container className="py-10">
      <Card className="max-w-xl">
        <CardTitle>Estimator is unavailable</CardTitle>
        <CardDescription>
          {error.message || "The estimator API could not be reached."}
        </CardDescription>
        <div className="mt-4">
          <Button onClick={() => unstable_retry()}>Try again</Button>
        </div>
      </Card>
    </Container>
  );
}
