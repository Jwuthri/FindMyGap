"""
Authentication and authorization for FindMyGap.
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from app.config import Settings, get_settings
from app.database.repositories import UserRepository
from app.core.exceptions import UnauthorizedError, ValidationError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthManager:
    """Authentication and authorization manager."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.

        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time

        Returns:
            JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token data

        Raises:
            UnauthorizedError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token has expired")
        except jwt.JWTError:
            raise UnauthorizedError("Invalid token")

    def create_api_key(self, user_id: str, name: Optional[str] = None) -> str:
        """
        Create an API key for a user.

        Args:
            user_id: User identifier
            name: Optional name for the API key

        Returns:
            API key string
        """
        data = {
            "user_id": user_id,
            "type": "api_key",
            "name": name,
            "created_at": datetime.utcnow().isoformat()
        }

        # API keys don't expire by default
        return self.create_access_token(data, expires_delta=timedelta(days=365))

    def verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Verify an API key.

        Args:
            api_key: API key string

        Returns:
            API key data

        Raises:
            UnauthorizedError: If API key is invalid
        """
        payload = self.verify_token(api_key)

        if payload.get("type") != "api_key":
            raise UnauthorizedError("Invalid API key format")

        return payload
