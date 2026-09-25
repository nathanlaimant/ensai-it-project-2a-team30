from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dao.user_dao import UserDAO
from service.user_service import UserService
from utils.db_connection import DbConnection
from utils.token_cache import app_token_cache

security = HTTPBearer()


def get_db(request: Request) -> DbConnection:
    return request.app.state.db


def get_user_dao(db: DbConnection = Depends(get_db)) -> UserDAO:
    return UserDAO(db)


def get_user_service(user_dao: UserDAO = Depends(get_user_dao)):
    return UserService(user_dao)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_dao: UserDAO = Depends(get_user_dao),
) -> int:
    token = credentials.credentials

    cached_user_id = app_token_cache.get(token)
    if cached_user_id:
        return cached_user_id

    persistent_user = user_dao.get_by_access_token(token)
    if not persistent_user:
        raise HTTPException(status_code=401, detail="Invalid token.")

    app_token_cache.set(token, persistent_user.user_id)
    return persistent_user.user_id
