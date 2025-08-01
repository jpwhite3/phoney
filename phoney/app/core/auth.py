from datetime import datetime, timedelta, timezone
from typing import Annotated, Dict, Optional

from jose import jwt
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose.exceptions import JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

from ..core.config import settings


class Token(BaseModel):
    """Token schema for authentication responses."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data schema."""
    username: Optional[str] = None


class User(BaseModel):
    """Basic user information schema."""
    username: str
    disabled: Optional[bool] = None


class UserInDB(User):
    """User schema with password hash."""
    hashed_password: str


# User database simulation - in a real app, this would be a database
users_db = {
    "api_user": {
        "username": settings.API_USERNAME,
        "hashed_password": settings.API_PASSWORD_HASH,
    }
}


# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter(tags=["authentication"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plain password matches a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a password hash using bcrypt."""
    return pwd_context.hash(password)


def get_user(db: Dict, username: str) -> Optional[UserInDB]:
    """Get a user from the database by username."""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(db: Dict, username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user by username and password."""
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    # Use timezone-aware datetime (UTC) instead of utcnow()
    expire = datetime.now(tz=timezone.utc) + (
        expires_delta 
        if expires_delta 
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    """Get the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> UserInDB:
    """Get the current user and verify it's not disabled."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Dict[str, str]:
    """Endpoint to authenticate and get access token."""
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
