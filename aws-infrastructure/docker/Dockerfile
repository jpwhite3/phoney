# Use the official AWS Lambda Python runtime as base image
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY phoney/ ./phoney/
COPY lambda_handler.py .

# Set the CMD to the Lambda handler
CMD ["lambda_handler.handler"]

# Add labels for better container management
LABEL maintainer="your-email@example.com"
LABEL version="1.0"
LABEL description="Phoney Template API Lambda Function"

# Health check (not used in Lambda but good practice)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD echo "Lambda function container is healthy"