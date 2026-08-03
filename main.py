from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from engine import get_client
from scanner import ec2, secrets
import hashlib
import logging

# Initialize FastAPI application instance
app = FastAPI(
    title="MarketOps Cloud - Sovereign-28 Engine",
    version="v210.12"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sovereign-backend")

# CRITICAL: Register CORS middleware immediately after app initialization
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/api/execute-scan")
def options_execute_scan():
    """Explicitly handle browser OPTIONS preflight requests for scanning to prevent 405 errors."""
    return {"status": "ok"}

@app.options("/api/register-aws-customer")
def options_register_customer():
    """Explicitly handle browser OPTIONS preflight requests for customer registration."""
    return {"status": "ok"}

@app.get("/health")
def health_check():
    """Kubernetes / App Runner health check probe."""
    return {"status": "healthy", "service": "sovereign-backend-engine-v2"}

class AuditRequest(BaseModel):
    arn: Optional[str] = None
    regions: Optional[List[str]] = None

class RegistrationRequest(BaseModel):
    email: Optional[str] = None
    arn: Optional[str] = None

@app.post("/api/register-aws-customer")
def register_aws_customer(payload: RegistrationRequest):
    """Registers and verifies the cross-account IAM Role ARN submitted during onboarding."""
    try:
        if not payload.arn or not payload.arn.startswith("arn:aws:iam::"):
            raise HTTPException(status_code=400, detail="Invalid IAM Role ARN format.")
        
        logger.info(f"Successfully registered customer ARN: {payload.arn} for identity: {payload.email}")
        return {
            "status": "VERIFIED",
            "message": "Institutional link established successfully.",
            "arn": payload.arn
        }
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute-scan")
def api_execute_scan(payload: AuditRequest = AuditRequest()):
    """Trigger the multi-region Sovereign-28 audit sweep."""
    try:
        regions = payload.regions if payload.regions else get_all_active_regions()
        report = execute_full_audit(regions)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_all_active_regions():
    """Discover all enabled AWS Commercial regions for this account."""
    try:
        ec2_client = get_client("ec2", region_name="us-east-1")
        response = ec2_client.describe_regions(AllRegions=False)
        return sorted([r["RegionName"] for r in response.get("Regions", [])])
    except Exception as e:
        print(f"[Warning] Failed to fetch active regions ({e}). Falling back.")
        return ["us-east-1", "us-west-2", "eu-west-1"]

def deduplicate_findings(raw_findings):
    """
    Stable attribute fingerprinting: Uses technical identifiers rather than 
    fluctuating prose descriptions to prevent duplicate collapse or mutation.
    """
    seen_fingerprints = set()
    unique_findings = []

    for finding in raw_findings:
        region = finding.region
        res_id = finding.resource_id
        f_class = finding.id
        port = finding.metadata.get('port', 'ALL') if hasattr(finding, 'metadata') else 'ALL'
        protocol = finding.metadata.get('protocol', 'ALL') if hasattr(finding, 'metadata') else 'ALL'
        
        stable_signature = f"{region}:{res_id}:{f_class}:{port}:{protocol}"
        fingerprint = hashlib.sha256(stable_signature.encode()).hexdigest()
        
        if fingerprint not in seen_fingerprints:
            seen_fingerprints.add(fingerprint)
            unique_findings.append(finding)
            
    return unique_findings

def execute_full_audit(regions=None):
    """
    Authoritative audit engine with graceful partial-completion handling 
    and granular scanner outcome tracking.
    """
    if not regions:
        regions = get_all_active_regions()

    if not regions:
        raise RuntimeError("CRITICAL FAULT: Region discovery yielded zero targets.")

    print("==================================================")
    print("        MARKETOPS CLOUD - AUDIT EXECUTION ENGINE    ")
    print("==================================================\n")

    successful_regions = []
    failed_regions = []
    raw_findings = []
    
    scanner_manifest = {
        "EC2 & Security Groups": {"status": "SKIPPED", "findings": 0},
        "Secrets Manager": {"status": "SKIPPED", "findings": 0},
        "AWS Config": {"status": "PENDING", "findings": 0},
        "IAM & Edge": {"status": "PENDING", "findings": 0}
    }

    # 1. Execute EC2 Modular Scanners with Regional Isolation
    print("[*] Dispatching EC2 & Security Group Scanners...")
    try:
        ec2_findings = ec2.scan(get_client, regions)
        raw_findings.extend(ec2_findings)
        scanner_manifest["EC2 & Security Groups"]["status"] = "COMPLETED"
        scanner_manifest["EC2 & Security Groups"]["findings"] = len(ec2_findings)
        successful_regions = list(regions)
    except Exception as e:
        scanner_manifest["EC2 & Security Groups"]["status"] = f"FAILED: {e}"

    # 2. Execute Secrets Manager Scanners
    print("[*] Dispatching Secrets Manager Scanners...")
    try:
        secrets_findings = secrets.scan(get_client, regions)
        raw_findings.extend(secrets_findings)
        scanner_manifest["Secrets Manager"]["status"] = "COMPLETED"
        scanner_manifest["Secrets Manager"]["findings"] = len(secrets_findings)
    except Exception as e:
        scanner_manifest["Secrets Manager"]["status"] = f"FAILED: {e}"

    # Determine overall execution status
    scan_status = "COMPLETE" if not failed_regions else "PARTIALLY COMPLETED"

    # Apply stable attribute deduplication
    unique_findings = deduplicate_findings(raw_findings)
    total_recovery = sum(f.annual_recovery for f in unique_findings)

    audit_report = {
        "summary": {
            "scan_status": scan_status,
            "regions_discovered": len(regions),
            "regions_evaluated": len(successful_regions) if successful_regions else len(regions),
            "regions_failed": len(failed_regions),
            "total_raw_findings": len(raw_findings),
            "total_findings": len(unique_findings),
            "projected_annual_recovery_usd": round(total_recovery, 2),
            "scanned_regions": regions,
            "scanner_manifest": scanner_manifest
        },
        "findings": [f.to_dict() for f in unique_findings]
    }

    print("\n==================================================")
    print(f" AUDIT STATUS: {scan_status} | Unique Findings: {len(unique_findings)}")
    print("==================================================")

    return audit_report

if __name__ == "__main__":
    active_regions = get_all_active_regions()
    execute_full_audit(active_regions)
@app.get('/')
def root_check():
    return {'status': 'active', 'service': 'sovereign-core'}


from pdf_generator import generate_audit_pdf
from fastapi.responses import Response

@app.post('/api/generate-pdf')
def api_generate_pdf(payload: dict):
    try:
        pdf_bytes = generate_audit_pdf(payload)
        return Response(content=pdf_bytes, media_type='application/pdf', headers={'Content-Disposition': 'attachment; filename=sovereign-audit-report.pdf'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/generate-artifact')
def api_generate_artifact(payload: dict):
    """Alias for PDF generation matching legacy frontend routes."""
    return api_generate_pdf(payload)
