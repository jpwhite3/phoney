import unittest, asyncio
from pydantic import BaseModel
from phoney.app.core import auth
from fastapi.testclient import TestClient
from phoney.app.main import app


class TestCoreAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.client = TestClient(app)

    def test_TokenModel(self) -> None:
        self.assertTrue(issubclass(auth.Token, BaseModel))

    def test_TokenDataModel(self) -> None:
        self.assertTrue(issubclass(auth.TokenData, BaseModel))

    def test_UserModel(self) -> None:
        self.assertTrue(issubclass(auth.User, BaseModel))

    def test_UserInDBModel(self) -> None:
        self.assertTrue(issubclass(auth.UserInDB, BaseModel))

    def test_get_password_hash(self):
        test_pwd = 'arbitrary'
        test_pwd_hash = auth.get_password_hash(test_pwd)
        self.assertTrue(auth.verify_password(test_pwd, test_pwd_hash))

    def test_get_user(self):
        test_username = 'ubuntu'
        test_user = auth.get_user(auth.fake_users_db, test_username)
        self.assertIsInstance(test_user, auth.UserInDB)
        self.assertEqual(test_user.username, test_username)

    def test_authenticate_user(self):
        test_username = 'ubuntu'
        test_userpwd = 'debian'
        test_user = auth.authenticate_user(auth.fake_users_db, test_username, test_userpwd)
        self.assertIsInstance(test_user, auth.UserInDB)

    def test_create_access_token(self):
        test_data = {'sub': 'ubuntu'}
        test_access_token = auth.create_access_token(test_data)
        self.assertTrue(test_access_token)

    def test_get_current_user(self):
        test_data = {'sub': 'ubuntu'}
        test_access_token = auth.create_access_token(test_data)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        test_user = loop.run_until_complete(auth.get_current_user(test_access_token))
        self.assertIsInstance(test_user, auth.UserInDB)

    def test_post_token(self):
        formdata = {'username': 'ubuntu', 'password': 'debian'}
        response = self.client.post("/token", data=formdata)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json())
        self.assertIn('token_type', response.json())
        self.assertEqual(response.json()['token_type'], 'bearer')

    def test_invalid_post_token(self):
        formdata = {'username': 'bogus', 'password': 'bogus'}
        response = self.client.post("/token", data=formdata)
        self.assertEqual(response.status_code, 401)
