from tortoise import fields
from tortoise.models import Model


class City(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name

