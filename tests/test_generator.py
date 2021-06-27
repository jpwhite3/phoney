import unittest
from phoney.app.apis import generator
import faker

class TestGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass
    
    def test_is_private_member(self) -> None:
        private_member_names = ['_bad', '__worse', 'BaseProvider', 'OrderedDict']
        for member_name in private_member_names:
            self.assertTrue(generator.is_private_member(member_name))

    def test_isnt_private_member(self) -> None:
        public_member_names = ['good', 'also_good', 'still_good_']
        for member_name in public_member_names:
            self.assertFalse(generator.is_private_member(member_name))

    def test_is_base_provider_attr(self) -> None:
        base_provider_attrs = ['__class__', 'numerify', 'lexify']
        for attr_name in base_provider_attrs:
            self.assertTrue(generator.is_base_provider_attr(attr_name))

    def test_isnt_base_provider_attr(self) -> None:
        base_provider_attrs = ['real_attr', 'arbitrary']
        for attr_name in base_provider_attrs:
            self.assertFalse(generator.is_base_provider_attr(attr_name))

    def test_get_provider_list(self) -> None:
        for provider_name in generator.get_provider_list():
            self.assertIn(provider_name, dir(faker.providers))
            self.assertFalse(generator.is_private_member(provider_name))
