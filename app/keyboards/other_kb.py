from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.db.get_buttons import get_role_buttons

start_register = CallbackData("start", "status")
register_callback = CallbackData("register", "status", "role")


def get_register_button():
    button = InlineKeyboardButton('Начать регистрацию', callback_data=start_register.new(status='yes'))
    register_keyboard = InlineKeyboardMarkup(row_width=1)
    register_keyboard.add(button)
    return register_keyboard


def get_pos_keyboard():
    role_list = get_role_buttons()
    print(role_list)
    role_keyboard = InlineKeyboardMarkup(row_width=2)
    for data, text in role_list:
        role_keyboard.insert(InlineKeyboardButton(text=text,
                                              callback_data=register_callback.new(status='position', role=data)))
    return role_keyboard


def get_cancel_button():
    button = KeyboardButton('отмена')
    cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_keyboard.add(button)
    return cancel_keyboard