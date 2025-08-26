# Phoney

[![Build Status](https://github.com/jpwhite3/gitinspector/actions/workflows/python-package.yml/badge.svg)](https://github.com/jpwhite3/phoney/actions/workflows/python-package.yml)
[![Coverage Status](https://coveralls.io/repos/github/jpwhite3/phoney/badge.svg?branch=main)](https://coveralls.io/github/jpwhite3/phoney?branch=main)
[![Latest release](https://img.shields.io/github/release/jpwhite3/phoney.svg?style=flat-square)](https://github.com/jpwhite3/phoney/releases/latest)
[![License](https://img.shields.io/github/license/jpwhite3/phoney.svg?style=flat-square)](https://github.com/jpwhite3/phoney/blob/master/LICENSE.txt)

A modern FastAPI wrapper for the Python Faker library, providing access to all Faker data generators via a RESTful API.

**Perfect for beginners learning automated testing** - generate realistic fake data with simple HTTP requests!

## 🚀 Quick Start for Beginners

Generate fake data in 3 simple steps:

1. **Start the API server:**
   ```bash
   git clone https://github.com/jpwhite3/phoney.git
   cd phoney
   poetry install
   poetry run uvicorn phoney.app.main:app --reload
   ```

2. **Generate fake data:**
   ```bash
   # Get a random name
   curl http://localhost:8000/fake/name
   
   # Get 5 email addresses
   curl "http://localhost:8000/fake/email?count=5"
   
   # Get a French address
   curl "http://localhost:8000/fake/address?locale=fr_FR"
   ```

3. **Use in your tests:**
   ```python
   import requests
   
   # Generate test user data
   name = requests.get('http://localhost:8000/fake/name').json()['data']
   email = requests.get('http://localhost:8000/fake/email').json()['data']
   
   # Use in your test
   assert register_user(name, email) == True
   ```

✨ **That's it!** No complex setup, no provider knowledge needed - just ask for what you want.

## ✨ Features

### 🎯 **Beginner-Friendly**
- **Simple API**: Just `GET /fake/name` to get a name - no complex URLs!
- **Smart Detection**: Ask for `phone`, `email`, or `address` and get exactly what you expect
- **No Setup**: Works immediately without authentication or configuration
- **Clear Errors**: Helpful error messages with suggestions when something goes wrong

### 🔧 **Powerful & Flexible**
- **288+ Generators**: Access to every Faker generator (names, emails, addresses, companies, etc.)
- **Multiple Formats**: Get single items or arrays of data in one request
- **Localization**: Generate data in 50+ locales (English, French, German, Spanish, etc.)
- **Reproducible**: Use seeds for consistent test data across test runs
- **Fast**: Optimized for high-volume test data generation

### 🏗️ **Production Ready**
- **Python 3.12+ Compatible**: Built with modern Python features
- **RESTful Design**: Standard HTTP methods and status codes
- **OpenAPI Documentation**: Interactive API docs at `/docs`
- **Docker Support**: Easy deployment with included Dockerfile
- **Security**: Optional authentication for advanced features

## 📖 Beginner Tutorial

### Why Use Fake Data in Testing?

When writing automated tests, you need realistic data that:
- **Looks real** but doesn't expose sensitive information
- **Is consistent** across test runs for reliable results  
- **Is diverse** to test edge cases and different scenarios
- **Is easy to generate** without manual data creation

**Phoney solves this!** Instead of hardcoding test data like `"John Doe"` and `"test@example.com"`, generate realistic, varied data on-demand.

### Your First API Call

```bash
# Try this in your terminal:
curl http://localhost:8000/fake/name

# Response:
{
  "generator": "name",
  "data": "Sarah Johnson",
  "count": 1,
  "locale": "en_US",
  "seed": null
}
```

### Common Test Data Patterns

```bash
# User registration tests
curl http://localhost:8000/fake/name          # "Michael Brown"
curl http://localhost:8000/fake/email         # "sarah@example.net"
curl http://localhost:8000/fake/phone         # "555-0123"

# E-commerce tests
curl http://localhost:8000/fake/company       # "Tech Solutions Inc"
curl http://localhost:8000/fake/address       # "123 Main St, City"

# Content tests
curl http://localhost:8000/fake/text          # Random paragraph
curl http://localhost:8000/fake/url           # "https://example.org"
```

### Testing with Python

```python
import requests
import pytest

class TestUserRegistration:
    def test_valid_user_registration(self):
        # Generate realistic test data
        name = requests.get('http://localhost:8000/fake/name').json()['data']
        email = requests.get('http://localhost:8000/fake/email').json()['data']
        
        # Test your application
        response = register_user(name, email)
        assert response.status_code == 201
        
    def test_multiple_users(self):
        # Generate 10 users at once
        names = requests.get('http://localhost:8000/fake/name?count=10').json()['data']
        
        for name in names:
            response = register_user(name, f"{name.lower().replace(' ', '')}@test.com")
            assert response.status_code == 201
```

### Testing with JavaScript

```javascript
// Using fetch API
const generateTestUser = async () => {
  const nameResp = await fetch('http://localhost:8000/fake/name');
  const emailResp = await fetch('http://localhost:8000/fake/email');
  
  return {
    name: (await nameResp.json()).data,
    email: (await emailResp.json()).data
  };
};

// In your Jest/Mocha tests
test('user registration works with fake data', async () => {
  const user = await generateTestUser();
  const result = await registerUser(user.name, user.email);
  expect(result.success).toBe(true);
});
```

### Pro Tips for Testing

1. **Use seeds for consistent tests:**
   ```bash
   curl "http://localhost:8000/fake/name?seed=42"
   # Always returns "Allison Hill" - great for predictable tests!
   ```

2. **Generate bulk data efficiently:**
   ```bash
   curl "http://localhost:8000/fake/email?count=100"
   # Get 100 emails in one request
   ```

3. **Test internationalization:**
   ```bash
   curl "http://localhost:8000/fake/name?locale=ja_JP"  # Japanese names
   curl "http://localhost:8000/fake/address?locale=fr_FR"  # French addresses
   ```

4. **Discover new generators:**
   ```bash
   curl http://localhost:8000/generators
   # See all 288+ available data types
   ```

## 🛠️ Installation

### Prerequisites
- Python 3.12 or higher
- Poetry (for dependency management)

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/jpwhite3/phoney.git
cd phoney

# 2. Install Poetry (if you don't have it)
curl -sSL https://install.python-poetry.org | python3 -

# 3. Install dependencies
poetry install

# 4. Create configuration (optional for basic usage)
cp .env.example .env
# Edit .env only if you need authentication features
```

### Starting the Server

```bash
# Start in development mode (recommended for testing)
poetry run uvicorn phoney.app.main:app --reload

# Server starts at: http://localhost:8000
# API documentation: http://localhost:8000/docs
# Try it: http://localhost:8000/fake/name
```

**Alternative Methods:**
```bash
# Production mode
poetry run uvicorn phoney.app.main:app --host 0.0.0.0 --port 8000

# With Docker
docker-compose up
```

### Verify Installation

```bash
# Test the API is working
curl http://localhost:8000/fake/name

# Should return something like:
# {"generator":"name","data":"Jennifer Wilson","count":1,"locale":"en_US","seed":null}
```

## 📚 Complete API Reference

### 🔥 Simple API (Start Here!)

Perfect for beginners - just ask for what you need!

**Basic Pattern:** `GET /fake/{what_you_want}`

```bash
# Essential test data
curl http://localhost:8000/fake/name         # "Jessica Martinez"
curl http://localhost:8000/fake/email        # "john@example.com"
curl http://localhost:8000/fake/phone        # "555-0123"
curl http://localhost:8000/fake/address      # "123 Oak Street"

# Multiple items
curl "http://localhost:8000/fake/name?count=5"

# Different languages
curl "http://localhost:8000/fake/address?locale=fr_FR"

# Reproducible data (same seed = same result)
curl "http://localhost:8000/fake/company?seed=42"
```

**Response Format:**
```json
{
  "generator": "name",
  "data": "Sarah Johnson",
  "count": 1,
  "locale": "en_US",
  "seed": null
}
```

### 🤖 Smart Generator Detection

Don't worry about exact generator names - the API understands what you want!

| What You Type | What You Get | Actual Generator |
|---------------|--------------|------------------|
| `name`, `person`, `full_name` | Person names | `name` |
| `email`, `mail` | Email addresses | `email` |
| `phone`, `telephone`, `mobile` | Phone numbers | `phone_number` |
| `address`, `street` | Street addresses | `address` |
| `company`, `business` | Company names | `company` |
| `job`, `profession` | Job titles | `job` |
| `url`, `website` | Web URLs | `url` |
| `date`, `time` | Dates/times | `date`, `time` |
| `text`, `paragraph` | Random text | `text`, `paragraph` |

### 🗑️ Discover All Generators

```bash
# See all 288+ available generators
curl http://localhost:8000/generators | jq '.[0:10]'  # First 10

# Search for specific types (using grep)
curl http://localhost:8000/generators | grep -i color
```

**Popular Generators:**
- **People**: `name`, `first_name`, `last_name`, `prefix`, `suffix`
- **Contact**: `email`, `phone_number`, `address`, `city`, `state`, `country`
- **Internet**: `url`, `domain_name`, `ipv4`, `user_name`, `password`
- **Business**: `company`, `job`, `catch_phrase`, `bs`
- **Finance**: `credit_card_number`, `iban`, `currency_code`
- **Dates**: `date`, `time`, `date_time`, `future_date`, `past_date`
- **Text**: `sentence`, `paragraph`, `text`, `word`, `words`
- **IDs**: `uuid4`, `ssn`, `ean`, `isbn`

### 🎨 Query Parameters

Customize your fake data with URL parameters:

```bash
# Count: Generate multiple items (1-100)
curl "http://localhost:8000/fake/email?count=10"

# Locale: Get localized data
curl "http://localhost:8000/fake/name?locale=es_ES"     # Spanish
curl "http://localhost:8000/fake/address?locale=ja_JP"  # Japanese
curl "http://localhost:8000/fake/name?locale=de_DE"     # German

# Seed: Reproducible results (great for testing!)
curl "http://localhost:8000/fake/name?seed=123"         # Always same result
curl "http://localhost:8000/fake/email?seed=456&count=5" # Same 5 emails

# Combine parameters
curl "http://localhost:8000/fake/address?count=3&locale=fr_FR&seed=789"
```

**Available Locales:** `en_US`, `en_GB`, `fr_FR`, `de_DE`, `es_ES`, `it_IT`, `pt_BR`, `ja_JP`, `ko_KR`, `zh_CN`, `ru_RU`, `ar_SA`, and 40+ more!

### 🛡️ Advanced API

For advanced users who need more control:

**Browse Providers:**
```bash
curl http://localhost:8000/api/v1/providers
```

**List Provider Generators:**
```bash
curl http://localhost:8000/api/v1/provider/person
```

**Provider-Specific Generation:**
```bash
# Explicit provider/generator syntax
curl http://localhost:8000/api/v1/provider/person/name
curl http://localhost:8000/api/v1/provider/internet/email
curl http://localhost:8000/api/v1/provider/address/address
```

**Custom Parameters (requires authentication):**

1. Get authentication token:
   ```bash
   curl -X POST http://localhost:8000/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=api_user&password=your_password"
   ```

2. Use advanced features:
   ```bash
   curl -X POST http://localhost:8000/api/v1/generate \
     -H "Authorization: Bearer your_token" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "address",
       "generator": "address",
       "count": 3,
       "locale": "en_US",
       "seed": 42,
       "unique": true,
       "params": {
         "kwargs": {"include_secondary": true}
       }
     }'
   ```

## 🔧 Configuration

**For basic usage, no configuration needed!** 

For advanced features (authentication, custom settings), create a `.env` file:

```env
# Basic settings
ENV_STATE=dev
HOST=0.0.0.0
PORT=8000

# Security (for advanced POST endpoint)
SECRET_KEY=your_secure_random_key  # openssl rand -hex 32
API_USERNAME=api_user
API_PASSWORD_HASH=bcrypt_hash       # See documentation for hash generation

# CORS (allow all origins for testing)
CORS_ORIGINS=["*"]
```

**Generate secure keys:**
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate password hash (Python)
python -c "from passlib.context import CryptContext; print(CryptContext(['bcrypt']).hash('your_password'))"
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