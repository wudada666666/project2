from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from services import auth_service

security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="请先登录")
    user = auth_service.get_user_from_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    return user
