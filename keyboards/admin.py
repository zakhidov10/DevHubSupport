from os import getenv
from html import escape

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest

from dotenv import load_dotenv

from database.database import (
    get_admin_role,
    add_admin,
    remove_admin,
    get_admins,

    get_ticket,
    get_tickets,
    get_ticket_messages,
    close_ticket,
    reopen_ticket,
    get_ticket_stats,
    get_user_ticket_counts,

    add_ticket_message,
)

load_dotenv()

OWNER_ID = int(getenv("ADMIN_USER_ID"))

router = Router()


# =========================================================
# FSM для ответа администратора
# =========================================================

class AdminReplyForm(StatesGroup):
    waiting_text = State()


# =========================================================
# Проверка роли
# =========================================================

async def get_role(user_id: int):
    """
    Возвращает:
    owner
    admin
    None
    """

    # Owner всегда имеет полный доступ
    if user_id == OWNER_ID:
        return "owner"

    return await get_admin_role(user_id)


async def is_admin(user_id: int):
    role = await get_role(user_id)
    return role in ("owner", "admin")


async def is_owner(user_id: int):
    role = await get_role(user_id)
    return role == "owner"


# =========================================================
# Клавиатура главной админки
# =========================================================

def admin_menu_keyboard(
    new_count: int = 0,
    open_count: int = 0
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"📥 Новые обращения ({new_count})",
                    callback_data="admin:new"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"📂 Открытые тикеты ({open_count})",
                    callback_data="admin:open"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚠️ Жалобы",
                    callback_data="admin:complaints"
                ),
                InlineKeyboardButton(
                    text="❓ Вопросы",
                    callback_data="admin:questions"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="admin:stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Администраторы",
                    callback_data="admin:admins"
                )
            ]
        ]
    )


# =========================================================
# Клавиатура управления администраторами
# =========================================================

def admins_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Добавить администратора",
                    callback_data="admins:add"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➖ Удалить администратора",
                    callback_data="admins:remove"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Список администраторов",
                    callback_data="admins:list"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ В админ-панель",
                    callback_data="admin:menu"
                )
            ]
        ]
    )


# =========================================================
# Клавиатура списка тикетов
# =========================================================

def tickets_keyboard(tickets):
    buttons = []

    for ticket in tickets:
        ticket_id = ticket[0]
        support_type = ticket[2]
        status = ticket[4]

        if "Жалоб" in support_type:
            emoji = "⚠️"
        else:
            emoji = "❓"

        status_emoji = "🟢" if status == "open" else "🔴"

        buttons.append([
            InlineKeyboardButton(
                text=f"{status_emoji} #{ticket_id} {emoji}",
                callback_data=f"ticket:view:{ticket_id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ В админ-панель",
            callback_data="admin:menu"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


# =========================================================
# Клавиатура тикета
# =========================================================

def ticket_keyboard(ticket_id: int, status: str):
    buttons = [
        [
            InlineKeyboardButton(
                text="💬 Ответить",
                callback_data=f"ticket:reply:{ticket_id}"
            ),
            InlineKeyboardButton(
                text="📜 История",
                callback_data=f"ticket:history:{ticket_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 Пользователь",
                callback_data=f"ticket:user:{ticket_id}"
            )
        ]
    ]

    if status == "open":
        buttons.append([
            InlineKeyboardButton(
                text="✅ Закрыть",
                callback_data=f"ticket:close:{ticket_id}"
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text="🔄 Открыть",
                callback_data=f"ticket:reopen:{ticket_id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="admin:open"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


# =========================================================
# /admin
# =========================================================

@router.message(Command("admin"))
async def admin_command(message: Message):

    role = await get_role(message.from_user.id)

    if role is None:
        await message.answer("⛔ У вас нет доступа к админ-панели.")
        return

    stats = await get_ticket_stats()

    new_count = stats.get("new", 0)
    open_count = stats.get("open", 0)

    role_text = "👑 Owner" if role == "owner" else "🛠 Admin"

    await message.answer(
        f"🛠 <b>Админ-панель</b>\n\n"
        f"Ваша роль: <b>{role_text}</b>\n\n"
        f"📥 Новые обращения: <b>{new_count}</b>\n"
        f"📂 Открытые тикеты: <b>{open_count}</b>",
        reply_markup=admin_menu_keyboard(
            new_count,
            open_count
        ),
        parse_mode="HTML"
    )


# =========================================================
# Главное меню админки
# =========================================================

@router.callback_query(F.data == "admin:menu")
async def admin_menu(callback: CallbackQuery):

    role = await get_role(callback.from_user.id)

    if role is None:
        await callback.answer(
            "⛔ Нет доступа",
            show_alert=True
        )
        return

    stats = await get_ticket_stats()

    new_count = stats.get("new", 0)
    open_count = stats.get("open", 0)

    role_text = "👑 Owner" if role == "owner" else "🛠 Admin"

    await callback.message.edit_text(
        f"🛠 <b>Админ-панель</b>\n\n"
        f"Ваша роль: <b>{role_text}</b>\n\n"
        f"📥 Новые обращения: <b>{new_count}</b>\n"
        f"📂 Открытые тикеты: <b>{open_count}</b>",
        reply_markup=admin_menu_keyboard(
            new_count,
            open_count
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# Управление администраторами
# =========================================================

@router.callback_query(F.data == "admin:admins")
async def admin_management(callback: CallbackQuery):

    if not await is_owner(callback.from_user.id):
        await callback.answer(
            "⛔ Только Owner может управлять администраторами.",
            show_alert=True
        )
        return

    await callback.message.edit_text(
        "👥 <b>Управление администраторами</b>\n\n"
        "Здесь Owner может добавлять и удалять администраторов.",
        reply_markup=admins_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# Добавление администратора
# =========================================================

@router.callback_query(F.data == "admins:add")
async def add_admin_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not await is_owner(callback.from_user.id):
        await callback.answer(
            "⛔ Только Owner.",
            show_alert=True
        )
        return

    await state.set_state("waiting_admin_id")

    await callback.message.answer(
        "➕ <b>Добавление администратора</b>\n\n"
        "Отправьте Telegram ID пользователя.\n\n"
        "Например:\n"
        "<code>123456789</code>",
        parse_mode="HTML"
    )

    await callback.answer()


@router.message(F.text, F.state == "waiting_admin_id")
async def add_admin_process(
    message: Message,
    state: FSMContext
):

    if not await is_owner(message.from_user.id):
        await state.clear()
        return

    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ ID должен состоять только из цифр.\n\n"
            "Пример: <code>123456789</code>",
            parse_mode="HTML"
        )
        return

    if user_id == OWNER_ID:
        await message.answer(
            "👑 Этот пользователь уже является Owner."
        )
        await state.clear()
        return

    existing_role = await get_admin_role(user_id)

    if existing_role == "admin":
        await message.answer(
            "ℹ️ Этот пользователь уже является администратором."
        )
        await state.clear()
        return

    await add_admin(user_id, role="admin")

    await message.answer(
        f"✅ Пользователь <code>{user_id}</code> "
        f"назначен администратором.",
        parse_mode="HTML"
    )

    await state.clear()


# =========================================================
# Удаление администратора
# =========================================================

@router.callback_query(F.data == "admins:remove")
async def remove_admin_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not await is_owner(callback.from_user.id):
        await callback.answer(
            "⛔ Только Owner.",
            show_alert=True
        )
        return

    await state.set_state("waiting_remove_admin_id")

    await callback.message.answer(
        "➖ <b>Удаление администратора</b>\n\n"
        "Отправьте Telegram ID администратора.",
        parse_mode="HTML"
    )

    await callback.answer()


@router.message(F.text, F.state == "waiting_remove_admin_id")
async def remove_admin_process(
    message: Message,
    state: FSMContext
):

    if not await is_owner(message.from_user.id):
        await state.clear()
        return

    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ ID должен состоять только из цифр."
        )
        return

    if user_id == OWNER_ID:
        await message.answer(
            "⛔ Owner нельзя удалить."
        )
        await state.clear()
        return

    role = await get_admin_role(user_id)

    if role != "admin":
        await message.answer(
            "❌ Такой администратор не найден."
        )
        await state.clear()
        return

    await remove_admin(user_id)

    await message.answer(
        f"✅ Администратор <code>{user_id}</code> удалён.",
        parse_mode="HTML"
    )

    await state.clear()


# =========================================================
# Список администраторов
# =========================================================

@router.callback_query(F.data == "admins:list")
async def admins_list(callback: CallbackQuery):

    if not await is_owner(callback.from_user.id):
        await callback.answer(
            "⛔ Только Owner.",
            show_alert=True
        )
        return

    admins = await get_admins()

    if not admins:
        text = "👥 <b>Администраторы</b>\n\nСписок пуст."
    else:
        lines = [
            "👥 <b>Администраторы</b>\n"
        ]

        for user_id, role, created_at in admins:

            if role == "owner":
                role_text = "👑 Owner"
            else:
                role_text = "🛠 Admin"

            lines.append(
                f"{role_text}\n"
                f"🆔 <code>{user_id}</code>\n"
                f"📅 {created_at}\n"
            )

        text = "\n".join(lines)

    await callback.message.edit_text(
        text,
        reply_markup=admins_keyboard(),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# Новые обращения
# =========================================================

@router.callback_query(F.data == "admin:new")
async def new_tickets(callback: CallbackQuery):

    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )
        return

    tickets = await get_tickets(
        status="open",
        is_new=True
    )

    if not tickets:
        await callback.message.edit_text(
            "📥 <b>Новые обращения</b>\n\n"
            "Новых обращений нет.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data="admin:menu"
                        )
                    ]
                ]
            ),
            parse_mode="HTML"
        )

        await callback.answer()
        return

    await callback.message.edit_text(
        "📥 <b>Новые обращения</b>\n\n"
        "Выберите тикет:",
        reply_markup=tickets_keyboard(tickets),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# Открытые тикеты
# =========================================================

@router.callback_query(F.data == "admin:open")
async def open_tickets(callback: CallbackQuery):

    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )
        return

    tickets = await get_tickets(
        status="open"
    )

    if not tickets:
        await callback.message.edit_text(
            "📂 <b>Открытые тикеты</b>\n\n"
            "Открытых тикетов нет.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data="admin:menu"
                        )
                    ]
                ]
            ),
            parse_mode="HTML"
        )

        await callback.answer()
        return

    await callback.message.edit_text(
        "📂 <b>Открытые тикеты</b>\n\n"
        "Выберите тикет:",
        reply_markup=tickets_keyboard(tickets),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# Жалобы
# =========================================================

@router.callback_query(F.data == "admin:complaints")
async def complaints(callback: CallbackQuery):

    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )
        return

    tickets = await get_tickets(
        status="open",
        support_type="Жалоба"
    )

    if not tickets:
        await callback.message.edit_text(
            "⚠️ <b>Жалобы</b>\n\n"
            "Открытых жалоб нет.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data="admin:menu"
                        )
                    ]
                ]
            ),
            parse_mode="HTML"
        )

        await callback.answer()
        return

    await callback.message.edit_text(
        "⚠️ <b>Жалобы</b>\n\n"
        "Выберите тикет:",
        reply_markup=tickets_keyboard(tickets),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# Вопросы
# =========================================================

@router.callback_query(F.data == "admin:questions")
async def questions(callback: CallbackQuery):

    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )
        return

    tickets = await get_tickets(
        status="open",
        support_type="Вопрос"
    )

    if not tickets:
        await callback.message.edit_text(
            "❓ <b>Вопросы</b>\n\n"
            "Открытых вопросов нет.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data="admin:menu"
                        )
                    ]
                ]
            ),
            parse_mode="HTML"
        )

        await callback.answer()
        return

    await callback.message.edit_text(
        "❓ <b>Вопросы</b>\n\n"
        "Выберите тикет:",
        reply_markup=tickets_keyboard(tickets),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# Просмотр тикета
# =========================================================

@router.callback_query(F.data.startswith("ticket:view:"))
async def view_ticket(callback: CallbackQuery, bot: Bot):

    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )
        return

    ticket_id = int(
        callback.data.split(":")[2]
    )

    ticket = await get_ticket(ticket_id)

    if ticket is None:
        await callback.answer(
            "Тикет не найден.",
            show_alert=True
        )
        return

    (
        ticket_id,
        user_id,
        support_type,
        text,
        status,
        created_at,
        closed_at
    ) = ticket

    # Помечаем новое обращение просмотренным
    # Если функция существует в БД
    try:
        from database.database import mark_ticket_seen

        await mark_ticket_seen(ticket_id)
    except ImportError:
        pass

    try:
        user = await bot.get_chat(user_id)

        full_name = user.full_name or "Неизвестно"

        if user.username:
            username = f"@{user.username}"
        else:
            username = "Нет username"

    except TelegramBadRequest:
        full_name = "Неизвестно"
        username = "Нет username"

    status_text = "🟢 Открыт" if status == "open" else "🔴 Закрыт"

    if "Жалоб" in support_type:
        type_text = "⚠️ Жалоба"
    else:
        type_text = "❓ Вопрос"

    user_link = (
        f'<a href="tg://user?id={user_id}">'
        f'{escape(full_name)}'
        f'</a>'
    )

    await callback.message.edit_text(
        f"🎫 <b>Тикет #{ticket_id}</b>\n\n"
        f"{type_text}\n\n"
        f"👤 {user_link}\n"
        f"🔗 {escape(username)}\n"
        f"🆔 <code>{user_id}</code>\n\n"
        f"📝 <b>Обращение:</b>\n"
        f"{escape(text)}\n\n"
        f"🕐 {created_at}\n"
        f"{status_text}",
        reply_markup=ticket_keyboard(
            ticket_id,
            status
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# Ответить на тикет
# =========================================================

@router.callback_query(F.data.startswith("ticket:reply:"))
async def start_ticket_reply(
    callback: CallbackQuery,
    state: FSMContext
):

    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )
        return

    ticket_id = int(
        callback.data.split(":")[2]
    )

    ticket = await get_ticket(ticket_id)

    if ticket is None:
        await callback.answer(
            "Тикет не найден.",
            show_alert=True
        )
        return

    if ticket[4] != "open":
        await callback.answer(
            "Этот тикет закрыт.",
            show_alert=True
        )
        return

    await state.update_data(
        reply_ticket_id=ticket_id
    )

    await state.set_state(
        AdminReplyForm.waiting_text
    )

    await callback.message.answer(
        f"💬 <b>Ответ на тикет #{ticket_id}</b>\n\n"
        f"Напишите сообщение, которое нужно отправить пользователю.",
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# Отправка ответа пользователю
# =========================================================

@router.message(
    AdminReplyForm.waiting_text,
    F.text
)
async def send_ticket_reply(
    message: Message,
    state: FSMContext,
    bot: Bot
):

    if not await is_admin(message.from_user.id):
        await state.clear()
        return

    data = await state.get_data()

    ticket_id = data.get("reply_ticket_id")

    if not ticket_id:
        await state.clear()
        return

    ticket = await get_ticket(ticket_id)

    if ticket is None:
        await message.answer(
            "❌ Тикет не найден."
        )
        await state.clear()
        return

    user_id = ticket[1]
    status = ticket[4]

    if status != "open":
        await message.answer(
            "🔴 Этот тикет уже закрыт."
        )
        await state.clear()
        return

    reply_text = message.text

    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"💬 <b>Ответ администратора</b>\n\n"
                f"{escape(reply_text)}\n\n"
                f"🎫 Тикет #{ticket_id}"
            ),
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        await message.answer(
            "❌ Не удалось отправить сообщение пользователю."
        )
        await state.clear()
        return

    await add_ticket_message(
        ticket_id=ticket_id,
        sender_id=message.from_user.id,
        sender_type="admin",
        text=reply_text
    )

    await message.answer(
        f"✅ Ответ по тикету #{ticket_id} отправлен."
    )

    await state.clear()


# =========================================================
# История тикета
# =========================================================

@router.callback_query(F.data.startswith("ticket:history:"))
async def ticket_history(callback: CallbackQuery):

    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )
        return

    ticket_id = int(
        callback.data.split(":")[2]
    )

    ticket = await get_ticket(ticket_id)

    if ticket is None:
        await callback.answer(
            "Тикет не найден.",
            show_alert=True
        )
        return

    messages = await get_ticket_messages(
        ticket_id
    )

    if not messages:
        history_text = "История сообщений пуста."
    else:
        lines = []

        for item in messages:
            (
                message_id,
                sender_id,
                sender_type,
                text,
                created_at
            ) = item

            if sender_type == "admin":
                sender = "🛠 Админ"
            else:
                sender = "👤 Пользователь"

            lines.append(
                f"{sender} • {created_at}\n"
                f"{escape(text)}"
            )

        history_text = "\n\n".join(lines)

    await callback.message.edit_text(
        f"📜 <b>История тикета #{ticket_id}</b>\n\n"
        f"{history_text}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ К тикету",
                        callback_data=f"ticket:view:{ticket_id}"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# Информация о пользователе
# =========================================================

@router.callback_query(F.data.startswith("ticket:user:"))
async def ticket_user(
    callback: CallbackQuery,
    bot: Bot
):

    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )
        return

    ticket_id = int(
        callback.data.split(":")[2]
    )

    ticket = await get_ticket(ticket_id)

    if ticket is None:
        await callback.answer(
            "Тикет не найден.",
            show_alert=True
        )
        return

    user_id = ticket[1]

    try:
        user = await bot.get_chat(user_id)

        full_name = user.full_name or "Неизвестно"

        if user.username:
            username = f"@{user.username}"
        else:
            username = "Нет username"

    except TelegramBadRequest:
        full_name = "Неизвестно"
        username = "Нет username"

    counts = await get_user_ticket_counts(
        user_id
    )

    user_link = (
        f'<a href="tg://user?id={user_id}">'
        f'{escape(full_name)}'
        f'</a>'
    )

    await callback.message.edit_text(
        f"👤 <b>Пользователь</b>\n\n"
        f"Имя: {user_link}\n"
        f"Username: {escape(username)}\n"
        f"ID: <code>{user_id}</code>\n\n"
        f"🎫 Всего тикетов: <b>{counts.get('total', 0)}</b>\n"
        f"🟢 Открытых: <b>{counts.get('open', 0)}</b>\n"
        f"🔴 Закрытых: <b>{counts.get('closed', 0)}</b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ К тикету",
                        callback_data=f"ticket:view:{ticket_id}"
                    )
                ]
            ]
        ),
        parse_mode="HTML"
    )

    await callback.answer()


# =========================================================
# Закрытие тикета
# =========================================================

@router.callback_query(F.data.startswith("ticket:close:"))
async def close_ticket_handler(callback: CallbackQuery):

    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )
        return

    ticket_id = int(
        callback.data.split(":")[2]
    )

    ticket = await get_ticket(ticket_id)

    if ticket is None:
        await callback.answer(
            "Тикет не найден.",
            show_alert=True
        )
        return

    if ticket[4] == "closed":
        await callback.answer(
            "Тикет уже закрыт."
        )
        return

    await close_ticket(ticket_id)

    await callback.answer(
        "✅ Тикет закрыт."
    )

    # Показываем обновлённый тикет
    ticket = await get_ticket(ticket_id)

    (
        ticket_id,
        user_id,
        support_type,
        text,
        status,
        created_at,
        closed_at
    ) = ticket

    if "Жалоб" in support_type:
        type_text = "⚠️ Жалоба"
    else:
        type_text = "❓ Вопрос"

    await callback.message.edit_text(
        f"🎫 <b>Тикет #{ticket_id}</b>\n\n"
        f"{type_text}\n\n"
        f"🆔 Пользователь: <code>{user_id}</code>\n\n"
        f"📝 {escape(text)}\n\n"
        f"🕐 {created_at}\n"
        f"🔴 Закрыт",
        reply_markup=ticket_keyboard(
            ticket_id,
            "closed"
        ),
        parse_mode="HTML"
    )


# =========================================================
# Повторное открытие
# =========================================================

@router.callback_query(F.data.startswith("ticket:reopen:"))
async def reopen_ticket_handler(callback: CallbackQuery):

    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )
        return

    ticket_id = int(
        callback.data.split(":")[2]
    )

    ticket = await get_ticket(ticket_id)

    if ticket is None:
        await callback.answer(
            "Тикет не найден.",
            show_alert=True
        )
        return

    await reopen_ticket(ticket_id)

    await callback.answer(
        "🔄 Тикет снова открыт."
    )

    # Возвращаемся к просмотру
    ticket = await get_ticket(ticket_id)

    (
        ticket_id,
        user_id,
        support_type,
        text,
        status,
        created_at,
        closed_at
    ) = ticket

    if "Жалоб" in support_type:
        type_text = "⚠️ Жалоба"
    else:
        type_text = "❓ Вопрос"

    await callback.message.edit_text(
        f"🎫 <b>Тикет #{ticket_id}</b>\n\n"
        f"{type_text}\n\n"
        f"🆔 Пользователь: <code>{user_id}</code>\n\n"
        f"📝 {escape(text)}\n\n"
        f"🕐 {created_at}\n"
        f"🟢 Открыт",
        reply_markup=ticket_keyboard(
            ticket_id,
            "open"
        ),
        parse_mode="HTML"
    )


# =========================================================
# Статистика
# =========================================================

@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):

    if not await is_admin(callback.from_user.id):
        await callback.answer(
            "⛔ Нет доступа.",
            show_alert=True
        )
        return

    stats = await get_ticket_stats()

    await callback.message.edit_text(
        "📊 <b>Статистика DevHub</b>\n\n"
        f"🎫 Всего тикетов: <b>{stats.get('total', 0)}</b>\n"
        f"📅 За сегодня: <b>{stats.get('today', 0)}</b>\n\n"
        f"📥 Новых: <b>{stats.get('new', 0)}</b>\n"
        f"🟢 Открытых: <b>{stats.get('open', 0)}</b>\n"
        f"🔴 Закрытых")