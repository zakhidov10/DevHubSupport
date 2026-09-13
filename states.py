from aiogram.fsm.state import State, StatesGroup


class SupportForm(StatesGroup):
    waiting_question = State()
    waiting_photo = State()