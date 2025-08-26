"""
Example: Using Phoney with pytest for automated testing
Run with: pytest examples/pytest_example.py -v
"""

import requests
import pytest
from typing import Dict, List, Any

# Configuration
PHONEY_BASE_URL = "http://localhost:8000"

class PhoneyClient:
    """Simple client for Phoney API."""
    
    def __init__(self, base_url: str = PHONEY_BASE_URL):
        self.base_url = base_url
    
    def fake(self, generator: str, **params) -> Any:
        """Get fake data from Phoney API."""
        url = f"{self.base_url}/fake/{generator}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()['data']
    
    def fake_bulk(self, generator: str, count: int, **params) -> List[Any]:
        """Get multiple fake data items."""
        return self.fake(generator, count=count, **params)

# Global client instance
phoney = PhoneyClient()

# Mock functions representing your application code
def register_user(name: str, email: str, phone: str = None) -> Dict:
    """Mock user registration function."""
    if not name or not email:
        raise ValueError("Name and email required")
    if "@" not in email:
        raise ValueError("Invalid email format")
    
    return {
        "id": hash(email) % 10000,  # Mock ID generation
        "name": name,
        "email": email,
        "phone": phone,
        "status": "active"
    }

class TestUserRegistration:
    """Test user registration with realistic fake data."""
    
    def test_valid_user_registration(self):
        """Test registering a user with valid fake data."""
        name = phoney.fake('name')
        email = phoney.fake('email')
        phone = phoney.fake('phone')
        
        user = register_user(name, email, phone)
        
        assert user['name'] == name
        assert user['email'] == email
        assert user['phone'] == phone
        assert user['status'] == 'active'
        assert user['id'] > 0
    
    def test_international_users(self):
        """Test registration with users from different locales."""
        locales = ['en_US', 'fr_FR', 'de_DE', 'ja_JP', 'es_ES']
        
        for locale in locales:
            name = phoney.fake('name', locale=locale)
            email = phoney.fake('email')
            
            user = register_user(name, email)
            assert user['name'] == name
            assert len(user['name']) > 0
    
    def test_reproducible_user_data(self):
        """Test that same seed produces same data (great for debugging)."""
        # Same seed should produce same results
        name1 = phoney.fake('name', seed=42)
        email1 = phoney.fake('email', seed=123)
        
        name2 = phoney.fake('name', seed=42)
        email2 = phoney.fake('email', seed=123)
        
        assert name1 == name2
        assert email1 == email2

if __name__ == "__main__":
    print("Run with: pytest examples/pytest_example.py -v")