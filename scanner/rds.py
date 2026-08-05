import logging
from datetime import datetime

logger = logging.getLogger("sovereign-backend")

def scan(get_client, regions):
    findings = []
    for region in regions:
        try:
            client = get_client("rds", region_name=region)
            paginator = client.get_paginator("describe_db_instances")
            for page in paginator.paginate():
                for db in page.get("DBInstances", []):
                    db_id = db.get("DBInstanceIdentifier")
                    publicly_accessible = db.get("PubliclyAccessible", False)
                    storage_encrypted = db.get("StorageEncrypted", False)
                    
                    if publicly_accessible:
                        findings.append({
                            "id": "SO28-RDS-PUBLIC",
                            "domain": "RDS",
                            "resource_id": db_id,
                            "region": region,
                            "title": f"RDS Database instance {db_id} is publicly accessible.",
                            "severity": "CRITICAL",
                            "annual_recovery": 0.0,
                            "metadata": {"engine": db.get("Engine"), "publicly_accessible": True}
                        })
                    if not storage_encrypted:
                        findings.append({
                            "id": "SO28-RDS-UNENCRYPTED",
                            "domain": "RDS",
                            "resource_id": db_id,
                            "region": region,
                            "title": f"RDS Database instance {db_id} storage is unencrypted.",
                            "severity": "HIGH",
                            "annual_recovery": 0.0,
                            "metadata": {"engine": db.get("Engine"), "encrypted": False}
                        })
        except Exception as e:
            logger.warning(f"RDS scan failed in region {region}: {e}")
    return findings