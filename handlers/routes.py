from handlers.support import ADMIN_ID, finish_support
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import (
    Message,
    KeyboardButton,

    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext
from keyboards.Keyboards import (
    keyboard, 
    choice_keyboard, 
    main_menu, 
    skip_keyboard,
    back,
    faq_choice,
    cancel_button
    )

from forms.support import SupportForm
router = Router()


@router.message(Command('start'))
async def start(message: Message):
    await message.answer(
        f"Здраствуйте, {message.from_user.full_name}\nВыберите действие",
    reply_markup = keyboard
    )

@router.message(F.text == 'О нас ℹ️')
async def about(message: Message):
    await message.answer(
        "О DevHub\n\n\n"
        "DevHub — это платформа для программистов и разработчиков, созданная для поиска людей в команду и совместной работы над проектами.\n\n"
        "💻 Здесь вы можете\n• найти разработчиков нужного направления;\n• рассказать о своих навыках;\n• найти единомышленников;\n• собрать команду для своего проекта.\n\n"
        "🚀 DevHub объединяет людей, которые хотят создавать проекты, развиваться в программировании и работать вместе.",
        reply_markup=main_menu
    )

@router.message(F.text == "FAQ 🔍")
async def faq(message: Message):
    await message.answer("Выберите раздел вопроса", reply_markup=faq_choice)

@router.message(F.text == "Основное 📌")
async def mainfaq(message: Message):
    await message.answer(
        "❓ Что такое DevHub?\n"
        "DevHub — бот для поиска разработчиков и участников в команду.\n\n"
        "🚀 Как начать?\n"
        "Нажмите /start и заполните свою анкету.\n\n"
        "👥 Для кого DevHub?\n"
        "Для разработчиков, дизайнеров и всех, кто хочет найти команду или участников для проекта.",
        reply_markup=back
    )

@router.message(F.text == "Анкета 👤")
async def anketa(message: Message):
    await message.answer(
        "❓ Что нужно указать?\n"
        "Возраст, имя или ник, информацию о себе, опыт, технологии, проекты и GitHub.\n\n"
        "✏️ Можно ли изменить анкету?\n"
        "Да. Вы можете изменить текст или фотографию профиля.\n\n"
        "🔄 Можно ли заполнить анкету заново?\n"
        "Да. Используйте кнопку «Заполнить анкету заново».\n\n"
        "🔗 Зачем нужен GitHub?\n"
        "Чтобы другие пользователи могли посмотреть ваши проекты и работы.",
        reply_markup=back
    )

@router.message(F.text == "Поиск анкет 🔎")
async def poisk(message: Message):
    await message.answer(
       "❓ Как посмотреть других пользователей?\n"
        "Нажмите «Смотреть анкеты» в меню профиля.\n\n"
        "👀 Что видно в анкете?\n"
        "Фото, имя, возраст, информацию о пользователе и ссылку на GitHub.\n\n"
        "🤝 Зачем смотреть анкеты?\n"
        "Чтобы найти подходящих людей для общения и совместной работы.",
        reply_markup=back 
    )
@router.message(F.text == "Профиль ⚙️")
async def profile(message: Message):
    await message.answer(
        "❓ Что можно изменить?\n\n"
        "📸 Фото анкеты — заменить фотографию.\n"
        "📝 Текст анкеты — изменить информацию о себе.\n"
        "🔄 Анкету заново — полностью заполнить профиль повторно.",
        reply_markup=back
    )

@router.message(F.text == "Проблемы 🛠️")
async def problems(message: Message):
    await message.answer(
        "❓ Указал неправильную информацию. Что делать?\n"
        "Просто отредактируйте свою анкету.\n\n"
        "🤔 Не понимаю, как пользоваться ботом.\n"
        "Изучите этот FAQ или обратитесь к администрации DevHub.",
        reply_markup=back
    )

@router.message(F.text.in_(["Вопрос", "Жалоба", "Не нашёл нужного раздела ❓"]))
async def support(message: Message, state: FSMContext):
    await state.update_data(support_type=message.text)
    await state.set_state(SupportForm.waiting_question)

    await message.answer(
        "Пожалуйста, введите текст вашего обращения.",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(SupportForm.waiting_question, F.text)
async def get_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)

    await message.answer(
        "Спасибо! Теперь отправьте фото (если есть) или нажмите «Пропустить».",
        reply_markup=skip_keyboard
    )

    await state.set_state(SupportForm.waiting_photo)

@router.message(SupportForm.waiting_photo, F.photo)
async def get_photo(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(photo=message.photo[-1].file_id)

    await finish_support(message, state, bot, keyboard )


@router.message(SupportForm.waiting_photo, F.text == "Пропустить ⏩")
async def skip_photo(message: Message, state: FSMContext, bot: Bot):
    await finish_support(message, state, bot, keyboard)

@router.message(F.text == "Обратиться к администратору 🧑‍💻")
async def notanswer(message: Message):
    await message.answer("Выберите тип обрашение", reply_markup=choice_keyboard)


@router.message(F.text == "Не нашёл нужного раздела ❓")
async def notanswer(message: Message):
    await message.answer("Тогда обратитесь к администрации")

@router.message(F.text =="Вернуться в главное меню 🏠")
async def home(message: Message):
    await message.answer("Вы вернулись в главное меню", reply_markup=keyboard)

@router.message(F.text == "Вернуться назад 🔙")
async def back1(message: Message):
    await message.answer("Выберите раздел вопроса", reply_markup=faq_choice)

@router.message(F.text == "Соотрудничество 🤝")
async def back1(message: Message):
    await message.answer(
        "🤝 Сотрудничество с DevHub\n\n"
        "Хотите сотрудничать с DevHub, предложить совместный проект "
        "или обсудить партнёрство?\n\n"
        "Напишите нам, кратко рассказав о вашем предложении "
        "и формате сотрудничества.\n\n"
        "👤 Для связи: @slimnoob,@xba16",
        reply_markup=main_menu
    )

