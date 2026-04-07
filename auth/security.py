from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .models import RefreshToken
# Load Environment Variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set!"
    )

# Password Hashing
pwd_context = CryptContext(
    schemes=["argon2"],  
    deprecated="auto"
)
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )
# JWT Token Creation
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt
def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    )
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt
# JWT Decode
def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
# Logout 
def logout_user(
    db: Session,
    refresh_token: str
):
    token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token
        )
        .first()
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found"
        )

    token.revoked = True

    db.commit()

    return {
        "message": "Logged out successfully"
    }