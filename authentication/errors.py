from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class AppError(Exception):
    status_code: int
    message: str
    code: Optional[int] = None


class BadRequestError(AppError):
    def __init__(self, message: str, code: int = 1000):
        super().__init__(status_code=400, message=message, code=code)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Требуется авторизация"):
        super().__init__(status_code=401, message=message, code=None)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Недостаточно прав"):
        super().__init__(status_code=403, message=message, code=None)


class NotFoundError(AppError):
    def __init__(self, message: str = "Пользователь не найден"):
        super().__init__(status_code=404, message=message, code=None)

