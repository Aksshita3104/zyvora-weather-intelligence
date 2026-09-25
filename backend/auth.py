from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel


router = APIRouter(prefix="/api/auth", tags=["Authentication"])

SECRET_KEY = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

security = HTTPBearer()


# -----------------------------------
# ADMIN CREDENTIALS
# -----------------------------------
ADMIN_USERNAME = "admin"

# Temporary hash for password: Admin@123
ADMIN_PASSWORD_HASH = pwd_context.hash("Admin@123")


class LoginRequest(BaseModel):
    username: str
    password: str


def create_access_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "role": "admin",
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


@router.post("/login")
@router.post("/admin/login")
def admin_login(data: LoginRequest):

    if data.username != ADMIN_USERNAME:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not pwd_context.verify(
        data.password,
        ADMIN_PASSWORD_HASH
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(data.username)

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "role": "admin"
    }


# -----------------------------------
# PROTECTED ADMIN CHECK
# -----------------------------------
def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        role = payload.get("role")

        if username != ADMIN_USERNAME or role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )

        return {
            "username": username,
            "role": role
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )