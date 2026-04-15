from tortoise import Tortoise
from authentication.config import DATABASE_URL

async def init_db():
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={'models': ['authentication.models.user']}
    )
    await Tortoise.generate_schemas()

# Для тестирования подключения можно запустить эту функцию
# if __name__ == '__main__':
#     run_async(init_db())