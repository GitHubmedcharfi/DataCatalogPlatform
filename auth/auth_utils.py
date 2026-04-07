from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from .security import decode_token
from .models import User
from sqlalchemy.orm import Session
from database import get_db

security = HTTPBearer()

async def get_current_user(
    credentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get the current authenticated user from the JWT token
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user exists in database
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"username": user.username, "user_id": user.id}
