from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.db.get_buttons import get_stage_buttons, get_result_buttons, get_role_buttons


async def get_admin_kb():
    buttons = [
        KeyboardButton('Загрузить'),
        KeyboardButton('Найти')
    ]
    admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    admin_kb.row(*buttons)
    return admin_kb


"""Клавиатуры загрузки протоколов"""

exam_callback = CallbackData('exam', 'action', 'action_data')


async def get_overload_keyboard():
    buttons = (
        InlineKeyboardButton(text='Подтвердить ✅', callback_data=exam_callback.new(action='overload', action_data='1')),
        InlineKeyboardButton(text='Перезагрузить 🔄', callback_data=exam_callback.new(action='overload', action_data='2'))
    )
    overload_keyboard = InlineKeyboardMarkup(row_width=1)
    overload_keyboard.add(*buttons)
    return overload_keyboard


#Клавиатура загрузки формата опроса
async def get_stage_keyboard():
    buttons = await get_stage_buttons()
    format_keyboard = InlineKeyboardMarkup(row_width=2)
    for data, text in buttons:
        format_keyboard.insert(InlineKeyboardButton(
            text=text, callback_data=exam_callback.new(action='format', action_data=data)
        ))
    return format_keyboard


# Клавиатура загрузки статуса опроса
async def get_result_keyboard():
    buttons = await get_result_buttons()
    result_keyboard = InlineKeyboardMarkup(row_width=1)
    for data, text in buttons:
        result_keyboard.insert(InlineKeyboardButton(
            text=text, callback_data=exam_callback.new(action='result', action_data=data)
        ))
    return result_keyboard


# Кнопка "удалить" под каждым протоколом
async def get_delete_button(id: int) -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(
            'Удалить запись аттестации', callback_data=exam_callback.new(action='delete', action_data=id))
    delete_keyboard = InlineKeyboardMarkup(row_width=1)
    delete_keyboard.add(button)
    return delete_keyboard


"""Клавиатуры рассылок"""

mailing_callback = CallbackData('mailing', 'action', 'c_data')


async def get_mailing_keyboard():
    buttons = [
        InlineKeyboardButton(text='Добавить', callback_data=mailing_callback.new(action='load', c_data=0)),
        InlineKeyboardButton(text='Подтвердить', callback_data=mailing_callback.new(action='confirm', c_data=0))
    ]
    mailing_keyboard = InlineKeyboardMarkup(row_width=2)
    mailing_keyboard.add(*buttons)
    return mailing_keyboard


async def text_switch_button():
    button = InlineKeyboardButton(text='Загрузить текст(-ы)', callback_data=mailing_callback.new(action='execute', c_data=0))
    text_switch_button = InlineKeyboardMarkup(row_width=1)
    text_switch_button.add(button)
    return text_switch_button


async def get_execute_button():
    button = InlineKeyboardButton(text='Начать рассылку', callback_data=mailing_callback.new(action='execute', c_data=0))
    execute_button = InlineKeyboardMarkup(row_width=1)
    execute_button.add(button)
    return execute_button


async def get_roles_keyboard():
    buttons = await get_role_buttons()
    roles_keyboard = InlineKeyboardMarkup(row_width=2)
    for data, text in buttons:
        roles_keyboard.insert(InlineKeyboardButton(text=text, callback_data=mailing_callback.new(action='worker', c_data=data)))
    return roles_keyboard
