from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)
from app.core.store import users, users_by_email, make_id, now_iso
from app.core.auth import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_SECONDS

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(payload: RegisterRequest):
    email = payload.email.lower()
    if email in users_by_email:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": 409,
                    "message": "Conflict: duplicate resource",
                    "detail": "Email already registered",
                }
            },
        )

    user_id = make_id("usr")
    created_at = now_iso()
    user = {
        "user_id": user_id,
        "name": payload.name,
        "email": email,
        "password_hash": hash_password(payload.password),
        "created_at": created_at,
    }
    users[user_id] = user
    users_by_email[email] = user_id

    return RegisterResponse(
        user_id=user_id,
        name=payload.name,
        email=email,
        created_at=created_at,
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    email = payload.email.lower()
    user_id = users_by_email.get(email)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": 401,
                    "message": "Unauthenticated: JWT missing or expired",
                    "detail": "Wrong email or password",
                }
            },
        )

    user = users[user_id]
    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": 401,
                    "message": "Unauthenticated: JWT missing or expired",
                    "detail": "Wrong email or password",
                }
            },
        )

    token = create_access_token(user_id)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
        user_id=user_id,
    )