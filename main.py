from os import getenv
import asyncio

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers.routes import router
from handlers.admin import router as admin_router
from database.database import init_db


load_dotenv()

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()

# Основные хендлеры
dp.include_router(router)

# Админские хендлеры
dp.include_router(admin_router)


async def main():
    await init_db()

    bot = Bot(token=TOKEN)

    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())