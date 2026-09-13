from os import getenv
from aiogram import Bot, Dispatcher
import asyncio
from dotenv import load_dotenv

load_dotenv()

from handlers.routes import router
from handlers.admin import router as admin_router
from database.database import (
    init_db,
    init_admins,
    get_admin_role,
    add_admin
)

TOKEN = getenv("BOT_TOKEN")
OWNER_ID = int(getenv("ADMIN_USER_ID"))

dp = Dispatcher()

dp.include_router(router)
dp.include_router(admin_router)


async def main():
    await init_db()
    await init_admins()

    # Если Owner ещё не существует в БД,
    # добавляем его как owner
    role = await get_admin_role(OWNER_ID)

    if role is None:
        await add_admin(OWNER_ID, role="owner")

    bot = Bot(token=TOKEN)

    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())