import logging

logger = logging.getLogger("sovereign-backend")

def create_finding(domain, resource_id, region, title, severity, recovery=0.0, metadata=None):
    return {
        "id": f"SO28-{domain.upper()}-001",
        "domain": domain,
        "resource_id": resource_id,
        "region": region,
        "title": title,
        "severity": severity,
        "annual_recovery": recovery,
        "metadata": metadata or {}
    }