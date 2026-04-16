from datetime import date

from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)

    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)

    # OpenAPI spec marks these as required in response models,
    # so we keep non-null defaults in the database.
    other_name = fields.CharField(max_length=50, default="")
    email = fields.CharField(max_length=50, unique=True)
    phone = fields.CharField(max_length=20, default="")
    birthday = fields.DateField(default=date(2000, 1, 1))

    city = fields.ForeignKeyField("models.City", related_name="users", null=True)
    additional_info = fields.TextField(default="")

    is_admin = fields.BooleanField(default=False)
    password_hash = fields.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"