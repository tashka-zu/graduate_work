from __future__ import annotations

from typing import Any

from authentication.config import DEFAULT_CITY_ID
from authentication.models.user import User


def _user_other_name(user: User) -> str:
    return user.other_name or ""


def _user_phone(user: User) -> str:
    return user.phone or ""


def _user_additional_info(user: User) -> str:
    return user.additional_info or ""


def user_to_current_response(user: User) -> dict[str, Any]:
    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "other_name": _user_other_name(user),
        "email": user.email,
        "phone": _user_phone(user),
        "birthday": user.birthday,
        "is_admin": user.is_admin,
    }


def user_to_update_response(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "other_name": _user_other_name(user),
        "email": user.email,
        "phone": _user_phone(user),
        "birthday": user.birthday,
    }


def user_to_private_detail_response(user: User) -> dict[str, Any]:
    city_id = user.city_id if getattr(user, "city_id", None) else DEFAULT_CITY_ID
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "other_name": _user_other_name(user),
        "email": user.email,
        "phone": _user_phone(user),
        "birthday": user.birthday,
        "city": city_id,
        "additional_info": _user_additional_info(user),
        "is_admin": user.is_admin,
    }


def user_to_list_element(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
    }

