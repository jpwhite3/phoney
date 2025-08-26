"""
Integration tests for the Phoney template API endpoints.

Tests cover:
- Simple template API (POST /template)
- Advanced template API (POST /api/v1/template/generate) 
- Template validation API (POST /api/v1/template/validate)
- Template examples API (GET /template/examples)
- Error handling and authentication
- Performance with realistic workloads
"""

import time

import pytest
from fastapi.testclient import TestClient


class TestSimpleTemplateAPI:
    """Test the simple template API endpoint (/template)."""
    
    def test_simple_template_generation(self, client: TestClient):
        """Test basic template generation."""
        template_request = {
            "template": {
                "name": "{{name}}",
                "email": "{{email}}",
                "age": "{{random_int:min=18,max=80}}"
            },
            "count": 5,
            "seed": 42
        }
        
        response = client.post("/template", json=template_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["generated_count"] == 5
        assert data["requested_count"] == 5
        assert data["format"] == "json"
        assert data["locale"] == "en_US"
        assert data["seed"] == 42
        assert len(data["data"]) == 5
        
        # Verify data structure
        for record in data["data"]:
            assert "name" in record
            assert "email" in record
            assert "age" in record
            assert isinstance(record["name"], str)
            assert "@" in record["email"]
            assert 18 <= record["age"] <= 80
    
    def test_simple_template_with_arrays(self, client: TestClient):
        """Test template generation with arrays."""
        template_request = {
            "template": {
                "company": "{{company}}",
                "employees": "{{[name]:count=3}}",
                "departments": "{{[word]:count=2}}"
            },
            "count": 2
        }
        
        response = client.post("/template", json=template_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 2
        for record in data["data"]:
            assert isinstance(record["employees"], list)
            assert len(record["employees"]) == 3
            assert isinstance(record["departments"], list)
            assert len(record["departments"]) == 2
    
    def test_simple_template_nested_objects(self, client: TestClient):
        """Test template generation with nested objects."""
        template_request = {
            "template": {
                "user": {
                    "profile": {
                        "name": "{{name}}",
                        "email": "{{email}}"
                    },
                    "address": {
                        "street": "{{street_address}}",
                        "city": "{{city}}"
                    }
                },
                "metadata": {
                    "created": "{{date_time}}",
                    "active": "{{pybool}}"
                }
            },
            "count": 1
        }
        
        response = client.post("/template", json=template_request)
        
        assert response.status_code == 200
        data = response.json()
        
        record = data["data"][0]
        assert "user" in record
        assert "profile" in record["user"]
        assert "address" in record["user"]
        assert "name" in record["user"]["profile"]
        assert "email" in record["user"]["profile"]
        assert "street" in record["user"]["address"]
        assert "city" in record["user"]["address"]
        assert "metadata" in record
        assert "created" in record["metadata"]
    
    def test_simple_template_with_locale(self, client: TestClient):
        """Test template generation with different locales."""
        locales = ["en_US", "fr_FR", "de_DE", "es_ES"]
        
        for locale in locales:
            template_request = {
                "template": {
                    "name": "{{name}}",
                    "address": "{{address}}"
                },
                "count": 1,
                "locale": locale
            }
            
            response = client.post("/template", json=template_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["locale"] == locale
            assert len(data["data"]) == 1
    
    def test_simple_template_reproducibility(self, client: TestClient):
        """Test that same seed produces same results."""
        template_request = {
            "template": {
                "name": "{{name}}",
                "number": "{{random_int:min=1,max=1000}}"
            },
            "count": 3,
            "seed": 123
        }
        
        # Make same request twice
        response1 = client.post("/template", json=template_request)
        response2 = client.post("/template", json=template_request)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["data"] == data2["data"], "Same seed should produce identical results"
    
    def test_simple_template_count_limit(self, client: TestClient):
        """Test count limit for unauthenticated requests."""
        template_request = {
            "template": {"name": "{{name}}"},
            "count": 1001  # Over the limit
        }
        
        response = client.post("/template", json=template_request)
        
        assert response.status_code == 400
        assert "maximum count" in response.json()["detail"].lower()
    
    def test_simple_template_validation_errors(self, client: TestClient):
        """Test template validation error handling."""
        template_request = {
            "template": {
                "name": "{{name}}",
                "invalid": "{{nonexistent_generator}}"
            },
            "count": 1
        }
        
        response = client.post("/template", json=template_request)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "template validation failed" in error_data["detail"]["message"].lower()
        assert "errors" in error_data["detail"]
        assert len(error_data["detail"]["errors"]) > 0
        
        # Should include suggestions
        error = error_data["detail"]["errors"][0]
        assert "suggestions" in error
        assert isinstance(error["suggestions"], list)
    
    def test_simple_template_empty_template(self, client: TestClient):
        """Test error handling for empty template."""
        template_request = {
            "template": {},
            "count": 1
        }
        
        response = client.post("/template", json=template_request)
        
        assert response.status_code == 422
    
    def test_simple_template_malformed_request(self, client: TestClient):
        """Test error handling for malformed requests."""
        # Missing template field
        response = client.post("/template", json={"count": 1})
        assert response.status_code == 422
        
        # Invalid count
        response = client.post("/template", json={"template": {"name": "{{name}}"}, "count": 0})
        assert response.status_code == 422
        
        # Invalid JSON
        response = client.post("/template", data="invalid json", headers={"Content-Type": "application/json"})
        assert response.status_code == 422


class TestAdvancedTemplateAPI:
    """Test the advanced template API endpoint (/api/v1/template/generate)."""
    
    def test_advanced_template_generation(self, client: TestClient, auth_headers: dict[str, str]):
        """Test advanced template generation with authentication."""
        template_request = {
            "template": {
                "name": "{{name}}",
                "email": "{{email}}"
            },
            "count": 10,
            "format": "json",
            "unique": False
        }
        
        response = client.post("/api/v1/template/generate", json=template_request, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["generated_count"] == 10
        assert data["format"] == "json"
        assert "execution_time_ms" in data
        assert isinstance(data["execution_time_ms"], int | float)
        assert len(data["data"]) == 10
    
    def test_advanced_template_csv_format(self, client: TestClient, auth_headers: dict[str, str]):
        """Test CSV format output."""
        template_request = {
            "template": {
                "name": "{{name}}",
                "email": "{{email}}",
                "age": "{{random_int:min=25,max=65}}"
            },
            "count": 5,
            "format": "csv"
        }
        
        response = client.post("/api/v1/template/generate", json=template_request, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["format"] == "csv"
        assert isinstance(data["data"], str)
        
        # Verify CSV structure
        csv_lines = data["data"].strip().split('\n')
        assert len(csv_lines) > 5  # Header + 5 data rows
        assert "name,email,age" in csv_lines[0] or "name" in csv_lines[0]  # Header row
    
    def test_advanced_template_large_dataset(self, client: TestClient, auth_headers: dict[str, str]):
        """Test generation of larger datasets (advanced endpoint only)."""
        template_request = {
            "template": {
                "id": "{{uuid4}}",
                "name": "{{name}}",
                "email": "{{email}}"
            },
            "count": 2000  # Large dataset
        }
        
        response = client.post("/api/v1/template/generate", json=template_request, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["generated_count"] == 2000
        assert len(data["data"]) == 2000
    
    def test_advanced_template_unique_values(self, client: TestClient, auth_headers: dict[str, str]):
        """Test unique value generation."""
        template_request = {
            "template": {
                "email": "{{email}}"
            },
            "count": 50,
            "unique": True
        }
        
        response = client.post("/api/v1/template/generate", json=template_request, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for uniqueness
        emails = [record["email"] for record in data["data"]]
        assert len(set(emails)) == len(emails), "All emails should be unique"
    
    def test_advanced_template_without_auth(self, client: TestClient):
        """Test advanced endpoint without authentication."""
        template_request = {
            "template": {"name": "{{name}}"},
            "count": 1
        }
        
        response = client.post("/api/v1/template/generate", json=template_request)
        
        assert response.status_code == 401  # Unauthorized


class TestTemplateValidationAPI:
    """Test the template validation API endpoint."""
    
    def test_validate_valid_template(self, client: TestClient):
        """Test validation of a valid template."""
        validation_request = {
            "template": {
                "name": "{{name}}",
                "email": "{{email}}",
                "age": "{{random_int:min=18,max=80}}"
            }
        }
        
        response = client.post("/api/v1/template/validate", json=validation_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is True
        assert len(data["errors"]) == 0
        assert "detected_fields" in data
        assert len(data["detected_fields"]) == 3
        
        # Check detected fields
        generators = {field["generator"] for field in data["detected_fields"]}
        assert generators == {"name", "email", "random_int"}
    
    def test_validate_invalid_template(self, client: TestClient):
        """Test validation of template with errors."""
        validation_request = {
            "template": {
                "name": "{{name}}",
                "invalid": "{{nonexistent_generator}}",
                "bad_params": "{{random_int:invalid_param=true}}"
            }
        }
        
        response = client.post("/api/v1/template/validate", json=validation_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is False
        assert len(data["errors"]) > 0
        
        # Check error details
        for error in data["errors"]:
            assert "field" in error
            assert "generator" in error
            assert "message" in error
            if error["generator"] == "nonexistent_generator":
                assert "suggestions" in error
                assert isinstance(error["suggestions"], list)
    
    def test_validate_with_strict_mode(self, client: TestClient):
        """Test validation with strict mode enabled."""
        validation_request = {
            "template": {
                "name": "{{name}}",
                "questionable": "{{word}}"  # Valid but might trigger warnings in strict mode
            },
            "strict": True
        }
        
        response = client.post("/api/v1/template/validate", json=validation_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still be valid, but might have more warnings in strict mode
        assert isinstance(data["valid"], bool)
        assert isinstance(data["warnings"], list)
    
    def test_validate_empty_template(self, client: TestClient):
        """Test validation of empty template."""
        validation_request = {
            "template": {}
        }
        
        response = client.post("/api/v1/template/validate", json=validation_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is False
        assert len(data["errors"]) > 0


class TestTemplateExamplesAPI:
    """Test the template examples API endpoints."""
    
    def test_simple_template_examples(self, client: TestClient):
        """Test simple template examples endpoint."""
        response = client.get("/template/examples")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "basic_example" in data
        assert "array_example" in data
        assert "syntax_guide" in data
        assert "quick_start" in data
        
        # Verify example structure
        basic_example = data["basic_example"]
        assert "template" in basic_example
        assert "count" in basic_example
        
        # Verify syntax guide
        syntax_guide = data["syntax_guide"]
        assert "simple_placeholder" in syntax_guide
        assert "with_parameters" in syntax_guide
        assert "arrays" in syntax_guide
    
    def test_advanced_template_examples(self, client: TestClient):
        """Test advanced template examples endpoint."""
        response = client.get("/api/v1/template/examples")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "examples" in data
        assert "syntax_help" in data
        assert "documentation" in data
        
        # Check examples
        examples = data["examples"]
        assert "basic_user_template" in examples
        assert "ecommerce_template" in examples
        assert "array_template" in examples
        assert "localized_template" in examples
        
        # Verify example structure
        for _example_name, example_data in examples.items():
            assert "description" in example_data
            assert "template" in example_data
            assert "count" in example_data


class TestTemplatePerformance:
    """Test template API performance."""
    
    def test_simple_template_performance(self, client: TestClient):
        """Test performance of simple template generation."""
        template_request = {
            "template": {
                "name": "{{name}}",
                "email": "{{email}}",
                "phone": "{{phone}}"
            },
            "count": 100
        }
        
        start_time = time.time()
        response = client.post("/template", json=template_request)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["generated_count"] == 100
        assert duration < 2.0, f"Simple template took too long: {duration:.3f}s"
        
        # Verify server-reported execution time
        assert data["execution_time_ms"] > 0
        assert data["execution_time_ms"] < 2000  # Less than 2 seconds
    
    def test_complex_template_performance(self, client: TestClient):
        """Test performance of complex nested template."""
        template_request = {
            "template": {
                "user": {
                    "id": "{{uuid4}}",
                    "profile": {
                        "name": "{{name}}",
                        "email": "{{email}}",
                        "phone": "{{phone}}",
                        "address": {
                            "street": "{{street_address}}",
                            "city": "{{city}}",
                            "state": "{{state}}",
                            "country": "{{country}}"
                        }
                    }
                },
                "orders": {
                    "recent": "{{[catch_phrase]:count=5}}",
                    "total_spent": "{{pydecimal:left_digits=4,right_digits=2}}"
                },
                "preferences": {
                    "theme": "{{word}}",
                    "notifications": {
                        "email": "{{pybool}}",
                        "sms": "{{pybool}}"
                    }
                }
            },
            "count": 50
        }
        
        start_time = time.time()
        response = client.post("/template", json=template_request)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["generated_count"] == 50
        assert duration < 5.0, f"Complex template took too long: {duration:.3f}s"
    
    def test_validation_performance(self, client: TestClient):
        """Test performance of template validation."""
        validation_request = {
            "template": {
                f"field_{i}": "{{name}}" for i in range(20)  # 20 fields
            }
        }
        
        start_time = time.time()
        for _ in range(50):  # Validate 50 times
            response = client.post("/api/v1/template/validate", json=validation_request)
            assert response.status_code == 200
        duration = time.time() - start_time
        
        assert duration < 2.0, f"Validation took too long: {duration:.3f}s for 50 validations"


class TestTemplateErrorHandling:
    """Test comprehensive error handling."""
    
    def test_request_validation_errors(self, client: TestClient):
        """Test various request validation errors."""
        # Invalid count values
        invalid_requests = [
            {"template": {"name": "{{name}}"}, "count": 0},     # Count too low
            {"template": {"name": "{{name}}"}, "count": -1},    # Negative count
            {"template": {"name": "{{name}}"}, "count": 10001}, # Count too high (simple endpoint)
            {"count": 5},                                       # Missing template
            {"template": {}},                                   # Empty template
        ]
        
        for invalid_request in invalid_requests:
            response = client.post("/template", json=invalid_request)
            assert response.status_code in [400, 422], f"Should reject: {invalid_request}"
    
    def test_generator_error_handling(self, client: TestClient):
        """Test handling of generator-related errors."""
        template_request = {
            "template": {
                "valid": "{{name}}",
                "invalid": "{{totally_fake_generator}}",
                "malformed": "{{name:invalid=param}}"
            },
            "count": 1
        }
        
        response = client.post("/template", json=template_request)
        
        # Should return validation error
        assert response.status_code == 422
        error_data = response.json()
        assert "validation failed" in error_data["detail"]["message"].lower()
    
    def test_large_request_handling(self, client: TestClient):
        """Test handling of unusually large requests."""
        # Very large template structure
        large_template = {}
        for i in range(100):  # 100 fields
            large_template[f"field_{i}"] = "{{name}}"
        
        template_request = {
            "template": large_template,
            "count": 10
        }
        
        response = client.post("/template", json=template_request)
        
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 400, 422, 500]
    
    def test_concurrent_requests(self, client: TestClient):
        """Test handling of concurrent template requests."""
        import queue
        import threading
        
        template_request = {
            "template": {
                "name": "{{name}}",
                "email": "{{email}}"
            },
            "count": 10
        }
        
        results = queue.Queue()
        
        def make_request():
            response = client.post("/template", json=template_request)
            results.put(response.status_code)
        
        # Launch 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        assert len(status_codes) == 10
        # Most should succeed
        success_count = sum(1 for code in status_codes if code == 200)
        assert success_count >= 8, f"Too many failures in concurrent requests: {status_codes}"


class TestTemplateIntegration:
    """Integration tests combining multiple template features."""
    
    def test_full_workflow_simple_api(self, client: TestClient):
        """Test complete workflow using simple API."""
        # 1. Get examples
        examples_response = client.get("/template/examples")
        assert examples_response.status_code == 200
        examples = examples_response.json()
        
        # 2. Use basic example
        basic_template = examples["basic_example"]
        response = client.post("/template", json=basic_template)
        assert response.status_code == 200
        
        # 3. Verify generated data
        data = response.json()
        assert data["generated_count"] == basic_template["count"]
        assert len(data["data"]) == basic_template["count"]
    
    def test_full_workflow_advanced_api(self, client: TestClient, auth_headers: dict[str, str]):
        """Test complete workflow using advanced API."""
        # 1. Get advanced examples
        examples_response = client.get("/api/v1/template/examples")
        assert examples_response.status_code == 200
        examples = examples_response.json()
        
        # 2. Validate a complex template
        ecommerce_template = examples["examples"]["ecommerce_template"]
        validation_response = client.post(
            "/api/v1/template/validate", 
            json={"template": ecommerce_template["template"]}
        )
        assert validation_response.status_code == 200
        assert validation_response.json()["valid"] is True
        
        # 3. Generate data with advanced features
        advanced_request = {
            "template": ecommerce_template["template"],
            "count": 10,
            "format": "json",
            "unique": True
        }
        generate_response = client.post(
            "/api/v1/template/generate",
            json=advanced_request,
            headers=auth_headers
        )
        assert generate_response.status_code == 200
        
        # 4. Verify advanced features
        data = generate_response.json()
        assert data["format"] == "json"
        assert data["generated_count"] == 10
        assert "execution_time_ms" in data


# Parametrized tests for different template types
@pytest.mark.parametrize("template_name,template_data", [
    ("simple", {"name": "{{name}}", "email": "{{email}}"}),
    ("parameterized", {"age": "{{random_int:min=18,max=80}}", "price": "{{pydecimal:left_digits=3,right_digits=2}}"}),
    ("arrays", {"employees": "{{[name]:count=5}}", "departments": "{{[word]:count=3}}"}),
    ("mixed", {"name": "{{name}}", "friends": "{{[name]:count=2}}", "age": "{{random_int:min=25,max=65}}"}),
])
def test_template_types(client: TestClient, template_name: str, template_data: dict):
    """Test different types of templates."""
    template_request = {
        "template": template_data,
        "count": 2,
        "seed": 42
    }
    
    response = client.post("/template", json=template_request)
    
    assert response.status_code == 200, f"Template type '{template_name}' failed"
    data = response.json()
    assert data["generated_count"] == 2
    assert len(data["data"]) == 2


# Load test fixtures
@pytest.fixture
def performance_template():
    """Provide a template for performance testing."""
    return {
        "user": {
            "id": "{{uuid4}}",
            "profile": {
                "name": "{{name}}",
                "email": "{{email}}",
                "phone": "{{phone}}",
                "birth_date": "{{date_of_birth}}"
            },
            "address": {
                "street": "{{street_address}}",
                "city": "{{city}}",
                "state": "{{state}}",
                "country": "{{country}}",
                "zip": "{{zipcode}}"
            }
        },
        "account": {
            "balance": "{{pydecimal:left_digits=4,right_digits=2}}",
            "created": "{{date_between:start_date=-2y,end_date=today}}",
            "active": "{{pybool}}"
        },
        "preferences": {
            "theme": "{{word}}",
            "language": "{{language_code}}",
            "notifications": {
                "email": "{{pybool}}",
                "sms": "{{pybool}}",
                "push": "{{pybool}}"
            }
        }
    }


def test_realistic_workload(client: TestClient, performance_template: dict):
    """Test with realistic production-like workload."""
    template_request = {
        "template": performance_template,
        "count": 100,
        "locale": "en_US",
        "seed": 12345
    }
    
    start_time = time.time()
    response = client.post("/template", json=template_request)
    duration = time.time() - start_time
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["generated_count"] == 100
    assert duration < 3.0, f"Realistic workload took too long: {duration:.3f}s"
    
    # Verify data quality
    sample_record = data["data"][0]
    assert "user" in sample_record
    assert "account" in sample_record
    assert "preferences" in sample_record
    assert "profile" in sample_record["user"]
    assert "address" in sample_record["user"]