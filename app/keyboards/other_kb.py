from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.db.get_buttons import get_role_buttons, get_education_buttons

register_callback = CallbackData("register", "stage", "stage_data")


async def get_register_button():
    button = InlineKeyboardButton('Начать регистрацию', callback_data=register_callback.new(stage='yes', stage_data='yes'))
    register_keyboard = InlineKeyboardMarkup(row_width=1)
    register_keyboard.add(button)
    return register_keyboard


async def get_pos_keyboard():
    role_list = await get_role_buttons()
    role_keyboard = InlineKeyboardMarkup(row_width=2)
    for data, text in role_list:
        role_keyboard.insert(InlineKeyboardButton(text=text,
                                              callback_data=register_callback.new(stage='position', stage_data=data)))
    return role_keyboard


async def get_cancel_button():
    button = KeyboardButton('Отмена')
    cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_keyboard.add(button)
    return cancel_keyboard


async def get_education_keyboard():
    buttons = await get_education_buttons()
    education_keyboard = InlineKeyboardMarkup(row_width=1)
    for data, text in buttons:
        education_keyboard.insert(InlineKeyboardButton(
            text=text, callback_data=register_callback.new(stage='education', stage_data=data)
        ))
    return education_keyboard


async def get_spec_keyboard():
    buttons = (
        InlineKeyboardButton(text='Не поступал и не собираюсь', callback_data=register_callback.new(stage='spec', stage_data='1')),
        InlineKeyboardButton(text='Не поступал, но собираюсь', callback_data=register_callback.new(stage='spec', stage_data='2')),
        InlineKeyboardButton(text='Учусь прямо сейчас', callback_data=register_callback.new(stage='spec', stage_data='3')),
        InlineKeyboardButton(text='Закончил обучение', callback_data=register_callback.new(stage='spec', stage_data='4'))
    )
    spec_keyboard = InlineKeyboardMarkup(row_width=1)
    spec_keyboard.add(*buttons)
    return spec_keyboard
