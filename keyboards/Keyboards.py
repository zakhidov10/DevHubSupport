from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="О нас ℹ️"), KeyboardButton(text="FAQ 🔍")],
        [KeyboardButton(text="Обратиться к администратору 🧑‍💻")],
        [KeyboardButton(text="Соотрудничество 🤝")]
    ],
    resize_keyboard=True
)
choice_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вопрос"), KeyboardButton(text="Жалоба")], 
        [KeyboardButton(text="Вернуться в главное меню 🏠")]
    ],
    resize_keyboard=True
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вернуться в главное меню 🏠")]
    ],
    resize_keyboard=True
)

skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пропустить ⏩")]
    ],
    resize_keyboard=True
)
faq_choice = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Основное 📌"), KeyboardButton(text="Анкета 👤"), KeyboardButton(text="Поиск анкет 🔎")],  # ← запятая
        [KeyboardButton(text="Профиль ⚙️"), KeyboardButton(text="Проблемы 🛠️")], 
        [KeyboardButton(text="Не нашёл нужного раздела ❓"),KeyboardButton(text="Вернуться в главное меню 🏠")]
    ],
    resize_keyboard=True
)  

back = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Вернуться назад 🔙")]
    ],
    resize_keyboard=True
)

cancel_button= ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена")]
    ],
    resize_keyboard=True
)