from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from os import getenv
from aiogram import Bot
from keyboards import Keyboards
from database.database import add_ticket
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(getenv('ADMIN_USER_ID'))
ticket_counter = 0

async def finish_support(message: Message, state:FSMContext, bot: Bot, keyboard):
    global ticket_counter
    ticket_counter += 1

    data = await state.get_data()
    user = message.from_user
    user_name = f'@{user.username}' if user.username else 'Нету username'


    ticket_id = await add_ticket(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name,
        support_type=data["support_type"],
        text=data["text"],
        photo_id=data.get("photo")
    )


    caption = (f"Новый тикет #{ticket_counter}\n"
        f"Тип обращения: {data['support_type']}\n"
        f"Пользователь: {user_name}\n"
        f"ID пользователя: {user.id}\n"
        f"Текст обращения: {data['text']}")

    if data.get('photo'):
        sent = await bot.send_photo(chat_id=ADMIN_ID, photo=data["photo"], caption=caption)
    else:
        sent = await bot.send_message(chat_id=ADMIN_ID, text=caption)
    pending_tickets[sent.message_id] = user.id
    await message.answer("Ваше обращение отправлено! Спасибо!", reply_markup=keyboard)
    await state.clear()

pending_tickets = {}