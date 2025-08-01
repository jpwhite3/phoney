# Phoney

[![Build Status](https://github.com/jpwhite3/gitinspector/actions/workflows/python-package.yml/badge.svg)](https://github.com/jpwhite3/phoney/actions/workflows/python-package.yml)
[![Coverage Status](https://coveralls.io/repos/github/jpwhite3/phoney/badge.svg?branch=main)](https://coveralls.io/github/jpwhite3/phoney?branch=main)
[![Latest release](https://img.shields.io/github/release/jpwhite3/phoney.svg?style=flat-square)](https://github.com/jpwhite3/phoney/releases/latest)
[![License](https://img.shields.io/github/license/jpwhite3/phoney.svg?style=flat-square)](https://github.com/jpwhite3/phoney/blob/master/LICENSE.txt)

A modern FastAPI wrapper for the Python Faker library, providing access to all Faker data generators via a RESTful API.

## Features

- 🚀 **Python 3.13 Compatible**: Built with the latest Python features
- 🔄 **Complete Faker Integration**: Access to all Faker data generators and providers
- 🔒 **Secure Authentication**: JWT token-based authentication for sensitive operations
- 📊 **Flexible Response Formats**: Get single or multiple fake data items in one request
- 🌐 **Locale Support**: Generate locale-specific fake data
- 🧩 **Advanced Parameters**: Pass arguments to Faker generators for customized data
- 📝 **OpenAPI Documentation**: Comprehensive API documentation with Swagger UI

## Quick Start

### Installation

Phoney uses Poetry for dependency management. To install:

```bash
# Clone the repository
git clone https://github.com/jpwhite3/phoney.git
cd phoney

# Install dependencies with Poetry
poetry install

# Create .env file with necessary secrets
cp .env.example .env
# Edit .env and add your SECRET_KEY and API credentials
```

### Running the API

```bash
# Development mode
poetry run uvicorn phoney.app.main:app --reload

# Production mode
poetry run uvicorn phoney.app.main:app --host 0.0.0.0 --port 8000

# With Docker
docker-compose up
```

## API Usage

### Browsing Available Providers

```bash
curl -X GET "http://localhost:8000/api/v1/providers" -H "accept: application/json"
```

### Listing Generators for a Provider

```bash
curl -X GET "http://localhost:8000/api/v1/provider/person" -H "accept: application/json"
```

### Generating Fake Data

```bash
# Generate a single name
curl -X GET "http://localhost:8000/api/v1/provider/person/name" -H "accept: application/json"

# Generate 5 names
curl -X GET "http://localhost:8000/api/v1/provider/person/name?count=5" -H "accept: application/json"

# Generate with a specific locale
curl -X GET "http://localhost:8000/api/v1/provider/person/name?locale=fr_FR" -H "accept: application/json"
```

### Advanced Generation with Parameters (requires authentication)

```bash
# Get authentication token
curl -X POST "http://localhost:8000/token" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "username=api_user&password=your_password"

# Use token to generate data with parameters
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "accept: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "address",
    "generator": "address",
    "locale": "en_US",
    "count": 3,
    "seed": 42,
    "params": {
      "args": [],
      "kwargs": {"include_country": true}
    }
  }'
```

## Configuration

Phoney uses environment variables for configuration. Create a `.env` file with:

```env
# Environment (dev, test, prod)
ENV_STATE=dev
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your_secure_random_key_here  # Generate with: openssl rand -hex 32
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
ALGORITHM=HS256

# API credentials
API_USERNAME=api_user
API_PASSWORD_HASH=bcrypt_hash_here  # Generate with Python: from passlib.context import CryptContext; CryptContext(['bcrypt']).hash('password')

# CORS settings
CORS_ORIGINS=["*"]
CORS_HEADERS=["*"]
CORS_METHODS=["*"]
```

## Development

### Running Tests

```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=phoney tests/
```

### Code Quality

```bash
# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run ruff check .
poetry run mypy .
```

## Docker Support

Phoney includes Docker support for easy deployment:

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.