import logging

logger = logging.getLogger("sovereign-backend")

def scan(get_client, regions):
    findings = []
    for region in regions:
        try:
            client = get_client("kms", region_name=region)
            paginator = client.get_paginator("list_keys")
            for page in paginator.paginate():
                for key in page.get("Keys", []):
                    key_id = key.get("KeyId")
                    try:
                        rot = client.get_key_rotation_status(KeyId=key_id)
                        if not rot.get("KeyRotationEnabled", False):
                            findings.append({
                                "id": "SO28-KMS-ROTATION",
                                "domain": "KMS",
                                "resource_id": key_id,
                                "region": region,
                                "title": f"KMS Customer Managed Key {key_id} has automatic rotation disabled.",
                                "severity": "MEDIUM",
                                "annual_recovery": 0.0,
                                "metadata": {"key_arn": key.get("KeyArn")}
                            })
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"KMS scan failed in region {region}: {e}")
    return findings