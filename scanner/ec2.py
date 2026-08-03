from findings import Finding

def scan(session_client_factory, regions):
    """
    Scans for F5 (Unattached EBS volumes), F17 (Unassociated Elastic IPs),
    and F20 (Security Groups with public ingress).
    """
    findings = []
    
    for region in regions:
        print(f"[EC2] Scanning region: {region}...")
        ec2 = session_client_factory("ec2", region_name=region)
        
        # 1. Check F5: Unattached EBS Volumes
        try:
            volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
            for vol in volumes.get('Volumes', []):
                vol_id = vol['VolumeId']
                size_gb = vol['Size']
                monthly_cost = size_gb * 0.08
                annual_recovery = round(monthly_cost * 12, 2)
                
                findings.append(Finding(
                    id="F5",
                    severity="Medium",
                    resource="EBS Volume",
                    resource_id=vol_id,
                    region=region,
                    annual_recovery=annual_recovery,
                    classification="BILLABLE",
                    description=f"Unattached EBS volume {vol_id} ({size_gb} GB) sitting idle.",
                    cli_remediation=f"aws ec2 delete-volume --volume-id {vol_id} --region {region}"
                ))
        except Exception as e:
            print(f"[Error] EC2 volume scan failed in {region}: {e}")

        # 2. Check F17: Unassociated Elastic IPs
        try:
            addresses = ec2.describe_addresses(Filters=[{'Name': 'domain', 'Values': ['vpc']}])
            for addr in addresses.get('Addresses', []):
                if 'AssociationId' not in addr and 'InstanceId' not in addr:
                    allocation_id = addr.get('AllocationId', 'Unknown')
                    annual_recovery = 43.20
                    
                    findings.append(Finding(
                        id="F17",
                        severity="Low",
                        resource="Elastic IP",
                        resource_id=allocation_id,
                        region=region,
                        annual_recovery=annual_recovery,
                        classification="BILLABLE",
                        description=f"Unassociated Elastic IP {allocation_id} incurring hourly charges.",
                        cli_remediation=f"aws ec2 release-address --allocation-id {allocation_id} --region {region}"
                    ))
        except Exception as e:
            print(f"[Error] EIP scan failed in {region}: {e}")

        # 3. Check F20: Security Groups with public ingress (0.0.0.0/0)
        try:
            sgs = ec2.describe_security_groups()
            for sg in sgs.get('SecurityGroups', []):
                group_id = sg['GroupId']
                for perm in sg.get('IpPermissions', []):
                    for ip_range in perm.get('IpRanges', []):
                        if ip_range.get('CidrIp') == '0.0.0.0/0':
                            from_port = perm.get('FromPort', 0)
                            to_port = perm.get('ToPort', 65535)
                            
                            # Calibrate risk level based on port
                            critical_ports = [22, 3389, 3306, 5432, 1433, 27017]
                            if any(p in range(from_port, to_port + 1) for p in critical_ports):
                                severity = "Critical"
                                desc = f"High-risk admin/database port range ({from_port}-{to_port}) exposed globally (0.0.0.0/0) on Security Group {group_id}."
                            else:
                                severity = "High"
                                desc = f"Broad network ingress open to 0.0.0.0/0 on port range ({from_port}-{to_port}) on Security Group {group_id}."

                            findings.append(Finding(
                                id="F20",
                                severity=severity,
                                resource="Security Group",
                                resource_id=group_id,
                                region=region,
                                annual_recovery=0.00,
                                classification="SECURITY",
                                description=desc,
                                cli_remediation=f"aws ec2 revoke-security-group-ingress --group-id {group_id} --protocol {perm.get('IpProtocol', 'tcp')} --port {from_port}"
                            ))
        except Exception as e:
            print(f"[Error] Security Group scan failed in {region}: {e}")

    return findings