from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

def generate_audit_pdf(payload: dict) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=12
    )

    story.append(
        Paragraph(
            "Sovereign-28 Institutional Audit Report",
            title_style
        )
    )

    story.append(Spacer(1, 12))

    telemetry = payload.get("telemetry", {})

    story.append(
        Paragraph(
            "Scan Status: COMPLETE",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"Detected Drift: {telemetry.get('drift_detected', 0)}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"Annualized Recovery: \ USD",
            styles["Normal"]
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
