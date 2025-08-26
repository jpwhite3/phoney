# 📖 Phoney Tutorial: Fake Data for Automated Testing

## Table of Contents
1. [Why Use Fake Data?](#why-use-fake-data)
2. [Getting Started](#getting-started)
3. [Your First API Call](#your-first-api-call)
4. [Essential Test Data Types](#essential-test-data-types)
5. [Testing with Different Programming Languages](#testing-with-different-programming-languages)
6. [Advanced Techniques](#advanced-techniques)
7. [Real-World Examples](#real-world-examples)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Why Use Fake Data?

### The Problem with Hardcoded Test Data

❌ **Bad Practice:**
```python
def test_user_registration():
    # Always the same data - boring and unrealistic
    result = register_user("John Doe", "john@example.com")
    assert result.success == True
```

### The Power of Dynamic Fake Data

✅ **Good Practice:**
```python
def test_user_registration():
    # Fresh, realistic data every time
    name = get_fake_data('name')     # "Sarah Martinez"
    email = get_fake_data('email')   # "sarah.martinez@example.net"
    result = register_user(name, email)
    assert result.success == True
```

### Benefits of Fake Data

- 🎯 **Realistic**: Looks like real user data
- 🔄 **Variable**: Different data each run catches more bugs
- 🔒 **Safe**: No real user information exposed
- ⚡ **Fast**: Generated on-demand, no database needed
- 🌍 **International**: Test with data from any locale
- 📊 **Bulk**: Generate hundreds of records instantly

## Getting Started

### Installation (5 minutes)

```bash
# Clone and setup
git clone https://github.com/jpwhite3/phoney.git
cd phoney
poetry install

# Start the server
poetry run uvicorn phoney.app.main:app --reload

# Test it works
curl http://localhost:8000/fake/name
```

### Your Development Workflow

1. **Start Phoney server** (once per session)
2. **Generate test data** via HTTP requests
3. **Use data in your tests**
4. **Run tests** with fresh data each time

## Your First API Call

### Basic Pattern

```bash
GET http://localhost:8000/fake/{what_you_want}
```

### Try These Examples

```bash
# Generate different types of data
curl http://localhost:8000/fake/name
curl http://localhost:8000/fake/email
curl http://localhost:8000/fake/phone
curl http://localhost:8000/fake/address
curl http://localhost:8000/fake/company

# Get multiple items
curl "http://localhost:8000/fake/email?count=5"

# Get localized data
curl "http://localhost:8000/fake/name?locale=fr_FR"
```

### Understanding Responses

```json
{
  "generator": "name",
  "data": "Jessica Wilson",
  "count": 1,
  "locale": "en_US", 
  "seed": null
}
```

- **generator**: Which Faker generator was used
- **data**: Your fake data (string or array)
- **count**: How many items generated
- **locale**: Language/region used
- **seed**: For reproducible results (null = random)

## Essential Test Data Types

### 👤 User/Person Data

```bash
curl http://localhost:8000/fake/name          # "Michael Johnson"
curl http://localhost:8000/fake/first_name    # "Sarah"
curl http://localhost:8000/fake/last_name     # "Martinez"
curl http://localhost:8000/fake/prefix        # "Dr."
curl http://localhost:8000/fake/suffix        # "Jr."
```

### 📧 Contact Information

```bash
curl http://localhost:8000/fake/email         # "user@example.com"
curl http://localhost:8000/fake/phone         # "555-0123"
curl http://localhost:8000/fake/address       # "123 Main St"
curl http://localhost:8000/fake/city          # "Springfield"
curl http://localhost:8000/fake/state         # "California"
curl http://localhost:8000/fake/country       # "United States"
curl http://localhost:8000/fake/zipcode       # "12345"
```

### 🌐 Internet/Web Data

```bash
curl http://localhost:8000/fake/url           # "https://example.org"
curl http://localhost:8000/fake/domain        # "example.com"
curl http://localhost:8000/fake/username      # "user123"
curl http://localhost:8000/fake/ipv4          # "192.168.1.1"
curl http://localhost:8000/fake/user_agent    # Browser string
```

### 🏢 Business Data

```bash
curl http://localhost:8000/fake/company       # "Tech Solutions Inc"
curl http://localhost:8000/fake/job           # "Software Engineer"
curl http://localhost:8000/fake/catch_phrase  # "Innovative solutions"
curl http://localhost:8000/fake/bs            # Business speak
```

### 💰 Financial Data

```bash
curl http://localhost:8000/fake/credit_card_number  # "4111111111111111"
curl http://localhost:8000/fake/iban               # Bank account
curl http://localhost:8000/fake/currency_code      # "USD"
```

### 📅 Date/Time Data

```bash
curl http://localhost:8000/fake/date          # "2023-05-15"
curl http://localhost:8000/fake/time          # "14:30:22"
curl http://localhost:8000/fake/date_time     # Full timestamp
curl http://localhost:8000/fake/future_date   # Date in future
curl http://localhost:8000/fake/past_date     # Date in past
```

### 📝 Text Content

```bash
curl http://localhost:8000/fake/word          # "amazing"
curl http://localhost:8000/fake/words         # "great innovative solution"  
curl http://localhost:8000/fake/sentence      # "The quick brown fox..."
curl http://localhost:8000/fake/paragraph     # Full paragraph
curl http://localhost:8000/fake/text          # Multiple paragraphs
```

### 🔢 Numbers & IDs

```bash
curl http://localhost:8000/fake/uuid4         # "f47ac10b-58cc-4372-a567-0e02b2c3d479"
curl http://localhost:8000/fake/ssn           # "123-45-6789"
curl http://localhost:8000/fake/ean           # Barcode number
curl http://localhost:8000/fake/isbn          # Book ISBN
```

## Testing with Different Programming Languages

### Python (pytest, unittest)

```python
import requests
import pytest

# Helper function for clean code
def fake(generator, **kwargs):
    params = '&'.join(f'{k}={v}' for k, v in kwargs.items())
    url = f'http://localhost:8000/fake/{generator}?{params}' if params else f'http://localhost:8000/fake/{generator}'
    response = requests.get(url)
    return response.json()['data']

class TestUserManagement:
    def test_create_user(self):
        # Generate realistic test data
        name = fake('name')
        email = fake('email')
        phone = fake('phone')
        
        user = create_user(name, email, phone)
        assert user.id is not None
        assert user.name == name
    
    def test_bulk_user_creation(self):
        # Test with multiple users
        names = fake('name', count=10)
        
        for name in names:
            user = create_user(name, fake('email'))
            assert user.name == name
    
    def test_international_users(self):
        # Test with different locales
        locales = ['en_US', 'fr_FR', 'de_DE', 'ja_JP']
        
        for locale in locales:
            name = fake('name', locale=locale)
            email = fake('email')
            user = create_user(name, email)
            assert len(user.name) > 0
```

### JavaScript/Node.js (Jest, Mocha)

```javascript
const axios = require('axios');

// Helper function
async function fake(generator, options = {}) {
    const params = new URLSearchParams(options);
    const url = `http://localhost:8000/fake/${generator}?${params}`;
    const response = await axios.get(url);
    return response.data.data;
}

describe('User Registration', () => {
    test('should register user with valid data', async () => {
        const userData = {
            name: await fake('name'),
            email: await fake('email'),
            phone: await fake('phone')
        };
        
        const result = await registerUser(userData);
        expect(result.success).toBe(true);
        expect(result.user.email).toBe(userData.email);
    });
    
    test('should handle multiple registrations', async () => {
        const emails = await fake('email', { count: 5 });
        
        for (const email of emails) {
            const name = await fake('name');
            const result = await registerUser({ name, email });
            expect(result.success).toBe(true);
        }
    });
    
    test('should work with reproducible data', async () => {
        const name1 = await fake('name', { seed: 42 });
        const name2 = await fake('name', { seed: 42 });
        
        expect(name1).toBe(name2); // Same seed = same result
    });
});
```

### Java (JUnit)

```java
import org.junit.jupiter.api.Test;
import org.springframework.web.client.RestTemplate;
import java.util.Map;

public class UserServiceTest {
    private final RestTemplate restTemplate = new RestTemplate();
    private final String PHONEY_BASE = "http://localhost:8000/fake";
    
    private String fake(String generator) {
        Map response = restTemplate.getForObject(
            PHONEY_BASE + "/" + generator, Map.class
        );
        return (String) response.get("data");
    }
    
    @Test
    public void testUserCreation() {
        String name = fake("name");
        String email = fake("email");
        String phone = fake("phone");
        
        User user = userService.createUser(name, email, phone);
        
        assertThat(user.getName()).isEqualTo(name);
        assertThat(user.getEmail()).isEqualTo(email);
    }
    
    @Test
    public void testBulkUserCreation() {
        for (int i = 0; i < 10; i++) {
            String name = fake("name");
            String email = fake("email");
            
            User user = userService.createUser(name, email);
            assertThat(user.getId()).isNotNull();
        }
    }
}
```

### C# (.NET, xUnit)

```csharp
using Xunit;
using System.Net.Http;
using System.Text.Json;

public class UserServiceTests
{
    private readonly HttpClient httpClient = new HttpClient();
    private const string PhoneyBase = "http://localhost:8000/fake";
    
    private async Task<string> Fake(string generator)
    {
        var response = await httpClient.GetStringAsync($"{PhoneyBase}/{generator}");
        var json = JsonSerializer.Deserialize<Dictionary<string, object>>(response);
        return json["data"].ToString();
    }
    
    [Fact]
    public async Task CreateUser_WithFakeData_ShouldSucceed()
    {
        // Arrange
        var name = await Fake("name");
        var email = await Fake("email");
        var phone = await Fake("phone");
        
        // Act
        var user = await userService.CreateUserAsync(name, email, phone);
        
        // Assert
        Assert.NotNull(user.Id);
        Assert.Equal(name, user.Name);
        Assert.Equal(email, user.Email);
    }
    
    [Theory]
    [InlineData("en_US")]
    [InlineData("fr_FR")]
    [InlineData("de_DE")]
    public async Task CreateUser_WithDifferentLocales_ShouldWork(string locale)
    {
        var response = await httpClient.GetStringAsync($"{PhoneyBase}/name?locale={locale}");
        var json = JsonSerializer.Deserialize<Dictionary<string, object>>(response);
        var name = json["data"].ToString();
        
        var user = await userService.CreateUserAsync(name, await Fake("email"));
        Assert.NotNull(user);
    }
}
```

## Advanced Techniques

### 1. Reproducible Testing with Seeds

```python
def test_user_registration_deterministic():
    # Same seed = same data every time (great for debugging!)
    name = fake('name', seed=42)        # Always "Allison Hill"
    email = fake('email', seed=123)     # Always "melissagreen@example.net"
    
    user = register_user(name, email)
    assert user.name == "Allison Hill"
```

### 2. Bulk Data Generation

```python
def test_performance_with_many_users():
    # Generate 100 users efficiently
    names = fake('name', count=100)
    emails = fake('email', count=100)
    
    users = []
    for name, email in zip(names, emails):
        users.append(create_user(name, email))
    
    assert len(users) == 100
```

### 3. Localized Testing

```python
def test_international_support():
    locales = {
        'en_US': 'English (US)',
        'fr_FR': 'French', 
        'de_DE': 'German',
        'ja_JP': 'Japanese',
        'es_ES': 'Spanish'
    }
    
    for locale, description in locales.items():
        name = fake('name', locale=locale)
        address = fake('address', locale=locale)
        
        # Test your app handles international data
        user = create_user(name, f"test@example.com")
        user.address = address
        
        assert save_user(user) == True, f"Failed for {description}"
```

### 4. Custom Data Combinations

```python
def generate_complete_user():
    \"\"\"Generate a complete user profile for testing.\"\"\"
    return {
        'personal': {
            'name': fake('name'),
            'birth_date': fake('date_of_birth'),
            'ssn': fake('ssn')
        },
        'contact': {
            'email': fake('email'),
            'phone': fake('phone'),
            'address': fake('address')
        },
        'professional': {
            'company': fake('company'),
            'job': fake('job'),
            'salary': fake('random_int', min=30000, max=150000)
        },
        'account': {
            'username': fake('user_name'),
            'password': fake('password'),
            'uuid': fake('uuid4')
        }
    }

def test_complete_user_flow():
    user_data = generate_complete_user()
    
    # Test registration
    user = register_user(user_data['personal']['name'], 
                        user_data['contact']['email'])
    assert user.id is not None
    
    # Test profile update
    update_profile(user.id, user_data['professional'])
    
    # Test authentication
    login_result = login(user_data['account']['username'], 
                        user_data['account']['password'])
    assert login_result.success == True
```

## Real-World Examples

### Example 1: E-commerce Testing

```python
class TestEcommerceFlow:
    def test_complete_purchase_flow(self):
        # Generate customer data
        customer = {
            'name': fake('name'),
            'email': fake('email'),
            'phone': fake('phone'),
            'address': fake('address'),
            'credit_card': fake('credit_card_number')
        }
        
        # Generate product data  
        product = {
            'name': fake('catch_phrase'),
            'description': fake('text'),
            'price': fake('pydecimal', left_digits=3, right_digits=2),
            'sku': fake('ean')
        }
        
        # Test the flow
        user = register_customer(customer)
        item = create_product(product)
        cart = add_to_cart(user.id, item.id)
        order = checkout(cart, customer['credit_card'])
        
        assert order.status == 'confirmed'
        assert order.total > 0
```

### Example 2: Content Management System

```python
class TestCMS:
    def test_article_creation(self):
        # Generate realistic content
        article_data = {
            'title': fake('catch_phrase'),
            'content': fake('text', max_nb_chars=2000),
            'author': fake('name'),
            'category': fake('word'),
            'tags': fake('words', nb=5),
            'publish_date': fake('future_date')
        }
        
        article = create_article(article_data)
        assert article.id is not None
        assert len(article.content) > 100
    
    def test_comment_system(self):
        # Create article and comments
        article = create_article({
            'title': fake('sentence'),
            'content': fake('paragraph')
        })
        
        # Generate multiple comments
        comments = []
        for _ in range(5):
            comment = add_comment(article.id, {
                'author': fake('name'),
                'content': fake('paragraph'),
                'email': fake('email')
            })
            comments.append(comment)
        
        assert len(get_comments(article.id)) == 5
```

### Example 3: API Integration Testing

```python
class TestAPIIntegration:
    def test_user_api_endpoints(self):
        base_url = "https://api.myservice.com"
        
        # Test user creation endpoint
        user_data = {
            'name': fake('name'),
            'email': fake('email'),
            'age': fake('random_int', min=18, max=80),
            'country': fake('country')
        }
        
        response = requests.post(f"{base_url}/users", json=user_data)
        assert response.status_code == 201
        
        created_user = response.json()
        assert created_user['email'] == user_data['email']
        
        # Test user retrieval
        user_id = created_user['id']
        response = requests.get(f"{base_url}/users/{user_id}")
        assert response.status_code == 200
        
        # Test user update
        updated_data = {'name': fake('name')}
        response = requests.patch(f"{base_url}/users/{user_id}", json=updated_data)
        assert response.status_code == 200
```

## Best Practices

### 1. Create Helper Functions

```python
# Good: Reusable helper
def create_test_user(**overrides):
    default_data = {
        'name': fake('name'),
        'email': fake('email'),
        'phone': fake('phone'),
        'address': fake('address')
    }
    default_data.update(overrides)
    return register_user(**default_data)

# Usage
user1 = create_test_user()                    # All fake data
user2 = create_test_user(email="admin@test.com")  # Override email
```

### 2. Use Seeds for Debugging

```python
def test_bug_reproduction():
    # Use specific seed to reproduce exact bug scenario
    user_data = {
        'name': fake('name', seed=12345),      # Reproducible
        'email': fake('email', seed=12345),
        'age': fake('random_int', seed=12345, min=1, max=120)
    }
    
    # This will always generate the same data for debugging
    result = problematic_function(user_data)
    assert result.is_valid() == True
```

### 3. Test Edge Cases

```python
def test_edge_cases():
    # Test with very long names
    long_name = fake('text', max_nb_chars=255)
    user = create_user(long_name, fake('email'))
    
    # Test with special characters (if available)
    special_email = fake('email')  # May contain special chars
    user = create_user(fake('name'), special_email)
    
    # Test with different locales for edge cases
    chinese_name = fake('name', locale='zh_CN')
    arabic_name = fake('name', locale='ar_SA')
```

### 4. Performance Testing

```python
def test_bulk_operations():
    # Generate large datasets efficiently
    users_data = []
    names = fake('name', count=1000)
    emails = fake('email', count=1000)
    
    for name, email in zip(names, emails):
        users_data.append({'name': name, 'email': email})
    
    start_time = time.time()
    result = bulk_create_users(users_data)
    duration = time.time() - start_time
    
    assert len(result) == 1000
    assert duration < 10  # Should complete within 10 seconds
```

### 5. Cleanup and Isolation

```python
class TestWithCleanup:
    def setup_method(self):
        self.test_users = []
    
    def teardown_method(self):
        # Clean up test data
        for user in self.test_users:
            delete_user(user.id)
    
    def test_user_creation(self):
        user = create_user(fake('name'), fake('email'))
        self.test_users.append(user)  # Track for cleanup
        
        assert user.id is not None
```

## Troubleshooting

### Common Issues

**1. Connection Refused**
```bash
curl: (7) Failed to connect to localhost port 8000: Connection refused
```
**Solution:** Make sure Phoney server is running:
```bash
poetry run uvicorn phoney.app.main:app --reload
```

**2. Generator Not Found**
```json
{
  "detail": "Generator 'fake_name' not found. Did you mean: name, last_name?"
}
```
**Solution:** Use correct generator name or check available generators:
```bash
curl http://localhost:8000/generators | grep -i name
```

**3. Invalid Locale**
```json
{
  "detail": "Error generating data: Invalid locale 'invalid_locale'"
}
```
**Solution:** Use valid locale codes like `en_US`, `fr_FR`, `de_DE`, etc.

**4. Count Too High**
```json
{
  "detail": "count: ensure this value is less than or equal to 100"
}
```
**Solution:** Reduce count to 100 or less, or make multiple requests.

### Debugging Tips

**1. Check Available Generators**
```bash
# List all generators
curl http://localhost:8000/generators

# Search for specific type
curl http://localhost:8000/generators | grep -i email
```

**2. Test Generator Before Use**
```bash
# Test if generator works
curl http://localhost:8000/fake/your_generator
```

**3. Use Seeds for Consistent Results**
```bash
# Always returns same result for debugging
curl "http://localhost:8000/fake/name?seed=42"
```

**4. Check Server Logs**
```bash
# Server will show detailed error information
poetry run uvicorn phoney.app.main:app --reload --log-level debug
```

### Getting Help

- **📖 Full API Documentation:** http://localhost:8000/docs
- **🔍 Interactive API Explorer:** http://localhost:8000/redoc  
- **📋 Available Generators:** http://localhost:8000/generators
- **🐛 Report Issues:** https://github.com/jpwhite3/phoney/issues

## Next Steps

Congratulations! You now know how to:
- ✅ Generate realistic fake data for testing
- ✅ Use different data types (names, emails, addresses, etc.)
- ✅ Create reproducible tests with seeds
- ✅ Test with international data using locales
- ✅ Integrate with various testing frameworks
- ✅ Follow best practices for test data management

### Advanced Topics to Explore
- Custom Faker providers
- Database seeding with fake data
- Performance testing with bulk generation
- API testing automation
- Continuous integration with fake data

Happy testing! 🚀