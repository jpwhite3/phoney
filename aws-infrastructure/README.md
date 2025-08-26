# 🚀 Phoney AWS Serverless Infrastructure

This directory contains all the infrastructure-as-code and deployment automation for deploying the Phoney Template API to AWS serverless architecture.

## 📁 Directory Structure

```
aws-infrastructure/
├── cdk/                          # AWS CDK infrastructure code
│   ├── lib/phoney-stack.ts       # Main CDK stack definition
│   ├── bin/app.ts                # CDK application entry point
│   ├── package.json              # Node.js dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   └── cdk.json                  # CDK configuration
├── docker/                       # Lambda container configuration
│   ├── Dockerfile                # Container image definition
│   ├── requirements.txt          # Python dependencies for Lambda
│   └── lambda_handler.py         # Lambda handler with Mangum
├── scripts/                      # Deployment automation scripts
│   └── deploy.sh                 # Main deployment script
├── monitoring/                   # Observability configuration
│   ├── cloudwatch-dashboard.json # CloudWatch dashboard
│   ├── alarms.tf                 # CloudWatch alarms (Terraform)
│   └── log-insights-queries.txt  # Useful log queries
└── README.md                     # This file
```

## 🏗️ Architecture Overview

The serverless deployment uses:
- **AWS Lambda**: Container-based Python runtime with Mangum ASGI adapter
- **API Gateway HTTP API**: RESTful API endpoint with CORS and throttling
- **Amazon ECR**: Container registry for Lambda images
- **Systems Manager Parameter Store**: Configuration management
- **AWS Secrets Manager**: Secure credential storage
- **CloudWatch**: Logging, monitoring, and alerting

## 🚀 Quick Start

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Docker** installed and running
4. **Node.js 18+** for CDK
5. **Python 3.11+** for local testing

### Environment Variables

Set these environment variables before deployment:

```bash
export AWS_ACCOUNT_ID="123456789012"
export AWS_DEFAULT_REGION="us-east-1"

# Optional: Custom domain configuration
export PROD_CERTIFICATE_ARN="arn:aws:acm:us-east-1:123456789012:certificate/..."
export PROD_HOSTED_ZONE_ID="Z1234567890ABC"
```

### Deployment Commands

```bash
# Deploy to development
./scripts/deploy.sh dev

# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh prod

# Skip tests during deployment
./scripts/deploy.sh prod --skip-tests

# Force CDK bootstrap
./scripts/deploy.sh dev --force
```

## 🎯 Deployment Stages

### Development (`dev`)
- **Memory**: 256 MB
- **Timeout**: 15 seconds
- **Concurrency**: 100
- **Cost**: ~$5-10/month for moderate usage

### Staging (`staging`)
- **Memory**: 512 MB
- **Timeout**: 30 seconds  
- **Concurrency**: 500
- **Cost**: ~$15-25/month for testing workloads

### Production (`prod`)
- **Memory**: 1024 MB
- **Timeout**: 30 seconds
- **Concurrency**: 1000
- **Cost**: ~$25-100/month depending on traffic

## 📊 Monitoring and Observability

### CloudWatch Dashboard

The deployment creates a comprehensive dashboard showing:
- Lambda function metrics (invocations, errors, duration)
- API Gateway metrics (requests, latency, error rates)
- Custom application metrics (template processing performance)
- Recent errors and performance trends

Access at: AWS Console → CloudWatch → Dashboards → `phoney-{stage}`

### Alarms and Alerting

Automated alarms monitor:
- ❌ **Error rates** above threshold
- ⏱️ **High latency** (>5s production, >10s dev)
- 🚫 **Throttling events**
- 💾 **Memory usage patterns**
- 📊 **Custom metrics** (template processing time)

### Log Analysis

Use the provided CloudWatch Logs Insights queries:

```bash
# View recent errors
aws logs start-query \
  --log-group-name "/aws/lambda/phoney-prod" \
  --start-time 1609459200 \
  --end-time 1609545600 \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20'
```

## 🔧 Configuration Management

### Parameter Store

Application configuration is stored in AWS Systems Manager Parameter Store:

```
/phoney/{stage}/SECRET_KEY          # JWT secret key
/phoney/{stage}/API_USERNAME        # Basic auth username  
/phoney/{stage}/CORS_ORIGINS        # Allowed CORS origins
/phoney/{stage}/RATE_LIMIT_PER_MINUTE # Rate limiting
```

### Secrets Manager

Sensitive data is stored in AWS Secrets Manager:

```json
{
  "name": "phoney/{stage}/credentials",
  "value": {
    "api_password_hash": "$2b$12$...",
    "jwt_secret": "your-jwt-secret"
  }
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The `.github/workflows/deploy-aws.yml` provides:
- **Automated testing** on pull requests
- **Multi-stage deployment** (dev/staging/prod)
- **Smoke testing** after deployment
- **Rollback notifications** on failure

### Workflow Triggers

- `push` to `main` → Deploy to production
- `push` to `staging` → Deploy to staging  
- `push` to `develop` → Deploy to development
- `workflow_dispatch` → Manual deployment to any stage

## 💰 Cost Optimization

### Current Pricing (us-east-1)

Based on 1M requests/month with average 150ms execution time:

| Component | Cost |
|-----------|------|
| Lambda Requests | $0.20 |
| Lambda Compute (1GB) | $25.00 |
| API Gateway | $3.50 |
| CloudWatch Logs | $2.00 |
| Parameter Store | $0.05 |
| **Total** | **~$30.75/month** |

### Optimization Tips

1. **Right-size memory**: Monitor CloudWatch metrics and adjust
2. **Optimize code**: Reduce cold start time and execution duration
3. **Use reserved capacity**: For predictable workloads
4. **Log retention**: Set appropriate retention periods
5. **Unused resources**: Remove dev/staging when not needed

## 🔒 Security Best Practices

### IAM Roles and Policies

The Lambda function has minimal permissions:
- Read from Parameter Store (scoped to `/phoney/{stage}/*`)
- Read from Secrets Manager (scoped to specific secrets)
- Write to CloudWatch Logs
- X-Ray tracing permissions

### Network Security

- API Gateway with CORS restrictions
- Rate limiting and throttling enabled
- Optional VPC deployment for enhanced security
- WAF integration available for additional protection

### Data Protection

- All data encrypted in transit (HTTPS)
- Secrets encrypted at rest in Secrets Manager
- No persistent data storage (stateless functions)
- JWT token-based authentication

## 🚨 Troubleshooting

### Common Issues

**1. Cold Start Performance**
```bash
# Check cold start metrics
aws logs insights start-query \
  --log-group-name "/aws/lambda/phoney-prod" \
  --query-string 'fields @timestamp, @initDuration | filter ispresent(@initDuration) | stats avg(@initDuration)'
```

**2. Memory Issues**
```bash
# Monitor memory usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name MemoryUtilization \
  --dimensions Name=FunctionName,Value=phoney-prod \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average,Maximum
```

**3. Deployment Failures**
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name PhoneyStack-prod \
  --query 'StackEvents[?ResourceStatus!=`CREATE_COMPLETE`]'
```

### Health Checks

```bash
# Test API endpoint
curl -X POST https://api.phoney.example.com/template \
  -H "Content-Type: application/json" \
  -d '{"template":{"name":"{{name}}","email":"{{email}}"},"count":1}'

# Check Lambda function status
aws lambda get-function --function-name phoney-prod

# View recent logs
aws logs tail /aws/lambda/phoney-prod --follow
```

## 📚 Additional Resources

### AWS Documentation
- [AWS Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/lambda-images.html)
- [API Gateway HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
- [CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)

### Phoney Documentation
- [Main README](../README.md)
- [API Tutorial](../TUTORIAL.md)
- [Template Examples](../examples/)
- [Deployment Plan](../aws-serverless-deployment-plan.md)

## 🤝 Contributing

When making infrastructure changes:

1. Test in `dev` environment first
2. Update documentation
3. Run `cdk diff` to review changes
4. Use feature branches for major changes
5. Update cost estimates if resource changes impact pricing

## 📞 Support

For infrastructure issues:
- Check CloudWatch dashboards and alarms
- Review deployment logs in GitHub Actions
- Use CloudWatch Logs Insights queries for debugging
- Check AWS Health Dashboard for service issues

---

🚀 **Ready to deploy?** Run `./scripts/deploy.sh dev` to get started!