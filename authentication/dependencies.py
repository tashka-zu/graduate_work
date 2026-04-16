from __future__ import annotations

from fastapi import Depends, Request

from authentication.config import COOKIE_NAME
from authentication.errors import ForbiddenError, UnauthorizedError
from authentication.models.user import User
from authentication.security import decode_access_token


async def get_current_user(request: Request) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise UnauthorizedError()

    try:
        payload = decode_access_token(token)
    except Exception:
        # Any JWT validation problem should result in "unauthorized".
        raise UnauthorizedError()

    user_id_raw = payload.get("sub")
    if not user_id_raw:
        raise UnauthorizedError()

    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        raise UnauthorizedError()

    user = await User.get_or_none(id=user_id).select_related("city")
    if not user:
        raise UnauthorizedError()

    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise ForbiddenError()
    return user

