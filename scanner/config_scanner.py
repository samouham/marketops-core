import logging

logger = logging.getLogger("sovereign-backend")

def scan(get_client, regions):
    findings = []
    for region in regions:
        try:
            client = get_client("config", region_name=region)
            recorders = client.describe_configuration_recorders().get("ConfigurationRecorders", [])
            if not recorders:
                findings.append({
                    "id": "SO28-CONFIG-RECORDER",
                    "domain": "Config",
                    "resource_id": f"CONFIG-RECORDER-{region}",
                    "region": region,
                    "title": f"AWS Config recorder is not enabled in region {region}.",
                    "severity": "MEDIUM",
                    "annual_recovery": 0.0,
                    "metadata": {"region": region}
                })
        except Exception as e:
            logger.warning(f"Config scan failed in region {region}: {e}")
    return findings