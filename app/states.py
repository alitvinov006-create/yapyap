from aiogram.fsm.state import StatesGroup, State


class Reg(StatesGroup):
    course = State()
    fac = State()
    group = State()

class Mailing(StatesGroup):
    waiting_for_text = State()

class AdminAdd(StatesGroup):
    waiting_for_text = State()