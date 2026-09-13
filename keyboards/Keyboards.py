from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="ℹ️ О DevHub"),
            KeyboardButton(text="❔ FAQ"),
        ],
        [
            KeyboardButton(text="💬 Поддержка"),
            KeyboardButton(text="🤝 Сотрудничество"),
        ],
    ],
    resize_keyboard=True,
)


choice_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="❓ Вопрос"),
            KeyboardButton(text="⚠️ Жалоба"),
        ],
        [
            KeyboardButton(text="🏠 Главное меню"),
        ],
    ],
    resize_keyboard=True,
)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)


skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏩ Пропустить")],
        [KeyboardButton(text="❌ Отмена")],
    ],
    resize_keyboard=True,
)


cancel_button = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Отмена")],
    ],
    resize_keyboard=True,
)


faq_choice = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📌 Основное"),
            KeyboardButton(text="👤 Анкета"),
        ],
        [
            KeyboardButton(text="🔎 Поиск анкет"),
            KeyboardButton(text="⚙️ Профиль"),
        ],
        [
            KeyboardButton(text="🛠 Проблемы"),
        ],
        [
            KeyboardButton(text="🏠 Главное меню"),
        ],
    ],
    resize_keyboard=True,
)


back = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Назад")],
        [KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
)