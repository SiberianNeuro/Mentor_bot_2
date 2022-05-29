from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMAdmin(StatesGroup):
    document = State()
    form = State()
    status = State()
    retake = State()
    link = State()
    trainee_name = State()


class FSMRegister(StatesGroup):
    chat_id = State()
    name = State()
    position = State()
    username = State()
    reg_time = State()