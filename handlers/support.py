from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from os import getenv
from aiogram import Bot
from keyboards import Keyboards
from dotenv import load_dotenv
from database.database import(
    create_ticket,
    add_ticket_message,
    set_admin_message
)

load_dotenv()
ADMIN_ID = int(getenv('ADMIN_USER_ID'))

async def finish_support(message: Message, state:FSMContext, bot: Bot, keyboard):

    data = await state.get_data()
    user = message.from_user
    user_name = (f'@{user.username}' if user.username else 'Нету username')

    ticket_id = await create_ticket(
    user_id=user.id,
    support_type=data['support_type'],
    text=data['text']
)

    await add_ticket_message(
        ticket_id=ticket_id,
        sender_id=user.id,
        sender_type="user",
        text=(
            f"Тип обрашения: {data['support_type']}\n"
            f"Текст: {data['text']}"
        )
    )

    caption =(
        f"Новый тикет #{ticket_id}\n"
        f"Тип обращения: {data['support_type']}\n"
        f"Пользователь: {user_name}\n"
        f"ID пользователя: {user.id}\n"
        f"Текст обращения: {data['text']}"
    )

    if data.get('photo'):
        sent = await bot.send_photo(chat_id=ADMIN_ID, photo=data["photo"], caption=caption)
    else:
        sent = await bot.send_message(chat_id=ADMIN_ID, text=caption)

    await set_admin_message(
        ticket_id=ticket_id,
        admin_chat_id=ADMIN_ID,
        admin_message_id=sent.message_id
    )

    await message.answer(
        f"Ваше обрашение #{ticket_id} отправлено! Спасибо.",
        reply_markup=keyboard
    )