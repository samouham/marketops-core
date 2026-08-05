import logging

logger = logging.getLogger("sovereign-backend")

def scan(get_client, regions):
    findings = []
    for region in regions:
        try:
            client = get_client("lambda", region_name=region)
            paginator = client.get_paginator("list_functions")
            for page in paginator.paginate():
                for fn in page.get("Functions", []):
                    fn_name = fn.get("FunctionName")
                    runtime = fn.get("Runtime", "")
                    # Check deprecated runtimes
                    if any(dep in runtime for dep in ["python3.7", "python3.8", "nodejs12", "nodejs14", "ruby2.7"]):
                        findings.append({
                            "id": "SO28-LAMBDA-DEPRECATED",
                            "domain": "Lambda",
                            "resource_id": fn_name,
                            "region": region,
                            "title": f"Lambda function {fn_name} uses deprecated runtime {runtime}.",
                            "severity": "HIGH",
                            "annual_recovery": 0.0,
                            "metadata": {"runtime": runtime}
                        })
        except Exception as e:
            logger.warning(f"Lambda scan failed in region {region}: {e}")
    return findings