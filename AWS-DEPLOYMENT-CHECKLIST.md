# 🚀 AWS Serverless Deployment Checklist

## Pre-Deployment Setup

### ✅ AWS Account Preparation
- [ ] AWS account created and billing configured
- [ ] IAM user created with appropriate permissions:
  - [ ] Lambda full access
  - [ ] API Gateway full access
  - [ ] ECR full access
  - [ ] CloudFormation full access
  - [ ] Systems Manager Parameter Store access
  - [ ] Secrets Manager access
  - [ ] CloudWatch full access
  - [ ] IAM role creation permissions
- [ ] AWS CLI installed and configured
- [ ] AWS credentials configured (`aws configure`)

### ✅ Development Environment
- [ ] Docker installed and running
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Poetry installed (if using Poetry for dependencies)
- [ ] Git repository cloned locally

### ✅ Environment Variables
- [ ] `AWS_ACCOUNT_ID` set to your AWS account ID
- [ ] `AWS_DEFAULT_REGION` set (e.g., `us-east-1`)
- [ ] Optional domain variables set if using custom domain:
  - [ ] `PROD_CERTIFICATE_ARN` (SSL certificate ARN)
  - [ ] `PROD_HOSTED_ZONE_ID` (Route 53 hosted zone)
  - [ ] `STAGING_CERTIFICATE_ARN` (if using staging)
  - [ ] `STAGING_HOSTED_ZONE_ID` (if using staging)

## First-Time Deployment

### ✅ Step 1: Test Locally
- [ ] Run local tests: `poetry run pytest`
- [ ] Verify template system works: `poetry run python examples/template_examples.py`
- [ ] Check linting: `poetry run ruff check phoney/`
- [ ] Verify type checking: `poetry run mypy phoney/`

### ✅ Step 2: Create ECR Repositories
```bash
# Development
aws ecr create-repository --repository-name phoney-dev --region $AWS_DEFAULT_REGION

# Staging (if needed)
aws ecr create-repository --repository-name phoney-staging --region $AWS_DEFAULT_REGION

# Production
aws ecr create-repository --repository-name phoney-prod --region $AWS_DEFAULT_REGION
```

### ✅ Step 3: Deploy Development Environment
- [ ] Navigate to project root
- [ ] Make deploy script executable: `chmod +x aws-infrastructure/scripts/deploy.sh`
- [ ] Deploy to dev: `./aws-infrastructure/scripts/deploy.sh dev`
- [ ] Verify deployment success
- [ ] Test API endpoint
- [ ] Check CloudWatch logs

### ✅ Step 4: Configure Production Settings
- [ ] Update Parameter Store values for production:
  - [ ] `/phoney/prod/SECRET_KEY` - Strong 32+ character secret
  - [ ] `/phoney/prod/API_USERNAME` - Production username
  - [ ] `/phoney/prod/CORS_ORIGINS` - Production domains only
  - [ ] `/phoney/prod/RATE_LIMIT_PER_MINUTE` - Production rate limits
- [ ] Configure Secrets Manager:
  - [ ] Create secret: `phoney/prod/credentials`
  - [ ] Set strong password hash
  - [ ] Set JWT secret key

### ✅ Step 5: Deploy Production Environment
- [ ] Deploy to production: `./aws-infrastructure/scripts/deploy.sh prod`
- [ ] Verify all alarms are created
- [ ] Test production API thoroughly
- [ ] Configure domain name (if using custom domain)
- [ ] Update DNS records (if using custom domain)

## CI/CD Setup

### ✅ GitHub Actions Configuration
- [ ] Ensure GitHub repository has required secrets:
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
  - [ ] `AWS_ACCOUNT_ID`
- [ ] Test workflow on feature branch
- [ ] Verify staging deployment works
- [ ] Test production deployment (if ready)

### ✅ Branch Protection
- [ ] Configure branch protection for `main`
- [ ] Require pull request reviews
- [ ] Require status checks to pass
- [ ] Require up-to-date branches

## Monitoring Setup

### ✅ CloudWatch Configuration
- [ ] Import CloudWatch dashboard from `aws-infrastructure/monitoring/cloudwatch-dashboard.json`
- [ ] Verify all alarms are working
- [ ] Test alarm notifications
- [ ] Set up SNS topic for alerts
- [ ] Configure email/SMS notifications

### ✅ Log Analysis
- [ ] Test CloudWatch Logs Insights queries
- [ ] Set up log retention policies
- [ ] Configure log aggregation (if needed)
- [ ] Test structured logging format

## Security Configuration

### ✅ API Security
- [ ] Verify CORS settings are restrictive for production
- [ ] Test JWT authentication on protected endpoints
- [ ] Verify rate limiting is working
- [ ] Test API key authentication (if enabled)

### ✅ Infrastructure Security
- [ ] Review IAM roles and permissions
- [ ] Ensure least privilege access
- [ ] Verify encryption at rest and in transit
- [ ] Test network security (if using VPC)

## Performance Testing

### ✅ Load Testing
- [ ] Test with small loads (10 requests/second)
- [ ] Test with moderate loads (100 requests/second)
- [ ] Test with burst traffic
- [ ] Monitor Lambda concurrency limits
- [ ] Test cold start performance

### ✅ Template Processing
- [ ] Test simple templates (<10ms)
- [ ] Test complex nested templates
- [ ] Test large array generation (1000+ records)
- [ ] Test with different locales
- [ ] Verify memory usage patterns

## Production Readiness

### ✅ Documentation
- [ ] API documentation updated
- [ ] Infrastructure documentation complete
- [ ] Runbooks created for common issues
- [ ] Contact information for support

### ✅ Backup and Recovery
- [ ] Parameter Store values documented
- [ ] Secrets Manager values backed up securely
- [ ] Infrastructure code in version control
- [ ] Recovery procedures documented

### ✅ Monitoring and Alerting
- [ ] All critical alarms configured
- [ ] Alert recipients configured
- [ ] Escalation procedures defined
- [ ] Dashboard access permissions set

## Post-Deployment Verification

### ✅ Functional Testing
- [ ] Test all API endpoints
- [ ] Verify template examples work
- [ ] Test error handling
- [ ] Verify authentication flows

### ✅ Performance Validation
- [ ] Response times under expected thresholds
- [ ] Memory usage within limits
- [ ] Cold start times acceptable
- [ ] No throttling under normal load

### ✅ Cost Monitoring
- [ ] Set up billing alerts
- [ ] Monitor daily costs
- [ ] Compare actual vs estimated costs
- [ ] Optimize resource allocation if needed

## Ongoing Maintenance

### ✅ Regular Tasks
- [ ] Review CloudWatch dashboards weekly
- [ ] Monitor costs monthly
- [ ] Update dependencies quarterly
- [ ] Review security settings quarterly
- [ ] Test disaster recovery procedures

### ✅ Updates and Patches
- [ ] Keep Lambda runtime updated
- [ ] Update Python dependencies regularly
- [ ] Monitor AWS service announcements
- [ ] Plan for AWS CDK updates

## Rollback Plan

### ✅ Emergency Procedures
- [ ] Document rollback steps
- [ ] Test rollback procedure in staging
- [ ] Keep previous deployment artifacts
- [ ] Maintain emergency contact list

### ✅ Quick Rollback Commands
```bash
# Rollback Lambda function to previous version
aws lambda update-function-code \
  --function-name phoney-prod \
  --image-uri $ECR_REPO:previous-tag

# Rollback CloudFormation stack
aws cloudformation update-stack \
  --stack-name PhoneyStack-prod \
  --template-body file://previous-template.yaml
```

## Success Criteria

### ✅ Deployment Success
- [ ] All infrastructure deployed without errors
- [ ] API responds to health checks
- [ ] Template processing works correctly
- [ ] Monitoring and alerting operational
- [ ] Security measures in place
- [ ] Performance meets requirements
- [ ] Costs within budget
- [ ] Documentation complete

---

## 📞 Emergency Contacts

**Infrastructure Issues:**
- AWS Support: [Your AWS Support Plan]
- DevOps Team: [Your Team Contacts]

**Application Issues:**
- Development Team: [Your Dev Team]
- Product Owner: [Your Product Team]

**Security Issues:**
- Security Team: [Your Security Team]
- AWS Security: https://aws.amazon.com/security/

---

## 🚀 Deployment Commands Quick Reference

```bash
# Development deployment
./aws-infrastructure/scripts/deploy.sh dev

# Staging deployment  
./aws-infrastructure/scripts/deploy.sh staging

# Production deployment
./aws-infrastructure/scripts/deploy.sh prod

# Manual deployment via GitHub Actions
gh workflow run deploy-aws.yml -f stage=prod

# Monitor logs
aws logs tail /aws/lambda/phoney-prod --follow

# Check function status
aws lambda get-function --function-name phoney-prod
```

**Deployment Status:** ⏳ Ready for implementation
**Estimated Timeline:** 2-4 hours for first deployment
**Prerequisites:** All checklist items above ✅