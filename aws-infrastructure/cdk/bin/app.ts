#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { PhoneyStack } from '../lib/phoney-stack';

const app = new cdk.App();

// Get configuration from context or environment
const stage = app.node.tryGetContext('stage') || process.env.STAGE || 'dev';
const account = process.env.CDK_DEFAULT_ACCOUNT || process.env.AWS_ACCOUNT_ID;
const region = process.env.CDK_DEFAULT_REGION || process.env.AWS_REGION || 'us-east-1';

// Environment-specific configuration
const envConfig = {
  dev: {
    domainName: undefined,
    certificateArn: undefined,
    hostedZoneId: undefined,
  },
  staging: {
    domainName: 'staging-api.phoney.example.com',
    certificateArn: process.env.STAGING_CERTIFICATE_ARN,
    hostedZoneId: process.env.STAGING_HOSTED_ZONE_ID,
  },
  prod: {
    domainName: 'api.phoney.example.com',
    certificateArn: process.env.PROD_CERTIFICATE_ARN,
    hostedZoneId: process.env.PROD_HOSTED_ZONE_ID,
  },
};

const config = envConfig[stage as keyof typeof envConfig];

if (!account) {
  console.error('AWS account ID is required. Set CDK_DEFAULT_ACCOUNT or AWS_ACCOUNT_ID environment variable.');
  process.exit(1);
}

// Create the stack
new PhoneyStack(app, `PhoneyStack-${stage}`, {
  env: {
    account: account,
    region: region,
  },
  stage: stage as 'dev' | 'staging' | 'prod',
  domainName: config.domainName,
  certificateArn: config.certificateArn,
  hostedZoneId: config.hostedZoneId,
  description: `Phoney Template API infrastructure for ${stage} environment`,
  tags: {
    Project: 'Phoney',
    Stage: stage,
    ManagedBy: 'CDK',
  },
});

// Synthesize the app
app.synth();