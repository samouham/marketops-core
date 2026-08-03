from engine import sts_client

def test_aws_connection():
    print("Initiating test call to AWS STS...")
    try:
        response = sts_client.get_caller_identity()
        print("\n--- Success! API Call Executed ---")
        print(f"AWS Account ID : {response.get('Account')}")
        print(f"IAM User/Role ARN: {response.get('Arn')}")
        print(f"User ID        : {response.get('UserId')}")
        print("\nYour boto3 client is communicating with AWS successfully.")
    except Exception as e:
        print(f"\n[Error] API call failed: {e}")

if __name__ == "__main__":
    test_aws_connection()