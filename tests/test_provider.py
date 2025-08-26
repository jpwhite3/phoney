import unittest

import faker
from faker import Faker
from faker.providers import BaseProvider

from phoney.app.apis import provider


class TestProvider(unittest.TestCase):
    """Test the provider module functionality."""

    def test_is_private_member(self) -> None:
        """Test private member detection."""
        private_member_names = ['_bad', '__worse', 'BaseProvider', 'OrderedDict', '', None]
        for member_name in private_member_names:
            self.assertTrue(provider.is_private_member(member_name), f"{member_name} should be private")

    def test_isnt_private_member(self) -> None:
        """Test public member detection."""
        public_member_names = ['good', 'also_good', 'still_good_']
        for member_name in public_member_names:
            self.assertFalse(provider.is_private_member(member_name), f"{member_name} should be public")

    def test_is_base_provider_attr(self) -> None:
        """Test base provider attribute detection."""
        base_provider_attrs = ['__class__', 'numerify', 'lexify']
        for attr_name in base_provider_attrs:
            self.assertTrue(provider.is_base_provider_attr(attr_name), f"{attr_name} should be a BaseProvider attr")

    def test_isnt_base_provider_attr(self) -> None:
        """Test non-base provider attribute detection."""
        non_base_attrs = ['not_real_attr', 'arbitrary_method']
        for attr_name in non_base_attrs:
            self.assertFalse(provider.is_base_provider_attr(attr_name), f"{attr_name} should not be a BaseProvider attr")

    def test_is_provider(self) -> None:
        """Test provider module detection."""
        # Get a known provider module
        for provider_name in dir(faker.providers):
            if not provider.is_private_member(provider_name):
                module = getattr(faker.providers, provider_name, None)
                if hasattr(module, 'Provider'):
                    self.assertTrue(provider.is_provider(module), f"{provider_name} should be a provider")
                    break

    def test_isnt_provider(self) -> None:
        """Test non-provider module detection."""
        # Test with non-provider objects
        non_providers = [42, "string", {}, [], self]
        for obj in non_providers:
            self.assertFalse(provider.is_provider(obj), f"{type(obj)} should not be a provider")

    def test_get_provider_list(self) -> None:
        """Test provider list retrieval."""
        providers = provider.get_provider_list()
        self.assertIsInstance(providers, list)
        self.assertGreater(len(providers), 0)
        
        # Each provider should be available in faker.providers
        for provider_name in providers:
            self.assertIn(provider_name, dir(faker.providers))
            self.assertFalse(provider.is_private_member(provider_name))

    def test_get_provider(self) -> None:
        """Test getting a provider class."""
        # Test a few known providers
        known_providers = ["person", "address", "company"]
        
        for provider_name in known_providers:
            if provider_name in provider.get_provider_list():
                provider_class = provider.get_provider(provider_name)
                # Create a Faker instance and verify provider works
                fake = Faker()
                provider_instance = provider_class(fake)
                self.assertIsInstance(provider_instance, BaseProvider)

    def test_get_provider_unknown(self) -> None:
        """Test getting an unknown provider raises an error."""
        provider_name = 'NonexistentFakerProvider'
        with self.assertRaises(ValueError):
            provider.get_provider(provider_name)

    def test_get_provider_url_map(self) -> None:
        """Test generation of provider URL map."""
        url_map = provider.get_provider_url_map()
        self.assertIsInstance(url_map, dict)
        self.assertGreater(len(url_map), 0)
        
        for provider_name, url in url_map.items():
            self.assertEqual(f"/provider/{provider_name}", url)

    def test_get_generator_list(self) -> None:
        """Test getting generator list from a provider."""
        # Test a few known providers
        test_providers = ["person", "address"]
        
        for provider_name in test_providers:
            if provider_name in provider.get_provider_list():
                provider_class = provider.get_provider(provider_name)
                generators = provider.get_generator_list(provider_class)
                
                self.assertIsInstance(generators, list)
                self.assertGreater(len(generators), 0)
                
                # Test that generators are callable on a Faker instance
                fake = Faker()
                for gen_name in generators[:3]:  # Test a few generators
                    self.assertTrue(hasattr(fake, gen_name))
                    gen = getattr(fake, gen_name)
                    self.assertTrue(callable(gen))

    def test_get_provider_metadata(self) -> None:
        """Test getting comprehensive provider metadata."""
        metadata = provider.get_provider_metadata()
        self.assertIsInstance(metadata, dict)
        self.assertGreater(len(metadata), 0)
        
        for provider_name, data in list(metadata.items())[:3]:  # Test a few
            self.assertIn('name', data)
            self.assertIn('url', data)
            self.assertIn('generator_count', data)
            self.assertIn('generators', data)
            
            self.assertEqual(provider_name, data['name'])
            self.assertIsInstance(data['generators'], list)
            self.assertEqual(len(data['generators']), data['generator_count'])
