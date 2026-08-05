import logging

logger = logging.getLogger("sovereign-backend")

def scan(get_client, regions):
    findings = []
    for region in regions:
        try:
            client = get_client("wafv2", region_name=region)
            for scope in ["REGIONAL"]:
                web_acls = client.list_web_acls(Scope=scope).get("WebACLs", [])
                if not web_acls:
                    findings.append({
                        "id": "SO28-WAF-MISSING",
                        "domain": "WAF",
                        "resource_id": f"WAF-SCOPE-{region}",
                        "region": region,
                        "title": f"No WAF Web ACLs configured in region {region}.",
                        "severity": "LOW",
                        "annual_recovery": 0.0,
                        "metadata": {"scope": scope}
                    })
        except Exception as e:
            logger.warning(f"WAF scan failed in region {region}: {e}")
    return findings