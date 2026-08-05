import logging

logger = logging.getLogger("sovereign-backend")

def scan(get_client, regions):
    findings = []
    for region in regions:
        try:
            client = get_client("ecs", region_name=region)
            clusters = client.list_clusters().get("clusterArns", [])
            if clusters:
                desc = client.describe_clusters(clusters=clusters)
                for cluster in desc.get("clusters", []):
                    c_name = cluster.get("clusterName")
                    active_services = cluster.get("activeServicesCount", 0)
                    if active_services == 0:
                        findings.append({
                            "id": "SO28-ECS-IDLE",
                            "domain": "ECS",
                            "resource_id": c_name,
                            "region": region,
                            "title": f"ECS Cluster {c_name} has zero active services.",
                            "severity": "LOW",
                            "annual_recovery": 150.0,
                            "metadata": {"status": cluster.get("status")}
                        })
        except Exception as e:
            logger.warning(f"ECS scan failed in region {region}: {e}")
    return findings