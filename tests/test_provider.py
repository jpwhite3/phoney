import unittest

import faker

from faker.providers import BaseProvider
from phoney.app.apis import provider


class TestGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_is_private_member(self) -> None:
        private_member_names = ['_bad', '__worse', 'BaseProvider', 'OrderedDict']
        for member_name in private_member_names:
            self.assertTrue(provider.is_private_member(member_name))

    def test_isnt_private_member(self) -> None:
        public_member_names = ['good', 'also_good', 'still_good_']
        for member_name in public_member_names:
            self.assertFalse(provider.is_private_member(member_name))

    def test_is_base_provider_attr(self) -> None:
        base_provider_attrs = ['__class__', 'numerify', 'lexify']
        for attr_name in base_provider_attrs:
            self.assertTrue(provider.is_base_provider_attr(attr_name))

    def test_isnt_base_provider_attr(self) -> None:
        base_provider_attrs = ['real_attr', 'arbitrary']
        for attr_name in base_provider_attrs:
            self.assertFalse(provider.is_base_provider_attr(attr_name))

    def test_get_provider_list(self) -> None:
        for provider_name in provider.get_provider_list():
            self.assertIn(provider_name, dir(faker.providers))
            self.assertFalse(provider.is_private_member(provider_name))

    def test_get_provider(self) -> None:
        self.assertGreater(len(provider.get_provider_list()), 0)
        for provider_name in provider.get_provider_list():
            prov = provider.get_provider(provider_name)
            self.assertIsInstance(prov(''), BaseProvider)

    def test_get_provider_unknown(self) -> None:
        provider_name = 'ArbitraryNonexistantProvider'
        with self.assertRaises(LookupError):
            provider.get_provider(provider_name)

    def test_get_provider_url_map(self) -> None:
        self.assertGreater(len(provider.get_provider_url_map()), 0)
        for provider_name, url in provider.get_provider_url_map().items():
            expected_url = "/provider/%s" % provider_name
            self.assertEqual(expected_url, url)

    def test_get_generator_list(self) -> None:
        for provider_name in provider.get_provider_list():
            prov = provider.get_provider(provider_name)
            generators = provider.get_generator_list(prov)
            self.assertGreater(len(generators), 0)
