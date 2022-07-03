from aiogram.dispatcher.filters.state import StatesGroup, State


# Состояния для опросов
class FSMAdmin(StatesGroup):
    document = State()
    confirm = State()
    link = State()
    trainee_name = State()


# Состояния для регистрации пользователя
class FSMRegister(StatesGroup):
    name = State()
    city = State()
    role = State()
    med_education = State()
    traineeship = State()
    profession = State()
    start_year = State()
    end_year = State()
    phone = State()
    email = State()
    birthdate = State()


# Состояния для рассылки
class Mailing(StatesGroup):
    workers = State()
    process_workers = State()
    start_mailing = State()
    process_mailing = State()
    confirm_mailing = State()
