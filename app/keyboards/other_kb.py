from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.db.get_buttons import get_role_buttons, get_city_buttons

start_register = CallbackData("start", "status")
register_callback = CallbackData("register", "stage", "data")


def get_register_button():
    button = InlineKeyboardButton('Начать регистрацию', callback_data=start_register.new(status='yes'))
    register_keyboard = InlineKeyboardMarkup(row_width=1)
    register_keyboard.add(button)
    return register_keyboard


async def get_city_keyboard():
    city_list = await get_city_buttons()
    city_keyboard = InlineKeyboardMarkup(row_width=2)
    for data, text in city_list:
        city_keyboard.insert(InlineKeyboardButton(
            text=text, callback_data=register_callback.new(stage='city', data=data)
        ))
    return city_keyboard


async def get_pos_keyboard():
    role_list = await get_role_buttons()
    role_keyboard = InlineKeyboardMarkup(row_width=2)
    for data, text in role_list:
        role_keyboard.insert(InlineKeyboardButton(text=text,
                                              callback_data=register_callback.new(stage='position', data=data)))
    return role_keyboard


def get_cancel_button():
    button = KeyboardButton('отмена')
    cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_keyboard.add(button)
    return cancel_keyboard


def get_spec_keyboard():
    buttons = (
        InlineKeyboardButton(text='Не поступал и не собираюсь', callback_data=0),
        InlineKeyboardButton(text='Не поступал, но собираюсь', callback_data=1),
        InlineKeyboardButton(text='Учусь прямо сейчас', callback_data=2),
        InlineKeyboardButton(text='Закончил обучение', callback_data=3)
    )
    spec_keyboard = InlineKeyboardMarkup(row_width=1)
    spec_keyboard.add(*buttons)
    return spec_keyboard