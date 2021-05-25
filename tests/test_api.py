import unittest
from phoney.app.apis.api_a.mainmod import main_func as main_func_a
from phoney.app.apis.api_b.mainmod import main_func as main_func_b


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

    def test_func_main_b(self) -> None:
        seed = 500
        result = main_func_b(seed)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("seed"), seed)