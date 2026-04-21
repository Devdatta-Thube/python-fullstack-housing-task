"""
DRF serializers.

We only validate *input* payloads with serializers (what-if POST body).
Aggregate output is already plain JSON-safe dicts from services.compute_stats,
so we return them directly from views without wrapping in a serializer.
"""

from rest_framework import serializers


class HousingFeaturesSerializer(serializers.Serializer):
    """Mirrors ml-api's HousingFeatures validation bounds."""

    square_footage = serializers.FloatField(min_value=0.01, max_value=20000)
    bedrooms = serializers.IntegerField(min_value=0, max_value=20)
    bathrooms = serializers.FloatField(min_value=0, max_value=20)
    year_built = serializers.IntegerField(min_value=1800, max_value=2100)
    lot_size = serializers.FloatField(min_value=0.01, max_value=500000)
    distance_to_city_center = serializers.FloatField(min_value=0, max_value=500)
    school_rating = serializers.FloatField(min_value=0, max_value=10)


class WhatIfRequestSerializer(serializers.Serializer):
    """
    Forwarded to ml-api /predict. We ask for the features plus an optional
    baseline_id — if provided, the response includes the dataset row and the
    delta between predicted and actual price for that row.
    """

    features = HousingFeaturesSerializer()
    baseline_id = serializers.IntegerField(required=False, allow_null=True)
