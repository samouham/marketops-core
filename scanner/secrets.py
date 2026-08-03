from findings import Finding

def scan(session_client_factory, regions):
    """
    Scans Secrets Manager for potential risks or untagged secrets (F14).
    """
    findings = []
    
    for region in regions:
        print(f"[Secrets] Scanning region: {region}...")
        secrets_client = session_client_factory("secretsmanager", region_name=region)
        try:
            paginator = secrets_client.get_paginator('list_secrets')
            for page in paginator.paginate():
                for secret in page.get('SecretList', []):
                    secret_arn = secret['ARN']
                    secret_name = secret['Name']
                    
                    if secret.get('DeletedDate') is not None:
                        continue
                        
                    findings.append(Finding(
                        id="F14",
                        severity="High",
                        resource="Secrets Manager Secret",
                        resource_id=secret_name,
                        region=region,
                        annual_recovery=4.80,
                        classification="SECURITY",
                        description=f"Active secret managed in Secrets Manager: {secret_arn}",
                        cli_remediation=f"aws secretsmanager describe-secret --secret-id {secret_arn} --region {region}"
                    ))
        except Exception as e:
            print(f"[Notice] Secrets Manager scan skipped or unavailable in {region}: {e}")
            
    return findings