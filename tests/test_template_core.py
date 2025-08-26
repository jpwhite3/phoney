"""
Essential template system tests - focused on core functionality.

These tests validate the most important template features work correctly:
- Basic template processing
- API endpoints functionality
- Template validation
- Core error handling
"""

import pytest
from fastapi.testclient import TestClient

from phoney.app.apis.template_engine import TemplateEngine
from phoney.app.main import app


class TestTemplateCoreEngine:
    """Test core template engine functionality."""
    
    def test_basic_template_processing(self):
        """Test basic template processing works."""
        engine = TemplateEngine()
        
        template = {
            "name": "{{name}}",
            "email": "{{email}}",
            "age": "{{random_int:min=18,max=80}}"
        }
        
        result = engine.process_template(template, count=3, seed=42)
        
        assert len(result) == 3
        for item in result:
            assert "name" in item
            assert "email" in item  
            assert "age" in item
            assert isinstance(item["age"], int)
            assert 18 <= item["age"] <= 80
    
    def test_array_generation(self):
        """Test array generation functionality."""
        engine = TemplateEngine()
        
        template = {
            "employees": "{{[name]:count=5}}",
            "departments": "{{[word]:count=3}}"
        }
        
        result = engine.process_template(template, count=2)
        
        assert len(result) == 2
        for item in result:
            assert len(item["employees"]) == 5
            assert len(item["departments"]) == 3
    
    def test_nested_objects(self):
        """Test nested object generation."""
        engine = TemplateEngine()
        
        template = {
            "user": {
                "profile": {
                    "name": "{{name}}",
                    "email": "{{email}}"
                },
                "address": {
                    "city": "{{city}}",
                    "country": "{{country}}"
                }
            }
        }
        
        result = engine.process_template(template, count=2)
        
        assert len(result) == 2
        for item in result:
            assert "user" in item
            assert "profile" in item["user"]
            assert "address" in item["user"]
            assert "name" in item["user"]["profile"]
            assert "city" in item["user"]["address"]
    
    def test_template_validation(self):
        """Test template validation functionality."""
        engine = TemplateEngine()
        
        # Valid template
        valid_template = {"name": "{{name}}", "email": "{{email}}"}
        is_valid, errors, warnings = engine.validate_template(valid_template)
        assert is_valid is True
        assert len(errors) == 0
        
        # Invalid template
        invalid_template = {"name": "{{nonexistent_generator}}"}
        is_valid, errors, warnings = engine.validate_template(invalid_template)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_reproducible_results(self):
        """Test that seeds produce reproducible results."""
        engine = TemplateEngine()
        template = {"name": "{{name}}", "email": "{{email}}"}
        
        result1 = engine.process_template(template, count=3, seed=42)
        result2 = engine.process_template(template, count=3, seed=42)
        
        assert result1 == result2


class TestTemplateCoreAPI:
    """Test core template API functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_simple_template_endpoint(self, client):
        """Test the simple /template endpoint works."""
        template_request = {
            "template": {
                "name": "{{name}}",
                "email": "{{email}}"
            },
            "count": 2,
            "seed": 42
        }
        
        response = client.post("/template", json=template_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "generated_count" in data
        assert data["generated_count"] == 2
        assert len(data["data"]) == 2
    
    def test_template_examples_endpoint(self, client):
        """Test the template examples endpoint."""
        response = client.get("/template/examples")
        
        assert response.status_code == 200
        data = response.json()
        # Check that response contains example data
        assert len(data) > 0
        assert "basic_example" in data or "examples" in data
    
    def test_template_validation_errors(self, client):
        """Test template validation error handling."""
        template_request = {
            "template": {
                "invalid": "{{nonexistent_generator}}"
            },
            "count": 1
        }
        
        response = client.post("/template", json=template_request)
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    def test_template_with_parameters(self, client):
        """Test template with generator parameters."""
        template_request = {
            "template": {
                "age": "{{random_int:min=25,max=65}}",
                "price": "{{pydecimal:left_digits=3,right_digits=2}}"
            },
            "count": 1,
            "seed": 42
        }
        
        response = client.post("/template", json=template_request)
        
        assert response.status_code == 200
        data = response.json()
        item = data["data"][0]
        assert 25 <= item["age"] <= 65
        assert isinstance(float(item["price"]), float)


def test_template_integration():
    """Test end-to-end template functionality."""
    # Test the complete workflow
    engine = TemplateEngine()
    
    # 1. Validate template
    template = {
        "user": {
            "name": "{{name}}",
            "email": "{{email}}",
            "orders": "{{[uuid4]:count=3}}"
        }
    }
    
    is_valid, errors, warnings = engine.validate_template(template)
    assert is_valid is True
    
    # 2. Process template
    result = engine.process_template(template, count=2)
    assert len(result) == 2
    
    # 3. Verify structure
    for item in result:
        assert "user" in item
        assert "name" in item["user"]
        assert "email" in item["user"] 
        assert "orders" in item["user"]
        assert len(item["user"]["orders"]) == 3
        
    print("✅ Template integration test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])