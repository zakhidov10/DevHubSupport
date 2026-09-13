from os import getenv

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dotenv import load_dotenv

from database.database import (
    create_ticket,
    add_ticket_message,
    set_admin_message,
)

load_dotenv()

ADMIN_ID = int(getenv("ADMIN_USER_ID"))


async def finish_support(
    message: Message,
    state: FSMContext,
    bot: Bot,
    keyboard
):
    data = await state.get_data()

    user = message.from_user
    user_name = (
        f"@{user.username}"
        if user.username
        else "Нету username"
    )

    support_type = data.get("support_type")
    text = data.get("text")
    photo = data.get("photo")

    if not support_type or not text:
        await message.answer(
            "Произошла ошибка. Попробуйте создать обращение заново.",
            reply_markup=keyboard
        )
        await state.clear()
        return

    # Создаём тикет
    ticket_id = await create_ticket(
        user_id=user.id,
        support_type=support_type,
        text=text
    )

    # Сохраняем первое сообщение тикета
    await add_ticket_message(
        ticket_id=ticket_id,
        sender_id=user.id,
        sender_type="user",
        text=(
            f"Тип обращения: {support_type}\n"
            f"Текст: {text}"
        )
    )

    caption = (
        f"Новый тикет #{ticket_id}\n\n"
        f"Тип обращения: {support_type}\n"
        f"Пользователь: {user_name}\n"
        f"ID пользователя: {user.id}\n\n"
        f"Текст обращения:\n{text}\n\n"
        f"💬 Чтобы ответить, ответьте на это сообщение."
    )

    # Отправляем тикет админу
    if photo:
        sent = await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption=caption
        )
    else:
        sent = await bot.send_message(
            chat_id=ADMIN_ID,
            text=caption
        )

    # Запоминаем сообщение админа
    await set_admin_message(
        ticket_id=ticket_id,
        admin_chat_id=ADMIN_ID,
        admin_message_id=sent.message_id
    )

    # Очень важно: очищаем FSM
    await state.clear()

    await message.answer(
        f"Ваше обращение #{ticket_id} отправлено! Спасибо.",
        reply_markup=keyboard
    )