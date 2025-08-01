import unittest
import asyncio
from unittest.mock import patch

from pydantic import BaseModel
from fastapi.testclient import TestClient
jwt_mock = unittest.mock.MagicMock()

from phoney.app.core import auth
from phoney.app.main import app
from phoney.app.core.config import settings


class TestCoreAuth(unittest.TestCase):
    """Test the authentication system."""

    def setUp(self) -> None:
        """Set up test client and mock users."""
        self.client = TestClient(app)
        # Create a test user for authentication tests
        self.test_username = "api_user"
        self.test_password = "test_password"
        self.test_hash = auth.get_password_hash(self.test_password)
        
        # Mock the users_db for testing
        self.test_users_db = {
            self.test_username: {
                "username": self.test_username,
                "hashed_password": self.test_hash
            }
        }

    def test_token_model(self) -> None:
        """Test Token model inherits from BaseModel."""
        self.assertTrue(issubclass(auth.Token, BaseModel))
        # Test model instantiation
        token = auth.Token(access_token="test_token", token_type="bearer")
        self.assertEqual(token.access_token, "test_token")
        self.assertEqual(token.token_type, "bearer")

    def test_token_data_model(self) -> None:
        """Test TokenData model inherits from BaseModel."""
        self.assertTrue(issubclass(auth.TokenData, BaseModel))
        # Test with and without username
        token_data = auth.TokenData(username="test_user")
        self.assertEqual(token_data.username, "test_user")
        
        empty_token_data = auth.TokenData()
        self.assertIsNone(empty_token_data.username)

    def test_user_model(self) -> None:
        """Test User model inherits from BaseModel."""
        self.assertTrue(issubclass(auth.User, BaseModel))
        # Test model instantiation
        user = auth.User(username="test_user")
        self.assertEqual(user.username, "test_user")
        self.assertIsNone(user.disabled)

    def test_user_in_db_model(self) -> None:
        """Test UserInDB model inherits from User and BaseModel."""
        self.assertTrue(issubclass(auth.UserInDB, auth.User))
        self.assertTrue(issubclass(auth.UserInDB, BaseModel))
        # Test model instantiation
        user = auth.UserInDB(
            username="test_user", 
            hashed_password="test_hash"
        )
        self.assertEqual(user.username, "test_user")
        self.assertEqual(user.hashed_password, "test_hash")

    def test_password_hashing(self) -> None:
        """Test password hashing and verification."""
        test_pwd = "secure_password"
        test_pwd_hash = auth.get_password_hash(test_pwd)
        # Hash should be different from original password
        self.assertNotEqual(test_pwd, test_pwd_hash)
        # Verification should work
        self.assertTrue(auth.verify_password(test_pwd, test_pwd_hash))
        # Incorrect password should not verify
        self.assertFalse(auth.verify_password("wrong_password", test_pwd_hash))

    def test_get_user(self) -> None:
        """Test retrieving a user from the database."""
        # Test with patch to use test users
        with patch.object(auth, "users_db", self.test_users_db):
            # Valid user should be retrieved
            test_user = auth.get_user(self.test_users_db, self.test_username)
            self.assertIsInstance(test_user, auth.UserInDB)
            self.assertEqual(test_user.username, self.test_username)
            
            # Non-existent user should return None
            none_user = auth.get_user(self.test_users_db, "nonexistent")
            self.assertIsNone(none_user)

    def test_authenticate_user(self) -> None:
        """Test user authentication."""
        with patch.object(auth, "users_db", self.test_users_db):
            # Valid credentials should return user
            test_user = auth.authenticate_user(
                self.test_users_db, 
                self.test_username, 
                self.test_password
            )
            self.assertIsInstance(test_user, auth.UserInDB)
            
            # Invalid username should return None
            invalid_user = auth.authenticate_user(
                self.test_users_db, 
                "nonexistent", 
                self.test_password
            )
            self.assertIsNone(invalid_user)
            
            # Invalid password should return None
            invalid_pwd = auth.authenticate_user(
                self.test_users_db, 
                self.test_username, 
                "wrong_password"
            )
            self.assertIsNone(invalid_pwd)

    def test_create_access_token(self) -> None:
        """Test JWT token creation."""
        # Patch settings for consistent tests
        with patch.object(settings, "SECRET_KEY", "test_secret_key"):
            with patch.object(settings, "ALGORITHM", "HS256"):
                test_data = {"sub": self.test_username}
                
                # Test without expiration
                token = auth.create_access_token(test_data)
                self.assertIsInstance(token, str)
                
                # Test with custom expiration
                from datetime import timedelta
                token_with_exp = auth.create_access_token(
                    test_data, 
                    expires_delta=timedelta(minutes=15)
                )
                self.assertIsInstance(token_with_exp, str)

    @patch("jwt.decode")
    async def test_get_current_user(self, mock_jwt_decode) -> None:
        """Test current user retrieval from token."""
        # Mock JWT decode to return known payload
        mock_jwt_decode.return_value = {"sub": self.test_username}
        
        with patch.object(auth, "users_db", self.test_users_db):
            # Valid token should return user
            user = await auth.get_current_user("test_token")
            self.assertIsInstance(user, auth.UserInDB)
            self.assertEqual(user.username, self.test_username)

    @patch("jwt.decode")
    async def test_get_current_active_user(self, mock_jwt_decode) -> None:
        """Test active user retrieval."""
        # Mock JWT decode to return known payload
        mock_jwt_decode.return_value = {"sub": self.test_username}
        
        with patch.object(auth, "users_db", self.test_users_db):
            # Test with active user
            active_user = await auth.get_current_active_user(
                await auth.get_current_user("test_token")
            )
            self.assertIsInstance(active_user, auth.UserInDB)
            
            # Test with disabled user
            disabled_user = auth.UserInDB(
                username="disabled", 
                hashed_password="hash", 
                disabled=True
            )
            with self.assertRaises(Exception):
                await auth.get_current_active_user(disabled_user)

    def test_post_token_endpoint(self) -> None:
        """Test token endpoint integration."""
        with patch.object(auth, "users_db", self.test_users_db):
            # Valid credentials should return token
            formdata = {"username": self.test_username, "password": self.test_password}
            with patch.object(auth, "authenticate_user", return_value=auth.UserInDB(**self.test_users_db[self.test_username])):
                response = self.client.post("/token", data=formdata)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn("access_token", data)
                self.assertIn("token_type", data)
                self.assertEqual(data["token_type"], "bearer")
            
            # Invalid credentials should return 401
            with patch.object(auth, "authenticate_user", return_value=None):
                response = self.client.post("/token", data={"username": "invalid", "password": "wrong"})
                self.assertEqual(response.status_code, 401)
