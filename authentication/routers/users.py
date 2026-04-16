from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query

from authentication.dependencies import get_current_user
from authentication.errors import BadRequestError
from authentication.mappers import user_to_current_response, user_to_list_element, user_to_update_response
from authentication.models.user import User
from authentication.schemas import (
    CurrentUserResponseModel,
    UpdateUserModel,
    UpdateUserResponseModel,
    UsersListResponseModel,
)

router = APIRouter(tags=["user"])


@router.get("/users/current", response_model=CurrentUserResponseModel)
async def current_user(user: User = Depends(get_current_user)):
    return user_to_current_response(user)


@router.patch("/users/current", response_model=UpdateUserResponseModel)
async def edit_current_user(payload: UpdateUserModel, user: User = Depends(get_current_user)):
    # Update only provided fields.
    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.other_name is not None:
        user.other_name = payload.other_name
    if payload.email is not None:
        user.email = str(payload.email)
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.birthday is not None:
        user.birthday = payload.birthday

    await user.save()
    return user_to_update_response(user)


@router.get("/users", response_model=UsersListResponseModel)
async def users_list(
    page: int = Query(...),
    size: int = Query(...),
    _user: User = Depends(get_current_user),
):
    if page < 1 or size < 1:
        raise BadRequestError("Параметры `page` и `size` должны быть >= 1", code=1002)

    total = await User.all().count()
    offset = (page - 1) * size
    users: List[User] = await User.all().order_by("id").offset(offset).limit(size)

    return {
        "data": [user_to_list_element(u) for u in users],
        "meta": {"pagination": {"total": total, "page": page, "size": size}},
    }

