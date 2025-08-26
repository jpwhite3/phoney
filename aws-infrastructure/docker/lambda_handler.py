"""
AWS Lambda handler for Phoney Template API.

This module adapts the FastAPI application for AWS Lambda using Mangum.
It includes optimizations for cold start performance and AWS service integration.
"""

import json
import logging
import os
from functools import lru_cache
from typing import Any, Dict, Optional

import structlog

# Configure structured logging for CloudWatch
logging.basicConfig(
    format="%(message)s",
    level=logging.INFO if os.getenv("LOG_LEVEL", "INFO") == "INFO" else logging.DEBUG,
)

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Import AWS services for configuration
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    logger.warning("AWS SDK not available - running in local mode")

# Lambda cold start optimization
if os.getenv("LAMBDA_COLD_START_OPTIMIZATION") == "true":
    logger.info("Initializing Lambda cold start optimizations")

    # Preload Faker for better performance
    if os.getenv("PRELOAD_FAKER_PROVIDERS") == "true":
        try:
            from faker import Faker

            _fake = Faker()
            # Preload common generators to reduce cold start
            _fake.name()
            _fake.email()
            _fake.address()
            logger.info("Faker providers preloaded successfully")
        except Exception as e:
            logger.warning("Failed to preload Faker providers", error=str(e))

# Global variables for caching
_ssm_client = None
_secrets_client = None
_parameter_cache = {}


@lru_cache(maxsize=1)
def get_ssm_client():
    """Get cached SSM client."""
    global _ssm_client
    if _ssm_client is None and AWS_AVAILABLE:
        _ssm_client = boto3.client("ssm")
    return _ssm_client


@lru_cache(maxsize=1)
def get_secrets_client():
    """Get cached Secrets Manager client."""
    global _secrets_client
    if _secrets_client is None and AWS_AVAILABLE:
        _secrets_client = boto3.client("secretsmanager")
    return _secrets_client


def load_parameter_store_config() -> Dict[str, str]:
    """Load configuration from AWS Systems Manager Parameter Store."""
    if not AWS_AVAILABLE:
        return {}

    ssm = get_ssm_client()
    if not ssm:
        return {}

    prefix = os.getenv("PARAMETER_STORE_PREFIX", "/phoney/prod/")
    config = {}

    try:
        # Get all parameters with the prefix
        paginator = ssm.get_paginator("get_parameters_by_path")
        for page in paginator.paginate(
            Path=prefix, Recursive=True, WithDecryption=True
        ):
            for param in page["Parameters"]:
                key = param["Name"].replace(prefix, "")
                config[key] = param["Value"]

        logger.info("Loaded configuration from Parameter Store", count=len(config))

    except (ClientError, NoCredentialsError) as e:
        logger.warning("Failed to load Parameter Store configuration", error=str(e))

    return config


def load_secrets_manager_config() -> Dict[str, str]:
    """Load secrets from AWS Secrets Manager."""
    if not AWS_AVAILABLE:
        return {}

    secrets_client = get_secrets_client()
    if not secrets_client:
        return {}

    secret_name = os.getenv("SECRET_NAME")
    if not secret_name:
        return {}

    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response["SecretString"])

        logger.info("Loaded secrets from Secrets Manager", secret_name=secret_name)
        return secret_data

    except (ClientError, NoCredentialsError, json.JSONDecodeError) as e:
        logger.warning(
            "Failed to load Secrets Manager configuration",
            secret_name=secret_name,
            error=str(e),
        )

    return {}


def setup_aws_configuration():
    """Setup configuration from AWS services."""
    # Load from Parameter Store
    if os.getenv("USE_PARAMETER_STORE") == "true":
        param_config = load_parameter_store_config()
        for key, value in param_config.items():
            if key not in os.environ:  # Don't override existing env vars
                os.environ[key] = value

    # Load from Secrets Manager
    if os.getenv("USE_SECRETS_MANAGER") == "true":
        secret_config = load_secrets_manager_config()
        for key, value in secret_config.items():
            env_key = key.upper().replace("-", "_")
            if env_key not in os.environ:  # Don't override existing env vars
                os.environ[env_key] = value


# Setup AWS configuration on module import
setup_aws_configuration()

# Import the FastAPI app after configuration is set up
try:
    from mangum import Mangum

    from phoney.app.main import app

    # Create the Mangum handler with optimizations
    handler = Mangum(
        app,
        lifespan="off",  # Disable lifespan for Lambda
        api_gateway_base_path=None,
        text_mime_types=[
            "application/json",
            "application/javascript",
            "application/xml",
            "application/vnd.api+json",
        ],
    )

    logger.info("FastAPI application initialized successfully")

except ImportError as e:
    logger.error("Failed to import FastAPI application", error=str(e))
    raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.

    Args:
        event: API Gateway event data
        context: Lambda context object

    Returns:
        API Gateway response format
    """
    # Log request details
    logger.info(
        "Lambda invocation started",
        request_id=context.aws_request_id,
        function_name=context.function_name,
        memory_limit=context.memory_limit_in_mb,
        remaining_time=context.get_remaining_time_in_millis(),
        event_source=event.get("requestContext", {}).get("domainName", "unknown"),
        http_method=event.get("requestContext", {}).get("http", {}).get("method"),
        path=event.get("requestContext", {}).get("http", {}).get("path"),
    )

    try:
        # Add request ID to environment for tracing
        os.environ["AWS_REQUEST_ID"] = context.aws_request_id

        # Call the Mangum handler
        response = handler(event, context)

        # Log successful response
        logger.info(
            "Lambda invocation completed successfully",
            request_id=context.aws_request_id,
            status_code=response.get("statusCode"),
            remaining_time=context.get_remaining_time_in_millis(),
        )

        return response

    except Exception as e:
        # Log error details
        logger.error(
            "Lambda invocation failed",
            request_id=context.aws_request_id,
            error=str(e),
            error_type=type(e).__name__,
            remaining_time=context.get_remaining_time_in_millis(),
            exc_info=True,
        )

        # Return error response
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "error": "Internal server error",
                    "request_id": context.aws_request_id,
                    "message": "An error occurred processing your request",
                }
            ),
        }


# Export the handler for testing
__all__ = ["handler", "lambda_handler"]

# For backwards compatibility, also export as 'handler'
handler = lambda_handler
