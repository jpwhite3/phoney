#!/bin/bash

# Phoney AWS Serverless Deployment Script
# Usage: ./deploy.sh [dev|staging|prod] [--skip-tests] [--force]

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
STAGE="${1:-dev}"
SKIP_TESTS="${2:-false}"
FORCE="${3:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate stage
if [[ ! "$STAGE" =~ ^(dev|staging|prod)$ ]]; then
    log_error "Invalid stage: $STAGE. Must be one of: dev, staging, prod"
    exit 1
fi

log_info "Starting deployment for stage: $STAGE"

# Check required environment variables
required_vars=(
    "AWS_ACCOUNT_ID"
    "AWS_DEFAULT_REGION"
)

for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        log_error "Required environment variable $var is not set"
        exit 1
    fi
done

# Set stage-specific variables
case $STAGE in
    "prod")
        MEMORY_SIZE=1024
        TIMEOUT=30
        CONCURRENT_EXECUTIONS=1000
        ;;
    "staging")
        MEMORY_SIZE=512
        TIMEOUT=30
        CONCURRENT_EXECUTIONS=500
        ;;
    "dev")
        MEMORY_SIZE=256
        TIMEOUT=15
        CONCURRENT_EXECUTIONS=100
        ;;
esac

log_info "Configuration: Memory=$MEMORY_SIZE MB, Timeout=$TIMEOUT s, Concurrent=$CONCURRENT_EXECUTIONS"

# Change to project root
cd "$PROJECT_ROOT"

# Step 1: Run tests (unless skipped)
if [[ "$SKIP_TESTS" != "--skip-tests" ]]; then
    log_info "Running tests..."
    if command -v poetry &> /dev/null; then
        poetry run pytest tests/ -v --tb=short
    else
        python -m pytest tests/ -v --tb=short
    fi
    log_success "Tests passed"
else
    log_warning "Skipping tests"
fi

# Step 2: Prepare Docker build context
log_info "Preparing Docker build context..."
mkdir -p aws-infrastructure/docker/phoney
cp -r phoney/ aws-infrastructure/docker/
cp aws-infrastructure/docker/requirements.txt aws-infrastructure/docker/

# Step 3: Build and push Docker image
log_info "Building and pushing Docker image..."

# Get ECR repository URI
ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/phoney-${STAGE}"
IMAGE_TAG="$(date +%Y%m%d-%H%M%S)-$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"

# Login to ECR
log_info "Logging into ECR..."
aws ecr get-login-password --region "$AWS_DEFAULT_REGION" | \
    docker login --username AWS --password-stdin "$ECR_REPO"

# Build image
log_info "Building Docker image..."
cd aws-infrastructure/docker
docker build \
    --platform linux/amd64 \
    -t "phoney:$IMAGE_TAG" \
    -t "phoney:latest" \
    --build-arg STAGE="$STAGE" \
    .

# Tag for ECR
docker tag "phoney:$IMAGE_TAG" "$ECR_REPO:$IMAGE_TAG"
docker tag "phoney:latest" "$ECR_REPO:latest"

# Push to ECR
log_info "Pushing Docker image to ECR..."
docker push "$ECR_REPO:$IMAGE_TAG"
docker push "$ECR_REPO:latest"

log_success "Docker image pushed: $ECR_REPO:$IMAGE_TAG"

# Step 4: Deploy infrastructure with CDK
log_info "Deploying infrastructure with CDK..."
cd "$PROJECT_ROOT/aws-infrastructure/cdk"

# Install CDK dependencies if needed
if [[ ! -d node_modules ]]; then
    log_info "Installing CDK dependencies..."
    npm install
fi

# Bootstrap CDK if needed (for first deployment)
if [[ "$FORCE" == "--force" ]] || [[ ! -f ".cdk-bootstrapped-$STAGE" ]]; then
    log_info "Bootstrapping CDK..."
    npx cdk bootstrap "aws://$AWS_ACCOUNT_ID/$AWS_DEFAULT_REGION"
    touch ".cdk-bootstrapped-$STAGE"
fi

# Set environment variables for CDK
export STAGE="$STAGE"
export IMAGE_TAG="$IMAGE_TAG"

# Deploy the stack
log_info "Deploying CDK stack: PhoneyStack-$STAGE"
npx cdk deploy "PhoneyStack-$STAGE" \
    --require-approval never \
    --context "stage=$STAGE" \
    --context "imageTag=$IMAGE_TAG" \
    --outputs-file "outputs-$STAGE.json"

# Step 5: Update Lambda function with new image
log_info "Updating Lambda function with new image..."
FUNCTION_NAME="phoney-$STAGE"

aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --image-uri "$ECR_REPO:$IMAGE_TAG" \
    --region "$AWS_DEFAULT_REGION"

# Wait for function to be updated
log_info "Waiting for Lambda function to be updated..."
aws lambda wait function-updated \
    --function-name "$FUNCTION_NAME" \
    --region "$AWS_DEFAULT_REGION"

# Step 6: Run smoke tests
log_info "Running smoke tests..."
if [[ -f "outputs-$STAGE.json" ]]; then
    API_URL=$(cat "outputs-$STAGE.json" | jq -r '.["PhoneyStack-'$STAGE'"].ApiUrl' 2>/dev/null || echo "")
    
    if [[ -n "$API_URL" && "$API_URL" != "null" ]]; then
        log_info "Testing API endpoint: $API_URL"
        
        # Test health endpoint
        if curl -s --fail --connect-timeout 10 --max-time 30 "$API_URL" > /dev/null; then
            log_success "API health check passed"
        else
            log_warning "API health check failed, but deployment may still be successful"
        fi
        
        # Test template endpoint
        if curl -s --fail --connect-timeout 10 --max-time 30 \
            -H "Content-Type: application/json" \
            -d '{"template":{"name":"{{name}}"},"count":1}' \
            "$API_URL/template" > /dev/null; then
            log_success "Template API test passed"
        else
            log_warning "Template API test failed"
        fi
    else
        log_warning "Could not extract API URL from CDK outputs"
    fi
fi

# Step 7: Clean up Docker images (keep last 5)
log_info "Cleaning up old Docker images..."
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | \
    grep "phoney" | \
    tail -n +6 | \
    awk '{print $1}' | \
    xargs -r docker rmi 2>/dev/null || true

# Step 8: Display deployment summary
log_success "Deployment completed successfully!"
echo
echo "==================================="
echo "Deployment Summary"
echo "==================================="
echo "Stage: $STAGE"
echo "Image: $ECR_REPO:$IMAGE_TAG"
echo "Function: $FUNCTION_NAME"
if [[ -n "$API_URL" ]]; then
    echo "API URL: $API_URL"
fi
echo "Region: $AWS_DEFAULT_REGION"
echo "Timestamp: $(date)"
echo "==================================="

# Save deployment info
cat > "deployment-info-$STAGE.json" << EOF
{
    "stage": "$STAGE",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "image_tag": "$IMAGE_TAG",
    "ecr_repo": "$ECR_REPO",
    "function_name": "$FUNCTION_NAME",
    "api_url": "$API_URL",
    "region": "$AWS_DEFAULT_REGION",
    "memory_size": $MEMORY_SIZE,
    "timeout": $TIMEOUT,
    "concurrent_executions": $CONCURRENT_EXECUTIONS
}
EOF

log_success "Deployment information saved to deployment-info-$STAGE.json"

# Return to original directory
cd "$PROJECT_ROOT"

log_info "🚀 Phoney serverless deployment completed successfully!"

# Optional: Display next steps
echo
echo "Next steps:"
echo "1. Test the API: curl $API_URL"
echo "2. Monitor logs: aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
echo "3. View metrics: aws lambda get-function --function-name $FUNCTION_NAME"
echo "4. Update DNS if using custom domain"