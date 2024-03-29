import unittest
from fastapi.testclient import TestClient
from phoney.app.main import app
from phoney.app.apis.provider import get_provider_list, get_generator_list, get_provider

client = TestClient(app)


class TestApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_endpoint_providers(self):
        response = client.get("/providers")
        self.assertEqual(response.status_code, 200)

        expected_provider_set = set([x for x in get_provider_list()])
        actual_provider_set = set(response.json().keys())
        self.assertEqual(expected_provider_set, actual_provider_set)

    def test_endpoint_provider(self):
        for provider_name in get_provider_list():
            response = client.get("/provider/%s" % provider_name)
            self.assertEqual(response.status_code, 200)

            provider = get_provider(provider_name)
            generators = get_generator_list(provider)
            excepted = {"provider": provider_name, "generators": generators}
            actual = response.json()
            self.assertEqual(excepted, actual)
