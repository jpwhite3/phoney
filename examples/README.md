# 📁 Phoney Testing Examples

This directory contains practical examples of using Phoney for automated testing across different programming languages and testing frameworks.

## 🚀 Quick Start

1. **Start Phoney server:**
   ```bash
   cd .. && poetry run uvicorn phoney.app.main:app --reload
   ```

2. **Choose your framework and run the examples!**

## 📋 Available Examples

### 🐍 Python Examples

#### `pytest_example.py` - pytest Integration
Complete pytest integration showing:
- Basic fake data generation
- International/localized testing
- Bulk data operations
- Reproducible tests with seeds
- Error handling and edge cases
- Performance testing

```bash
# Install dependencies
pip install requests pytest

# Run tests
pytest examples/pytest_example.py -v

# Run with coverage
pytest examples/pytest_example.py --cov
```

**Key Features Demonstrated:**
- `PhoneyClient` helper class for clean integration
- Parameterized tests with different locales
- Fixtures for complex test scenarios
- Performance testing with bulk data
- Reproducible debugging with seeds

### 🟨 JavaScript Examples

#### `jest_example.js` - Jest Integration
JavaScript/Node.js testing with Jest showing:
- Async/await API integration
- Bulk data generation
- International user testing
- Performance testing
- Error handling

```bash
# Install dependencies
npm install axios jest

# Run tests
npm test examples/jest_example.js

# Or with Jest directly
npx jest examples/jest_example.js
```

**Key Features Demonstrated:**
- `PhoneyClient` class for JavaScript
- Promise-based API calls
- Bulk operations with arrays
- E-commerce flow testing
- Reproducible test data

### 🐚 Shell Examples

#### `curl_examples.sh` - curl Integration
Comprehensive curl examples for:
- Basic data generation
- Bulk operations
- Localized data
- Reproducible results
- Error handling
- Discovery and exploration

```bash
# Make executable and run
chmod +x examples/curl_examples.sh
./examples/curl_examples.sh
```

**Perfect for:**
- Quick API testing
- Shell script integration
- CI/CD pipeline testing
- Learning the API
- Debugging and exploration

## 🎯 Common Testing Patterns

### Pattern 1: User Registration Testing
```python
def test_user_registration():
    name = fake('name')
    email = fake('email')
    phone = fake('phone')
    
    user = register_user(name, email, phone)
    assert user.status == 'active'
```

### Pattern 2: International Testing
```python
def test_international_users():
    for locale in ['en_US', 'fr_FR', 'ja_JP']:
        name = fake('name', locale=locale)
        user = create_user(name, fake('email'))
        assert user.id is not None
```

### Pattern 3: Bulk Data Testing
```python
def test_bulk_operations():
    names = fake('name', count=100)
    for name in names:
        user = create_user(name, fake('email'))
        assert user.created == True
```

### Pattern 4: Reproducible Testing
```python
def test_bug_reproduction():
    # Same seed = same data for debugging
    user_data = {
        'name': fake('name', seed=42),
        'email': fake('email', seed=123)
    }
    # Test specific bug scenario
```

## 🔧 Helper Functions

### Python Helper
```python
class PhoneyClient:
    def fake(self, generator, **params):
        url = f"http://localhost:8000/fake/{generator}"
        response = requests.get(url, params=params)
        return response.json()['data']
```

### JavaScript Helper
```javascript
class PhoneyClient {
    async fake(generator, options = {}) {
        const params = new URLSearchParams(options);
        const url = `http://localhost:8000/fake/${generator}?${params}`;
        const response = await axios.get(url);
        return response.data.data;
    }
}
```

### curl Helper
```bash
fake() {
    curl -s "http://localhost:8000/fake/$1?$2" | jq -r '.data'
}

# Usage: fake name "count=5&locale=fr_FR"
```

## 📊 Testing Scenarios

### E-commerce Testing
- User registration/authentication
- Product catalog management
- Order processing
- Payment validation
- Inventory management

### Content Management
- Article creation/editing
- Comment systems
- User-generated content
- Media management
- Search functionality

### API Testing
- Endpoint validation
- Data format testing
- Error handling
- Rate limiting
- Authentication flows

### Performance Testing
- Bulk data processing
- Database operations
- Search performance
- Concurrent user simulation
- Load testing

## 🛠️ Framework Integration

### Supported Test Frameworks
- **Python**: pytest, unittest, nose2, tox
- **JavaScript**: Jest, Mocha, Jasmine, Cypress
- **Java**: JUnit, TestNG, Spock
- **C#**: xUnit, NUnit, MSTest
- **Ruby**: RSpec, Minitest
- **Go**: testing package, Ginkgo
- **PHP**: PHPUnit, Codeception

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Start Phoney Server
  run: |
    poetry run uvicorn phoney.app.main:app &
    sleep 5  # Wait for server to start
    
- name: Run Tests
  run: pytest tests/ -v
```

## 📖 Best Practices

### 1. **Use Helper Classes**
Create reusable client classes to simplify API calls:
```python
phoney = PhoneyClient()
name = phoney.fake('name')  # Clean and simple
```

### 2. **Leverage Seeds for Debugging**
```python
# Reproducible test data for bug reports
user = create_user(fake('name', seed=12345))
```

### 3. **Test with Multiple Locales**
```python
locales = ['en_US', 'fr_FR', 'de_DE', 'ja_JP']
for locale in locales:
    test_with_locale(locale)
```

### 4. **Use Bulk Generation Efficiently**
```python
# Generate 100 users in one API call
names = fake('name', count=100)
emails = fake('email', count=100)
```

### 5. **Handle Errors Gracefully**
```python
try:
    data = fake('custom_generator')
except requests.HTTPError as e:
    # Handle API errors appropriately
    pass
```

## 🔍 Troubleshooting

### Common Issues

**Server not running:**
```bash
curl: (7) Failed to connect to localhost port 8000
# Solution: Start Phoney server first
```

**Invalid generator:**
```json
{"detail": "Generator 'invalid' not found"}
# Solution: Check available generators at /generators
```

**Request timeout:**
```
# Solution: Reduce count parameter or check server load
```

### Debugging Tips

1. **Test API connection:**
   ```bash
   curl http://localhost:8000/fake/name
   ```

2. **Check available generators:**
   ```bash
   curl http://localhost:8000/generators | jq '.[0:10]'
   ```

3. **Validate parameters:**
   ```bash
   curl "http://localhost:8000/fake/name?locale=invalid"
   ```

## 📚 Further Reading

- **[TUTORIAL.md](../TUTORIAL.md)**: Complete beginner tutorial
- **[README.md](../README.md)**: Full API documentation
- **API Docs**: http://localhost:8000/docs (when server running)
- **Interactive Explorer**: http://localhost:8000/redoc

## 🤝 Contributing Examples

Have a great testing example? Please contribute!

1. Create your example file
2. Follow the naming pattern: `{framework}_example.{ext}`
3. Include comprehensive documentation
4. Add entry to this README
5. Submit a pull request

**Example languages/frameworks we'd love to see:**
- Java (JUnit)
- C# (xUnit)
- Ruby (RSpec)
- Go (testing)
- PHP (PHPUnit)
- Cypress (E2E)
- Postman collections
- k6 performance testing

---

Happy testing! 🚀