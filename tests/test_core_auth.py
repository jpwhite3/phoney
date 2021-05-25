import unittest
from pydantic import BaseModel
from phoney.app.core import auth


class TestCoreAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass
    
    def test_TokenModel(self) -> None:
        self.assertTrue(issubclass(auth.Token, BaseModel))
    
    def test_TokenDataModel(self) -> None:
        self.assertTrue(issubclass(auth.TokenData, BaseModel))
    
    def test_UserModel(self) -> None:
        self.assertTrue(issubclass(auth.User, BaseModel))
    
    def test_UserInDBModel(self) -> None:
        self.assertTrue(issubclass(auth.UserInDB, BaseModel))
