"""
CSV + PDF exporters. Kept dumb on purpose — they render whatever rows you pass.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------- Font registration ----------------------------
#
# reportlab's built-in Type 1 Helvetica does not include the Indian Rupee sign
# (U+20B9). We register DejaVuSans at module import so ₹ renders crisply in
# the PDF. On systems where the font is missing (some dev laptops), we fall
# back to plain "Rs." text with the default Helvetica so exports still work.

_RUPEE_UNICODE = "\u20B9"  # ₹
_PDF_FONT_REGULAR = "Helvetica"
_PDF_FONT_BOLD = "Helvetica-Bold"
_PDF_PRICE_PREFIX = "Rs. "  # replaced below if a Unicode font registers OK


def _register_unicode_font() -> None:
    """Register DejaVuSans if we can find it, so ₹ renders in the PDF."""
    global _PDF_FONT_REGULAR, _PDF_FONT_BOLD, _PDF_PRICE_PREFIX
    candidates = [
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
        (
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        ),
    ]
    for regular, bold in candidates:
        if Path(regular).exists() and Path(bold).exists():
            try:
                pdfmetrics.registerFont(TTFont("DejaVuSans", regular))
                pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold))
            except Exception:
                return
            _PDF_FONT_REGULAR = "DejaVuSans"
            _PDF_FONT_BOLD = "DejaVuSans-Bold"
            _PDF_PRICE_PREFIX = _RUPEE_UNICODE
            return


_register_unicode_font()


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
    # Swap the built-in fonts for the Unicode-capable one (DejaVuSans) when
    # available; otherwise keep Helvetica and lean on the "Rs." fallback.
    for style_name in ("Title", "Heading1", "Heading2", "Normal", "Italic"):
        styles[style_name].fontName = (
            _PDF_FONT_BOLD if "Heading" in style_name or style_name == "Title"
            else _PDF_FONT_REGULAR
        )
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
        story.append(
            Paragraph(f"Price ({_PDF_PRICE_PREFIX.strip()})", styles["Heading2"])
        )
        price_table = Table(
            [
                ["Min", "Median", "Mean", "Max"],
                [
                    f"{_PDF_PRICE_PREFIX}{price['min']:,.0f}",
                    f"{_PDF_PRICE_PREFIX}{price['median']:,.0f}",
                    f"{_PDF_PRICE_PREFIX}{price['mean']:,.0f}",
                    f"{_PDF_PRICE_PREFIX}{price['max']:,.0f}",
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
            ("FONTNAME", (0, 0), (-1, 0), _PDF_FONT_BOLD),
            ("FONTNAME", (0, 1), (-1, -1), _PDF_FONT_REGULAR),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
    )
