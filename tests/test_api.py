import unittest

from fastapi.testclient import TestClient
from pydantic import TypeAdapter

from phoney.app.apis.models import ProviderDetail, ProviderInfo
from phoney.app.apis.provider import get_generator_list, get_provider, get_provider_list
from phoney.app.main import app

client = TestClient(app)


class TestApi(unittest.TestCase):
    """Test the API endpoints."""

    def test_root_endpoint(self) -> None:
        """Test the root endpoint returns correct API information."""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Phoney - Faker API")
        self.assertEqual(data["status"], "online")
        self.assertIn("version", data)

    def test_endpoint_providers(self) -> None:
        """Test the providers endpoint returns all available providers."""
        response = client.get("/api/v1/providers")
        self.assertEqual(response.status_code, 200)
        
        # Validate response against the model
        providers_adapter = TypeAdapter(list[ProviderInfo])
        providers = providers_adapter.validate_python(response.json())
        
        # Check all expected providers are present
        provider_names = {p.name for p in providers}
        expected_names = set(get_provider_list())
        self.assertTrue(expected_names.issubset(provider_names))
        
        # Check provider info structure
        for provider in providers:
            self.assertTrue(provider.name)
            self.assertTrue(provider.url)
            self.assertGreaterEqual(provider.generator_count, 0)

    def test_endpoint_provider_details(self) -> None:
        """Test the provider detail endpoint for each provider."""
        # Test for a few providers rather than all to speed up tests
        test_providers = list(get_provider_list())[:3]
        
        for provider_name in test_providers:
            response = client.get(f"/api/v1/provider/{provider_name}")
            self.assertEqual(response.status_code, 200)
            
            # Validate response against model
            provider_adapter = TypeAdapter(ProviderDetail)
            provider_detail = provider_adapter.validate_python(response.json())
            
            # Check content
            self.assertEqual(provider_detail.provider, provider_name)
            self.assertIsInstance(provider_detail.generators, list)
            self.assertIsInstance(provider_detail.generator_urls, dict)
            
            # Check generator count
            provider_class = get_provider(provider_name)
            expected_generators = get_generator_list(provider_class)
            self.assertGreaterEqual(len(provider_detail.generators), len(expected_generators))
            
    def test_generate_data(self) -> None:
        """Test generating data with simple parameters."""
        # Choose a reliable generator for testing
        provider_name = "person"
        generator_name = "name"
        
        # Test basic generation
        response = client.get(f"/api/v1/provider/{provider_name}/{generator_name}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["provider"], provider_name)
        self.assertEqual(data["generator"], generator_name)
        self.assertIsNotNone(data["data"])
        self.assertEqual(data["count"], 1)
        
        # Test with count parameter
        response = client.get(f"/api/v1/provider/{provider_name}/{generator_name}?count=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["data"]), 5)
        self.assertEqual(data["count"], 5)
        
    def test_invalid_provider(self) -> None:
        """Test requesting an invalid provider returns 404."""
        response = client.get("/api/v1/provider/invalid_provider")
        self.assertEqual(response.status_code, 422)  # Validation error for invalid enum
        
    def test_invalid_generator(self) -> None:
        """Test requesting an invalid generator returns 404."""
        response = client.get("/api/v1/provider/person/invalid_generator")
        self.assertEqual(response.status_code, 404)
        
    def test_docs_endpoint(self) -> None:
        """Test the documentation endpoints are accessible."""
        response = client.get("/docs")
        self.assertEqual(response.status_code, 200)
        
        response = client.get("/redoc")
        self.assertEqual(response.status_code, 200)
        
        response = client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
