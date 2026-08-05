import logging

logger = logging.getLogger("sovereign-backend")

def scan(get_client, regions):
    findings = []
    for region in regions:
        try:
            client = get_client("cloudtrail", region_name=region)
            trails = client.describe_trails(includeShadowTrails=False).get("trailList", [])
            if not trails:
                findings.append({
                    "id": "SO28-TRAIL-MISSING",
                    "domain": "CloudTrail",
                    "resource_id": f"CLOUDTRAIL-{region}",
                    "region": region,
                    "title": f"No CloudTrail trail configured in region {region}.",
                    "severity": "HIGH",
                    "annual_recovery": 0.0,
                    "metadata": {"region": region}
                })
        except Exception as e:
            logger.warning(f"CloudTrail scan failed in region {region}: {e}")
    return findings