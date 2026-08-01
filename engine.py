import boto3
from botocore.config import Config

# Safe append pattern for AWS Partner Revenue Measurement
prm_config = Config(
    user_agent_extra="APN_1.1/pc_cn6syebtx54abh7pwtgwj5o8w$"
)

# Core AWS clients utilizing your PRM partner attribution
ec2_client = boto3.client('ec2', config=prm_config)
s3_client = boto3.client('s3', config=prm_config)
iam_client = boto3.client('iam', config=prm_config)
sts_client = boto3.client('sts', config=prm_config)