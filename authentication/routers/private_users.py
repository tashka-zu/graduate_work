from __future__ import annotations

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, Response

from authentication.config import DEFAULT_CITY_ID
from authentication.dependencies import get_current_admin
from authentication.errors import BadRequestError, NotFoundError
from authentication.mappers import user_to_list_element, user_to_private_detail_response
from authentication.models.city import City
from authentication.models.user import User
from authentication.security import create_access_token, hash_password
from authentication.schemas import (
    PrivateCreateUserModel,
    PrivateDetailUserResponseModel,
    PrivateUpdateUserModel,
    PrivateUsersListResponseModel,
    PrivateUsersListMetaDataModel,
    CitiesHintModel,
    PrivateUsersListHintMetaModel,
)

router = APIRouter(prefix="/private", tags=["admin"])

DEFAULT_BIRTHDAY = date(2000, 1, 1)


@router.get("/users", response_model=PrivateUsersListResponseModel)
async def private_users_list(
    page: int = Query(...),
    size: int = Query(...),
    _admin: User = Depends(get_current_admin),
):
    if page < 1 or size < 1:
        raise BadRequestError("Параметры `page` и `size` должны быть >= 1", code=1002)

    total = await User.all().count()
    offset = (page - 1) * size
    users: List[User] = await User.all().order_by("id").offset(offset).limit(size)

    cities = await City.all().order_by("id")
    hint = {"city": [{"id": c.id, "name": c.name} for c in cities]}

    return {
        "data": [user_to_list_element(u) for u in users],
        "meta": {
            "pagination": {"total": total, "page": page, "size": size},
            "hint": hint,
        },
    }


@router.post("/users", response_model=PrivateDetailUserResponseModel, status_code=201)
async def private_create_user(
    payload: PrivateCreateUserModel,
    _admin: User = Depends(get_current_admin),
):
    if await User.get_or_none(email=payload.email):
        raise BadRequestError("Пользователь с таким email уже существует", code=1003)

    city_id = payload.city if payload.city is not None else DEFAULT_CITY_ID
    if city_id is not None:
        city = await City.get_or_none(id=city_id)
        if not city:
            raise BadRequestError("Город не найден", code=1004)

    user = await User.create(
        first_name=payload.first_name,
        last_name=payload.last_name,
        other_name=payload.other_name or "",
        email=payload.email,
        phone=payload.phone or "",
        birthday=payload.birthday or DEFAULT_BIRTHDAY,
        city_id=city_id,
        additional_info=payload.additional_info or "",
        is_admin=payload.is_admin,
        password_hash=hash_password(payload.password),
    )

    return user_to_private_detail_response(user)


@router.get("/users/{pk}", response_model=PrivateDetailUserResponseModel)
async def private_get_user(
    pk: int,
    _admin: User = Depends(get_current_admin),
):
    user = await User.get_or_none(id=pk)
    if not user:
        raise NotFoundError()
    return user_to_private_detail_response(user)


@router.patch("/users/{pk}", response_model=PrivateDetailUserResponseModel)
async def private_patch_user(
    pk: int,
    payload: PrivateUpdateUserModel,
    _admin: User = Depends(get_current_admin),
):
    if payload.id != pk:
        raise BadRequestError("id в теле запроса должен совпадать с pk", code=1005)

    user = await User.get_or_none(id=pk)
    if not user:
        raise NotFoundError()

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
    if payload.additional_info is not None:
        user.additional_info = payload.additional_info
    if payload.is_admin is not None:
        user.is_admin = payload.is_admin

    if payload.city is not None:
        city = await City.get_or_none(id=payload.city)
        if not city:
            raise BadRequestError("Город не найден", code=1004)
        user.city_id = payload.city

    await user.save()
    return user_to_private_detail_response(user)


@router.delete("/users/{pk}", status_code=204)
async def private_delete_user(
    pk: int,
    _admin: User = Depends(get_current_admin),
):
    user = await User.get_or_none(id=pk)
    if not user:
        raise NotFoundError()
    await user.delete()
    return Response(status_code=204)

