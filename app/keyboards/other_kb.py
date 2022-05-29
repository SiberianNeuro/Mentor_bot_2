from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram_calendar import SimpleCalendar

start_register = CallbackData("start", "status")
register_callback = CallbackData("register", "status", "position")

def get_register_button():
    button = [
        InlineKeyboardButton('Начать регистрацию', callback_data=start_register.new(status='yes'))
    ]
    register_keyboard = InlineKeyboardMarkup(row_width=1)
    register_keyboard.add(*button)
    return register_keyboard


def get_pos_keyboard():
    pos_list = ('Врач-стажер', 'И.О. врача', 'Врач', 'Сеньор врачей')
    pos_keyboard = InlineKeyboardMarkup(row_width=2)
    for data in pos_list:
        pos_keyboard.insert(InlineKeyboardButton(text=data,
                                              callback_data=register_callback.new(status='position', position=data)))
    return pos_keyboard


def get_cancel_button():
    button = KeyboardButton('отмена')
    cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_keyboard.add(button)
    return cancel_keyboard