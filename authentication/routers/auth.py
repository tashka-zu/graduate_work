from __future__ import annotations

from fastapi import APIRouter, Response

from authentication.config import COOKIE_MAX_AGE_SECONDS, COOKIE_NAME, COOKIE_SECURE
from authentication.dependencies import get_current_user
from authentication.errors import BadRequestError
from authentication.mappers import user_to_current_response
from authentication.models.user import User
from authentication.security import create_access_token, hash_password, verify_password
from authentication.schemas import CurrentUserResponseModel, LoginModel

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=CurrentUserResponseModel, responses={400: {"model": dict}, 422: {"model": dict}})
async def login(payload: LoginModel, response: Response):
    user = await User.get_or_none(email=payload.login)
    if not user or not verify_password(payload.password, user.password_hash):
        raise BadRequestError("Неверный логин или пароль", code=1001)

    token = create_access_token(user.id)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )
    return user_to_current_response(user)


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {}

