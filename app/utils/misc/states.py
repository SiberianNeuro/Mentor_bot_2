from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMAdmin(StatesGroup):
    document = State()
    form = State()
    status = State()
    retake = State()
    link = State()
    trainee_name = State()


class FSMRegister(StatesGroup):
    name = State()
    position = State()


class Mailing(StatesGroup):
    workers = State()
    process_workers = State()
    start_mailing = State()
    process_mailing = State()
    confirm_mailing = State()
