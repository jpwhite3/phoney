import unittest
from phoney.app.apis.api_a.mainmod import main_func as main_func_a


class TestApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass
    
    def test_func_main_a(self) -> None:
        seed = 420
        result = main_func_a(seed)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("seed"), seed)
