import logging

logger = logging.getLogger("sovereign-backend")

def scan(get_client, regions):
    findings = []
    for region in regions:
        try:
            client = get_client("ec2", region_name=region)
            paginator = client.get_paginator("describe_security_groups")
            for page in paginator.paginate():
                for sg in page.get("SecurityGroups", []):
                    sg_id = sg.get("GroupId")
                    sg_name = sg.get("GroupName")
                    for perm in sg.get("IpPermissions", []):
                        from_port = perm.get("FromPort", 0)
                        to_port = perm.get("ToPort", 65535)
                        for ip_range in perm.get("IpRanges", []):
                            if ip_range.get("CidrIp") == "0.0.0.0/0":
                                if from_port in [22, 3389] or from_port == 0:
                                    findings.append({
                                        "id": "SO28-SG-UNRESTRICTED",
                                        "domain": "SecurityGroups",
                                        "resource_id": sg_id,
                                        "region": region,
                                        "title": f"Security Group {sg_name} ({sg_id}) exposes sensitive port {from_port} to 0.0.0.0/0.",
                                        "severity": "CRITICAL",
                                        "annual_recovery": 0.0,
                                        "metadata": {"group_name": sg_name, "port": from_port}
                                    })
        except Exception as e:
            logger.warning(f"Security Groups scan failed in region {region}: {e}")
    return findings