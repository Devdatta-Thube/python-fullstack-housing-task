"""
CSV + PDF exporters. Kept dumb on purpose — they render whatever rows you pass.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------- CSV ----------------------------


def rows_to_csv(rows: Iterable[dict[str, Any]], columns: list[str]) -> bytes:
    """Encode rows as CSV bytes (utf-8). `columns` controls header + order."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue().encode("utf-8")


# ---------------------------- PDF ----------------------------


def stats_to_pdf(stats: dict[str, Any]) -> bytes:
    """Render a one-page market summary PDF from services.compute_stats output."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Housing Market Summary",
    )
    styles = getSampleStyleSheet()
    story: list[Any] = []

    story.append(Paragraph("Housing Market Summary", styles["Title"]))
    story.append(
        Paragraph(
            f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ·  "
            f"Dataset size: {stats.get('count', 0)} properties",
            styles["Italic"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))

    price = stats.get("price") or {}
    if price:
        story.append(Paragraph("Price ($)", styles["Heading2"]))
        price_table = Table(
            [
                ["Min", "Median", "Mean", "Max"],
                [
                    f"${price['min']:,.0f}",
                    f"${price['median']:,.0f}",
                    f"${price['mean']:,.0f}",
                    f"${price['max']:,.0f}",
                ],
            ],
            hAlign="LEFT",
        )
        price_table.setStyle(_table_style())
        story.append(price_table)
        story.append(Spacer(1, 0.4 * cm))

    features = stats.get("features") or {}
    if features:
        story.append(Paragraph("Feature summary", styles["Heading2"]))
        data = [["Feature", "Min", "Median", "Mean", "Max"]]
        for feat, summary in features.items():
            data.append(
                [
                    feat.replace("_", " "),
                    f"{summary['min']:g}",
                    f"{summary['median']:g}",
                    f"{summary['mean']:g}",
                    f"{summary['max']:g}",
                ]
            )
        feat_table = Table(data, hAlign="LEFT")
        feat_table.setStyle(_table_style())
        story.append(feat_table)
        story.append(Spacer(1, 0.4 * cm))

    bedrooms = stats.get("bedrooms") or []
    if bedrooms:
        story.append(Paragraph("Bedrooms distribution", styles["Heading2"]))
        data = [["Bedrooms", "Count"]] + [
            [str(b["value"]), str(b["count"])] for b in bedrooms
        ]
        bed_table = Table(data, hAlign="LEFT")
        bed_table.setStyle(_table_style())
        story.append(bed_table)

    doc.build(story)
    return buf.getvalue()


def _table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
    )
