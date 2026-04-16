from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class LoginModel(BaseModel):
    login: str
    password: str


class ErrorResponseModel(BaseModel):
    code: int
    message: str


class CodelessErrorResponseModel(BaseModel):
    message: str


class CurrentUserResponseModel(BaseModel):
    first_name: str
    last_name: str
    other_name: str
    email: EmailStr
    phone: str
    birthday: date
    is_admin: bool


class UpdateUserModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    other_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None


class UpdateUserResponseModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    other_name: str
    email: EmailStr
    phone: str
    birthday: date


class UsersListElementModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr


class PaginatedMetaDataModel(BaseModel):
    total: int
    page: int
    size: int


class UsersListMetaDataModel(BaseModel):
    pagination: PaginatedMetaDataModel


class UsersListResponseModel(BaseModel):
    data: List[UsersListElementModel]
    meta: UsersListMetaDataModel


class CitiesHintModel(BaseModel):
    id: int
    name: str


class PrivateUsersListHintMetaModel(BaseModel):
    city: List[CitiesHintModel]


class PrivateUsersListMetaDataModel(BaseModel):
    pagination: PaginatedMetaDataModel
    hint: PrivateUsersListHintMetaModel


class PrivateUsersListResponseModel(BaseModel):
    data: List[UsersListElementModel]
    meta: PrivateUsersListMetaDataModel


class PrivateCreateUserModel(BaseModel):
    first_name: str
    last_name: str
    other_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    birthday: Optional[date] = None
    city: Optional[int] = None
    additional_info: Optional[str] = None
    is_admin: bool
    password: str


class PrivateDetailUserResponseModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    other_name: str
    email: EmailStr
    phone: str
    birthday: date
    city: int
    additional_info: str
    is_admin: bool


class PrivateUpdateUserModel(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    other_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    city: Optional[int] = None
    additional_info: Optional[str] = None
    is_admin: Optional[bool] = None


class HTTPValidationError(BaseModel):
    # FastAPI returns a different structure; kept only for completeness.
    detail: list[dict]

