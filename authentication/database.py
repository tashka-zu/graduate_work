import os

from authentication.config import DEFAULT_CITY_ID, DEFAULT_CITY_NAME
from authentication.models.city import City
from authentication.models.user import User
from authentication.security import hash_password


async def seed_defaults() -> None:
    """
    Seed data that OpenAPI spec expects (default city) and optional demo users.

    Tortoise should already be initialized by `register_tortoise`.
    """

    # Ensure default city exists for spec compliance.
    await City.get_or_create(id=DEFAULT_CITY_ID, defaults={"name": DEFAULT_CITY_NAME})

    # Optional auto-seeding for development/testing.
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "")
    simple_email = os.getenv("DEFAULT_SIMPLE_EMAIL", "")
    simple_password = os.getenv("DEFAULT_SIMPLE_PASSWORD", "")
    birthday_admin = os.getenv("DEFAULT_BIRTHDAY_ADMIN", "1990-01-01")
    birthday_simple = os.getenv("DEFAULT_BIRTHDAY_SIMPLE", "1995-01-01")

    if admin_email and admin_password:
        await User.get_or_create(
            email=admin_email,
            defaults={
                "first_name": "Admin",
                "last_name": "User",
                "other_name": "",
                "phone": "",
                "birthday": birthday_admin,
                "city_id": DEFAULT_CITY_ID,
                "additional_info": "",
                "is_admin": True,
                "password_hash": hash_password(admin_password),
            },
        )

    if simple_email and simple_password:
        await User.get_or_create(
            email=simple_email,
            defaults={
                "first_name": "Simple",
                "last_name": "User",
                "other_name": "",
                "phone": "",
                "birthday": birthday_simple,
                "city_id": DEFAULT_CITY_ID,
                "additional_info": "",
                "is_admin": False,
                "password_hash": hash_password(simple_password),
            },
        )

# Для тестирования подключения можно запустить эту функцию
# if __name__ == '__main__':
#     run_async(seed_defaults())