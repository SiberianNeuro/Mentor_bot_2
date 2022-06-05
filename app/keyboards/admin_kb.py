from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.db.get_buttons import get_stage_buttons, get_result_buttons

button_load = KeyboardButton('Загрузить')
button_cancel = KeyboardButton('Отмена')
button_search = KeyboardButton('Найти')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).row(button_load, button_search)
button_case_cancel = ReplyKeyboardMarkup(resize_keyboard=True).row(button_cancel)

"""Клавиатуры загрузки протоколов"""

exam_callback = CallbackData('exam', 'action', 'action_data')


#Клавиатура загрузки формата опроса
def get_stage_keyboard():
    buttons = get_stage_buttons()
    format_keyboard = InlineKeyboardMarkup(row_width=2)
    for data, text in buttons:
        format_keyboard.insert(InlineKeyboardButton(
            text=text, callback_data=exam_callback.new(action='format', action_data=data)
        ))
    return format_keyboard


# Клавиатура загрузки статуса опроса
def get_result_keyboard():
    buttons = get_result_buttons()
    result_keyboard = InlineKeyboardMarkup(row_width=1)
    for data, text in buttons:
        result_keyboard.insert(InlineKeyboardButton(
            text=text, callback_data=exam_callback.new(action='result', action_data=data)
        ))
    return result_keyboard


# Кнопка "удалить" под каждым протоколом
def get_delete_button(id: int) -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(
            'Удалить запись аттестации', callback_data=exam_callback.new(action='delete', action_data=id))
    delete_keyboard = InlineKeyboardMarkup(row_width=1)
    delete_keyboard.add(button)
    return delete_keyboard


"""Клавиатуры рассылок"""

mailing_callback = CallbackData('mailing', 'action', 'stdout')


# Стартовая клавиатура
def get_mailing_menu():
    buttons = (
        InlineKeyboardButton(text='Загрузить', callback_data='upload'),
        InlineKeyboardButton(text='Отправить')
    )