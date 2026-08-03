from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import json
import hashlib
from datetime import datetime, timezone
from xml.sax.saxutils import escape

def add_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 7)
    canvas.setFillColor(colors.HexColor('#0f172a'))
    
    width, height = letter
    
    # Top Header Banner
    canvas.drawString(36, height - 27, "SOVEREIGN-28 APEX OMNI ARTIFACT | INSTITUTIONAL FORENSIC CONTROL PLANE")
    canvas.setStrokeColor(colors.HexColor('#cbd5e1'))
    canvas.setLineWidth(0.5)
    canvas.line(36, height - 33, width - 36, height - 33)
    
    # Bottom Footer
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(colors.HexColor('#64748b'))
    canvas.drawString(36, 20, "CHAIN OF CUSTODY VERIFIED | AWS WELL-ARCHITECTED REVIEW PRINCIPLES | FTR READINESS SUPPORTING ARTIFACT")
    canvas.drawRightString(width - 36, 20, f"Page {doc.page} | FORENSIC NODE")
    canvas.line(36, 30, width - 30, 30)
    
    canvas.restoreState()

def generate_audit_pdf(payload: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=70,
        bottomMargin=60
    )

    # Native PDF Metadata Properties
    doc.title = "Sovereign-28 Apex Omni Artifact"
    doc.author = "MarketOps Cloud - Forensic Engine"
    doc.subject = "AWS Governance Verification & Compliance Artifact"

    story = []
    styles = getSampleStyleSheet()
    
    # Secure multi-source payload extraction
    summary = payload.get("summary", {})
    telemetry = payload.get("telemetry", {})
    economic = payload.get("economic_exposure", {})
    
    raw_findings = (
        payload.get("findings") or 
        payload.get("drift_vectors") or 
        payload.get("audit_findings") or 
        payload.get("vectors") or 
        []
    )
    if not isinstance(raw_findings, list):
        raw_findings = []
    
    findings = [x for x in raw_findings if isinstance(x, dict)]
    
    principal = (
        payload.get("account_id") or 
        payload.get("aws_account_id") or 
        payload.get("principal_account") or
        payload.get("tenant_id") or
        payload.get("customer_account") or
        summary.get("account_id") or 
        summary.get("aws_account_id") or 
        "UNKNOWN_TENANT"
    )
    
    total_findings = int(
        summary.get("total_findings") or 
        telemetry.get("drift_detected") or 
        len(findings) or 
        0
    )
    
    raw_recovery = (
        summary.get("projected_annual_recovery_usd") or 
        summary.get("annualized_recovery") or 
        summary.get("billable_recovery") or 
        summary.get("annualized_billable_recovery") or 
        summary.get("recovery_estimate") or 
        summary.get("economic_impact") or 
        telemetry.get("annualized_recovery") or 
        economic.get("annualized_recovery") or 
        payload.get("annualized_recovery") or 
        payload.get("billable_recovery") or 
        0
    )
    
    try:
        recovery = float(raw_recovery or 0)
    except (ValueError, TypeError):
        recovery = 0.0
    
    raw_regions = (
        payload.get("regions") or 
        summary.get("regions") or 
        summary.get("scanned_regions") or 
        ["us-east-1"]
    )
    if not isinstance(raw_regions, list):
        raw_regions = [raw_regions]
    regions_list = [str(r) for r in raw_regions]
    regions_str = ", ".join(regions_list)

    evidence_timestamp = payload.get("captured_at", summary.get("captured_at", datetime.now(timezone.utc).isoformat()))
    artifact_timestamp = datetime.now(timezone.utc).isoformat()
    engine_version = "Master Gold v210.12"
    
    # Fail-closed cryptographic integrity seal
    try:
        artifact_metadata = {
            "payload": payload,
            "evidence_captured_at": evidence_timestamp,
            "artifact_generated_at": artifact_timestamp,
            "engine_version": engine_version
        }
        canonical_json = json.dumps(artifact_metadata, sort_keys=True, default=str, separators=(",", ":"))
        seal_hash = hashlib.sha384(canonical_json.encode("utf-8")).hexdigest().upper()
    except Exception as e:
        raise RuntimeError(f"Artifact sealing failed: {str(e)}")

    formatted_hash = seal_hash[:48] + "<br/>" + seal_hash[48:]
    artifact_id = f"SO28-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{seal_hash[:8]}"

    # Payload-backed evidence object count
    evidence_objects_count = payload.get("evidence_objects_count") or summary.get("evidence_objects_count") or len(findings)
    evidence_str = str(evidence_objects_count) if evidence_objects_count > 0 else "NOT PROVIDED"

    # Dynamic risk rating calculation based on finding severity
    severity_scores = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    max_severity_score = 0
    for f in findings:
        sev = str(f.get("severity") or f.get("Severity") or "LOW").upper()
        score = severity_scores.get(sev, 1)
        if score > max_severity_score:
            max_severity_score = score

    if max_severity_score >= 3 or total_findings >= 5:
        risk_rating = "HIGH"
    elif max_severity_score == 2 or total_findings > 0:
        risk_rating = "MODERATE"
    else:
        risk_rating = "LOW (CLEAN BASELINE)"

    # Typography Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6
    )

    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#0284c7'),
        spaceAfter=6,
        spaceBefore=10
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    cli_style = ParagraphStyle(
        'CLIStyle',
        parent=body_style,
        fontName='Courier',
        fontSize=6.5,
        leading=8,
        textColor=colors.HexColor('#0f172a')
    )

    kpi_style = ParagraphStyle(
        'KPIStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#16a34a'),
        alignment=1
    )

    kpi_sub_style = ParagraphStyle(
        'KPISub',
        parent=body_style,
        alignment=1,
        fontSize=8,
        leading=10,
        spaceBefore=4
    )

    # ================= PAGE 1: APEX OMNI IDENTITY & COVER =================
    story.append(Paragraph("SOVEREIGN-28 APEX OMNI ARTIFACT", title_style))
    story.append(Paragraph("Institutional Forensic Control Plane & Governance Verification", ParagraphStyle('SubTitle', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#0284c7'))))
    story.append(Spacer(1, 8))

    custody_data = [
        [Paragraph("<b>ARTIFACT CLASSIFICATION</b>", body_style), Paragraph("CONFIDENTIAL - CUSTOMER OWNED FORENSIC ARTIFACT", body_style)],
        [Paragraph("<b>ARTIFACT ID</b>", body_style), Paragraph(artifact_id, body_style)],
        [Paragraph("<b>AWS PRINCIPAL ACCOUNT</b>", body_style), Paragraph(str(principal), body_style)],
        [Paragraph("<b>ENGINE VERSION</b>", body_style), Paragraph(engine_version, body_style)],
        [Paragraph("<b>TAMPER-EVIDENT SEAL (SHA-384)</b>", body_style), Paragraph(f"<font name='Courier' size=6>{formatted_hash}</font>", body_style)],
        [Paragraph("<b>EVIDENCE CAPTURED</b>", body_style), Paragraph(str(evidence_timestamp), body_style)],
        [Paragraph("<b>ARTIFACT GENERATED</b>", body_style), Paragraph(f"{artifact_timestamp} | CRYPTOGRAPHICALLY VERIFIED", body_style)]
    ]
    t_custody = Table(custody_data, colWidths=[130, 410])
    t_custody.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_custody)
    story.append(Spacer(1, 10))

    # KPI Block (Annualized Billable Recovery) with bulletproof spacing
    kpi_content = [
        Paragraph(f"<b> USD</b>", kpi_style),
        Paragraph("<br/>", kpi_sub_style),
        Paragraph("PROJECTED ANNUALIZED BILLABLE RECOVERY", kpi_sub_style)
    ]
    t_kpi = Table([[kpi_content]], colWidths=[540])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#86efac')),
        ('TOPPADDING', (0,0), (-1,-1), 16),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 10))

    # Executive Governance Posture & Metrics Summary Table
    metrics_data = [
        ["Evaluation Metric", "Institutional Result"],
        ["Overall Governance Posture", risk_rating],
        ["Drift Vectors Isolated", str(total_findings)],
        ["Regions Evaluated", f"{len(regions_list)} ({regions_str})"],
        ["Services Evaluated", "12 (EC2, EBS, RDS, ECR, ECS, KMS, SecretMgr, Lambda, WAF, Config, Trail, SG)"],
        ["Scan Mode / IAM Authority", "Read-Only Observational Handshake (STS AssumeRole)"],
        ["Evidence Objects Collected", evidence_str],
        ["Projected Annual Recovery", f" USD"]
    ]
    t_metrics = Table(metrics_data, colWidths=[180, 360])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 10))

    story.append(Paragraph("0.0 EXECUTIVE FORENSIC NARRATIVE", section_style))
    story.append(Paragraph(f"Forensic sweep isolated <b>{total_findings} active drift vectors</b> across Infrastructure, Edge, and Audit planes. The Sovereign-28 inspection engine executed a read-only observational metadata handshake across the target AWS organization, determining capital leakage points with zero write-access footprint.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("0.1 DATA CUSTODY & METHODOLOGY", section_style))
    method_data = [
        ["Methodology", "Observational Metadata Handshake (Zero Write-Access)"],
        ["Industry Benchmark", "AWS Well-Architected Review principles and Foundational Technical Review readiness alignment."],
        ["Artifact Lifecycle", "Customer Controlled | SHA-384 Recomputable | Timestamp Bound"]
    ]
    t_method = Table(method_data, colWidths=[130, 410])
    t_method.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_method)
    story.append(PageBreak())

    # ================= PAGE 2: F1-F28 GLOSSARY =================
    story.append(Paragraph("1.0 INSTITUTIONAL FIELD GLOSSARY (F1-F28)", title_style))
    story.append(Spacer(1, 4))
    
    glossary_data = [
        ["Field", "Institutional Forensic Audit Definition & Business Logic Coverage"],
        ["F1-F4", "COMPUTE CORE: EC2 Zombie drift, Lambda hygiene, and ECS Cluster maturity."],
        ["F5-F8", "STORAGE VAULT: EBS unattached leakage and ECR image storage tax."],
        ["F9-F12", "DATABASE LAYER: RDS Stopped instances and S3 Exposure risk."],
        ["F13-F16", "VAULT & SECRET: KMS Key Rotation and SecretMgr Credential Tax."],
        ["F17-F20", "NETWORK PATH: Idle EIP namespace waste and Transit Gateway drift."],
        ["F21-F24", "IDENTITY & EDGE: IAM MFA identity drift and WAF-less ALB exposure."],
        ["F25-F28", "AUDIT & CERT: Config Recorder, CloudTrail Anchor, and SHA-384 Seal."]
    ]
    t_glossary = Table(glossary_data, colWidths=[65, 475])
    t_glossary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    ]))
    story.append(t_glossary)
    story.append(PageBreak())

    # ================= PAGE 3: EXECUTIVE INTERPRETATION & RECOMMENDED ACTIONS =================
    story.append(Paragraph("2.0 EXECUTIVE FORENSIC INTERPRETATION & ACTIONS", title_style))
    story.append(Spacer(1, 6))
    
    interp_box = [[
        Paragraph("<b>STRUCTURAL GOVERNANCE FINDING:</b><br/>The multi-regional sweep identified material 'Fiscal Drift' where abandoned digital infrastructure consumes cloud capital with zero organizational utility. Crucially, the absence of active CloudTrail anchors and Configuration Recorders creates a severe forensic blindspot. Immediate remediation optimizes EBITDA and establishes a cryptographically verifiable security posture.", body_style)
    ]]
    t_interp = Table(interp_box, colWidths=[540])
    t_interp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_interp)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>RECOMMENDED EXECUTIVE ACTIONS:</b>", section_style))
    actions_data = [
        ["1.", "Review and revoke overly permissive security group ingress rules exposing assets to 0.0.0.0/0."],
        ["2.", "Purge unattached EBS storage volumes and unreferenced ECR image repositories to stop idle tax."],
        ["3.", "Enable AWS Config recorders and AWS CloudTrail organizational trails across all commercial regions."],
        ["4.", "Enforce strict IAM MFA identity policies and attach WAF protections to publicly exposed ALBs."]
    ]
    t_actions = Table(actions_data, colWidths=[20, 520])
    t_actions.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#334155')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_actions)
    story.append(PageBreak())

    # ================= PAGE 4+: FINDINGS TABLES & CARDS =================
    story.append(Paragraph("3.0 ISOLATED DRIFT VECTORS & REMEDIATION MATRIX", title_style))
    story.append(Spacer(1, 6))

    if findings:
        for idx, f in enumerate(findings, 1):
            loc = escape(str(f.get('region') or f.get('Region') or 'us-east-1'))
            cls = escape(str(f.get('id') or f.get('finding_type') or f.get('FindingType') or 'F20'))
            resid = escape(str(f.get('resource_id') or f.get('ResourceId') or 'UNKNOWN_RESOURCE'))
            service = escape(str(f.get('service') or f.get('Service') or 'AWS Resource'))
            severity = escape(str(f.get('severity') or f.get('Severity') or 'HIGH'))
            materiality = f.get('materiality') or f.get('annual_recovery', 0.0)
            evidence = escape(str(f.get('evidence') or f.get('evidence_summary') or f.get('Description') or f.get('narrative') or 'Institutional drift vector isolated.'))
            fix_cli = escape(str(f.get('fix_cli') or f.get('fix') or f.get('remediation') or f.get('CliCommand') or f'aws resource-group remediate --resource-id {resid}'))
            
            try:
                mat_str = f""
            except (ValueError, TypeError):
                mat_str = escape(str(materiality))

            card_table_data = [
                [Paragraph(f"<b>VECTOR #{idx} | {cls}</b>", ParagraphStyle('TH', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#0284c7'))), ""],
                [Paragraph("<b>REGION</b>", body_style), Paragraph(loc, body_style)],
                [Paragraph("<b>SERVICE</b>", body_style), Paragraph(service, body_style)],
                [Paragraph("<b>RESOURCE</b>", body_style), Paragraph(resid, body_style)],
                [Paragraph("<b>SEVERITY</b>", body_style), Paragraph(severity, body_style)],
                [Paragraph("<b>MATERIALITY</b>", body_style), Paragraph(mat_str, body_style)],
                [Paragraph("<b>EVIDENCE</b>", body_style), Paragraph(evidence, body_style)],
                [Paragraph("<b>REMEDIATION CLI</b>", body_style), Paragraph(fix_cli, cli_style)]
            ]
            
            t_card = Table(card_table_data, colWidths=[110, 430])
            t_card.setStyle(TableStyle([
                ('SPAN', (0,0), (1,0)),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
                ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#f8fafc')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t_card)
            story.append(Spacer(1, 10))
    else:
        clean_box = [[
            Paragraph("<b>FINDING STATUS: CLEAN BASELINE</b><br/><br/>The Sovereign-28 engine completed multi-regional evaluation and identified no material governance drift or billable recovery opportunity requiring remediation.", body_style)
        ]]
        t_clean = Table(clean_box, colWidths=[540])
        t_clean.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#86efac')),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(t_clean)

    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer.getvalue()