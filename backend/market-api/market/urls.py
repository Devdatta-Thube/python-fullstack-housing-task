from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("stats/", views.StatsView.as_view(), name="stats"),
    path("rows/", views.RowsView.as_view(), name="rows"),
    path("what-if/", views.WhatIfView.as_view(), name="what-if"),
    path("export/csv/", views.ExportCsvView.as_view(), name="export-csv"),
    path("export/pdf/", views.ExportPdfView.as_view(), name="export-pdf"),
]
