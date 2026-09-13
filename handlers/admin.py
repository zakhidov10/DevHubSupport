from aiogram import Router, F, Bot
from aiogram.types import Message

from handlers.support import ADMIN_ID
from database.database import (
    get_ticket_by_admin_message,
    add_ticket_message,
)

router = Router()


@router.message(
    F.from_user.id == ADMIN_ID,
    F.reply_to_message,
    F.text
)
async def reply_to_ticket(message: Message, bot: Bot):

    original_message_id = message.reply_to_message.message_id

    ticket = await get_ticket_by_admin_message(
        ADMIN_ID,
        original_message_id
    )

    if ticket is None:
        await message.answer(
            "Не удалось найти тикет."
        )
        return

    ticket_id = ticket[0]
    user_id = ticket[1]
    status = ticket[2]

    if status != "open":
        await message.answer(
            "Этот тикет уже закрыт."
        )
        return

    if user_id is None:
        await message.answer(
            "Не удалось найти пользователя."
        )
        return

    # Отправляем ответ пользователю
    await bot.send_message(
        chat_id=user_id,
        text=(
            "💬 Ответ от администратора:\n\n"
            f"{message.text}"
        )
    )

    # Сохраняем ответ в БД
    await add_ticket_message(
        ticket_id=ticket_id,
        sender_id=message.from_user.id,
        sender_type="admin",
        text=message.text
    )

    await message.answer(
        "✅ Ответ отправлен пользователю."
    )