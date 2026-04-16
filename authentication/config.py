import os

# Connection string for Tortoise ORM.
# Example (postgres): postgres://user:pass@localhost:5432/dbname
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgres://postgres:tasha1502@localhost:5432/graduate_work_db",
)

# JWT settings for cookie-based auth.
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

COOKIE_NAME = os.getenv("COOKIE_NAME", "access_token")
COOKIE_MAX_AGE_SECONDS = int(os.getenv("COOKIE_MAX_AGE_SECONDS", str(JWT_EXPIRE_MINUTES * 60)))
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

# OpenAPI spec requires `city` in admin responses even if it wasn't provided on create.
DEFAULT_CITY_ID = int(os.getenv("DEFAULT_CITY_ID", "1"))
DEFAULT_CITY_NAME = os.getenv("DEFAULT_CITY_NAME", "Unknown")

# Optional auto-seeding for development/testing.
DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "")
DEFAULT_SIMPLE_EMAIL = os.getenv("DEFAULT_SIMPLE_EMAIL", "")
DEFAULT_SIMPLE_PASSWORD = os.getenv("DEFAULT_SIMPLE_PASSWORD", "")
DEFAULT_BIRTHDAY_ADMIN = os.getenv("DEFAULT_BIRTHDAY_ADMIN", "1990-01-01")
DEFAULT_BIRTHDAY_SIMPLE = os.getenv("DEFAULT_BIRTHDAY_SIMPLE", "1995-01-01")
