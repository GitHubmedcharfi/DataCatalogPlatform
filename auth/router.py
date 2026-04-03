from fastapi import APIRouter, Depends, status, Body, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .schemas import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse, RefreshTokenRequest,LogoutRequest
from .service import register_user, login_user, logout_user
from .security import decode_token, create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    return register_user(db, request)
@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    tokens = login_user(db, request.username, request.password)
    return tokens

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest):
    try:
        payload = decode_token(request.refresh_token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        new_access = create_access_token({"sub": user_id})
        new_refresh = create_refresh_token({"sub": user_id})
        return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

  
@router.post("/logout")
def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db)
):
    return logout_user(db, request.refresh_token)    