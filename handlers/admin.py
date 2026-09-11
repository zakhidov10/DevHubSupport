from handlers.support import ADMIN_ID, pending_tickets, finish_support
from aiogram import Bot
from aiogram.types import Message
from aiogram import Router, F

router = Router()

@router.message(F.from_user.id == ADMIN_ID, F.reply_to_message)
async def reply_to_ticket(message: Message, bot: Bot):
    original_message_id = message.reply_to_message.message_id
    user_id = pending_tickets.get(original_message_id)

    if user_id is None:
        await message.answer("Не удалось найти пользователя для этого тикета.")
        return

    await bot.send_message(chat_id=user_id, text=f"Ответ от администратора: \n\n{message.text}")
    await message.answer("Ответ отправлен пользователю.")   