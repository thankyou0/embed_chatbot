from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import bcrypt
from jose import JWTError, jwt
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _prepare_password(password: str) -> bytes:
    """Prepare password for bcrypt - handle 72 byte limit.
    
    Bcrypt has a 72-byte limit. For longer passwords, we pre-hash
    with SHA-256 to ensure consistent length while maintaining security.
    """
    password_bytes = password.encode('utf-8')
    # Bcrypt has a 72-byte limit. Pre-hash long passwords with SHA-256
    if len(password_bytes) > 72:
        # Hash with SHA-256 and use the hex string (64 chars = 64 bytes)
        password_bytes = hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
    return password_bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    try:
        password_bytes = _prepare_password(plain_password)
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.warning(f"Password verification failed: {str(e)[:30]}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.
    
    Automatically handles passwords longer than 72 bytes by pre-hashing.
    """
    password_bytes = _prepare_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        # Ensure sub is a string (JWT spec requirement)
        if "sub" in payload and not isinstance(payload["sub"], str):
            logger.warning("Token has invalid sub type - user needs to re-login")
            return None
        return payload
    except JWTError as e:
        error_msg = str(e)
        if "Subject must be a string" in error_msg:
            logger.warning("Token format invalid - please log in again")
        else:
            logger.warning(f"Token decode failed: {error_msg[:30]}")
        return None