from os import getenv
from aiogram import Bot, Dispatcher
import asyncio
from dotenv import load_dotenv
load_dotenv()
from handlers.routes import router
from database.database import init_db

TOKEN = getenv("BOT_TOKEN")
ADMIN = getenv("ADMIN_USER_ID")
dp = Dispatcher()
dp.include_router(router)

async def main():
    await init_db()
    bot = Bot(token=TOKEN)
    print("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())