import logging

logger = logging.getLogger("sovereign-backend")

def scan(get_client, regions):
    findings = []
    for region in regions:
        try:
            client = get_client("ecr", region_name=region)
            paginator = client.get_paginator("describe_repositories")
            for page in paginator.paginate():
                for repo in page.get("repositories", []):
                    repo_name = repo.get("repositoryName")
                    # Check image scanning on push configuration
                    try:
                        scan_config = client.get_repository_policy(repositoryName=repo_name)
                    except Exception:
                        findings.append({
                            "id": "SO28-ECR-POLICY",
                            "domain": "ECR",
                            "resource_id": repo_name,
                            "region": region,
                            "title": f"ECR Repository {repo_name} lacks a repository policy or strict access controls.",
                            "severity": "MEDIUM",
                            "annual_recovery": 0.0,
                            "metadata": {"repository_uri": repo.get("repositoryUri")}
                        })
        except Exception as e:
            logger.warning(f"ECR scan failed in region {region}: {e}")
    return findings