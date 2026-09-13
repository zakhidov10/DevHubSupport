from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.Keyboards import (
    keyboard,
    choice_keyboard,
    main_menu,
    skip_keyboard,
    back,
    faq_choice,
    cancel_button,
)

from forms.support import SupportForm
from handlers.support import finish_support


router = Router()


# =========================
# START
# =========================

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        f"Здравствуйте, {message.from_user.full_name}!\n\n"
        "Добро пожаловать в DevHub 👋\n"
        "Выберите действие:",
        reply_markup=keyboard
    )


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

@router.message(F.text == "🏠 Главное меню")
async def home(message: Message):
    await message.answer(
        "Главное меню 🏠\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )


@router.message(F.text == "❌ Отмена")
async def cancelation_button(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Действие отменено.\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )


# =========================
# О DEVHUB
# =========================

@router.message(F.text == "ℹ️ О DevHub")
async def about(message: Message):
    await message.answer(
        "ℹ️ О DevHub\n\n"
        "DevHub — платформа для программистов и разработчиков, "
        "созданная для поиска людей в команду и совместной работы "
        "над проектами.\n\n"

        "💻 Здесь вы можете:\n"
        "• найти разработчиков нужного направления;\n"
        "• рассказать о своих навыках;\n"
        "• найти единомышленников;\n"
        "• собрать команду для своего проекта.\n\n"

        "🚀 DevHub объединяет людей, которые хотят создавать "
        "проекты и развиваться в программировании.",
        reply_markup=main_menu
    )


# =========================
# FAQ
# =========================

@router.message(F.text == "❔ FAQ")
async def faq(message: Message):
    await message.answer(
        "❔ FAQ\n\n"
        "Выберите интересующий раздел:",
        reply_markup=faq_choice
    )


@router.message(F.text == "📌 Основное")
async def mainfaq(message: Message):
    await message.answer(
        "📌 Основное\n\n"

        "❓ Что такое DevHub?\n"
        "DevHub — бот для поиска разработчиков "
        "и участников в команду.\n\n"

        "🚀 Как начать?\n"
        "Нажмите /start и выберите нужный раздел.\n\n"

        "👥 Для кого DevHub?\n"
        "Для разработчиков, дизайнеров и всех, "
        "кто хочет найти команду или участников проекта.",
        reply_markup=back
    )


@router.message(F.text == "👤 Анкета")
async def anketa(message: Message):
    await message.answer(
        "👤 Анкета\n\n"

        "❓ Что нужно указать?\n"
        "Имя или ник, информацию о себе, опыт, "
        "технологии, проекты и GitHub.\n\n"

        "✏️ Можно ли изменить анкету?\n"
        "Да, информацию можно будет изменить.\n\n"

        "🔗 Зачем нужен GitHub?\n"
        "Чтобы другие пользователи могли посмотреть "
        "ваши проекты и работы.",
        reply_markup=back
    )


@router.message(F.text == "🔎 Поиск анкет")
async def poisk(message: Message):
    await message.answer(
        "🔎 Поиск анкет\n\n"

        "Здесь можно будет просматривать анкеты "
        "других участников DevHub.\n\n"

        "👀 В анкете могут отображаться:\n"
        "• имя;\n"
        "• информация о пользователе;\n"
        "• технологии;\n"
        "• проекты;\n"
        "• GitHub.",
        reply_markup=back
    )


@router.message(F.text == "⚙️ Профиль")
async def profile(message: Message):
    await message.answer(
        "⚙️ Профиль\n\n"

        "В профиле можно будет изменить:\n"
        "📸 фотографию;\n"
        "📝 информацию о себе;\n"
        "💻 технологии;\n"
        "🔗 GitHub.",
        reply_markup=back
    )


@router.message(F.text == "🛠 Проблемы")
async def problems(message: Message):
    await message.answer(
        "🛠 Проблемы\n\n"

        "Если вы столкнулись с проблемой или "
        "не понимаете, как пользоваться ботом, "
        "обратитесь в поддержку DevHub.",
        reply_markup=back
    )


# =========================
# НАЗАД В FAQ
# =========================

@router.message(F.text == "🔙 Назад")
async def back_to_faq(message: Message):
    await message.answer(
        "❔ Выберите раздел:",
        reply_markup=faq_choice
    )


# =========================
# ПОДДЕРЖКА
# =========================

@router.message(F.text == "💬 Поддержка")
async def support_menu(message: Message):
    await message.answer(
        "💬 Поддержка\n\n"
        "Выберите тип обращения:",
        reply_markup=choice_keyboard
    )


@router.message(
    F.text.in_({
        "❓ Вопрос",
        "⚠️ Жалоба"
    })
)
async def support(message: Message, state: FSMContext):
    await state.update_data(
        support_type=message.text
    )

    await state.set_state(
        SupportForm.waiting_question
    )

    await message.answer(
        "📝 Опишите вашу проблему или вопрос:",
        reply_markup=cancel_button
    )


@router.message(
    SupportForm.waiting_question,
    F.text
)
async def get_text(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        text=message.text
    )

    await message.answer(
        "📷 Хотите добавить фотографию?\n\n"
        "Если фото нет, нажмите «Пропустить».",
        reply_markup=skip_keyboard
    )

    await state.set_state(
        SupportForm.waiting_photo
    )


@router.message(
    SupportForm.waiting_photo,
    F.photo
)
async def get_photo(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    await state.update_data(
        photo=message.photo[-1].file_id
    )

    await finish_support(
        message,
        state,
        bot,
        keyboard
    )


@router.message(
    SupportForm.waiting_photo,
    F.text == "⏩ Пропустить"
)
async def skip_photo(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    await finish_support(
        message,
        state,
        bot,
        keyboard
    )


# =========================
# СОТРУДНИЧЕСТВО
# =========================

@router.message(F.text == "🤝 Сотрудничество")
async def cooperation(message: Message):
    await message.answer(
        "🤝 Сотрудничество с DevHub\n\n"

        "Хотите предложить совместный проект "
        "или обсудить партнёрство?\n\n"

        "Напишите администрации, кратко описав "
        "ваше предложение и формат сотрудничества.",
        reply_markup=main_menu
    )