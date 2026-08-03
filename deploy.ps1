$ErrorActionPreference = "Stop"

try {
    $AWS_REGION = "us-east-1"
    $ACCOUNT_ID = "778367658348"
    $REPO_NAME = "sovereign-28-repo"
    $SERVICE_ARN = "arn:aws:apprunner:${AWS_REGION}:${ACCOUNT_ID}:service/sovereign-backend-engine-v2/053bae45e3a34dab94314eb76260a600"

    $TIMESTAMP = (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
    $VERSION_TAG = "v210.12-$TIMESTAMP"
    $IMAGE_URI = "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}:${VERSION_TAG}"

    Write-Host "[*] Starting Sovereign-28 Deployment Pipeline..." -ForegroundColor Cyan
    Write-Host "[*] Target Immutable Image Tag: $VERSION_TAG" -ForegroundColor Yellow

    # 1. Authenticate Docker with ECR
    Write-Host "[*] Authenticating with Amazon ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

    # 2. Build Docker Image
    Write-Host "[*] Building Docker image locally..."
    docker build -t "${REPO_NAME}:${VERSION_TAG}" .

    # 3. Verification Gate
    $localImageCheck = docker images -q "${REPO_NAME}:${VERSION_TAG}"
    if (-not $localImageCheck) {
        throw "Docker build failed. Local image not found."
    }
    Write-Host "[+] Local image build verified successfully." -ForegroundColor Green

    # 4. Tag Image for ECR
    Write-Host "[*] Tagging image for ECR repository..."
    docker tag "${REPO_NAME}:${VERSION_TAG}" "$IMAGE_URI"

    # 5. Push Image to ECR
    Write-Host "[*] Pushing container image to ECR..."
    docker push "$IMAGE_URI"

    # 6. Trigger App Runner Deployment using a clean JSON config object
    Write-Host "[*] Initiating App Runner deployment for service..."
    
    $sourceConfig = @{
        ImageRepository = @{
            ImageIdentifier = $IMAGE_URI
            ImageConfiguration = @{
                Port = "8000"
                RuntimeEnvironmentVariables = @{
                    PRODUCT_CODE = "cn6syebtx54abh7pwtgwj5o8w"
                }
            }
            ImageRepositoryType = "ECR"
        }
    } | ConvertTo-Json -Depth 5

    aws apprunner update-service --service-arn $SERVICE_ARN --source-configuration "$sourceConfig"

    Write-Host "[+] Deployment triggered successfully. Monitoring service status..." -ForegroundColor Green

    # 7. Poll App Runner status safely
    while ($true) {
        Start-Sleep -Seconds 10
        $serviceJson = aws apprunner describe-service --service-arn $SERVICE_ARN
        $serviceDetails = $serviceJson | ConvertFrom-Json
        $status = $serviceDetails.Service.Status
        $operationStatus = $serviceDetails.Service.OperationStatus
        
        Write-Host "[*] Service Status: $status | Operation Status: $operationStatus" -ForegroundColor Yellow
        
        if ($status -eq "RUNNING" -and $operationStatus -eq "SUCCEEDED") {
            Write-Host "[+] SUCCESS: Sovereign-28 engine is running the new container revision!" -ForegroundColor Green
            break
        }
        elseif ($operationStatus -eq "FAILED") {
            throw "App Runner operation failed on AWS side. Check CloudWatch logs."
        }
    }
}
catch {
    Write-Error "[!] Deployment Pipeline Failed: $_"
    exit 1
}