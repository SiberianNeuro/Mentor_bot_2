from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

button_load = KeyboardButton('Загрузить')
button_cancel = KeyboardButton('Отмена')
button_search = KeyboardButton('Найти')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).row(button_load, button_search)
button_case_cancel = ReplyKeyboardMarkup(resize_keyboard=True).row(button_cancel)

exam_callback = CallbackData('exam', 'action', 'action_data')

def get_format_keyboard():
    buttons = [
        InlineKeyboardButton(
            '🟢 Аттестация на 4 день', callback_data=exam_callback.new(action='format', action_data='Опрос 4-го дня')
        ),
        InlineKeyboardButton(
            '🟡 Внутренняя аттестация', callback_data=exam_callback.new(action='format', action_data='Внутренний опрос')
        ),
        InlineKeyboardButton(
            '🟠 На И.О.', callback_data=exam_callback.new(action='format', action_data='Со стажера на И.О.')
        ),
        InlineKeyboardButton(
            '🔴 На врача', callback_data=exam_callback.new(action='format', action_data='С И.О. на врача')
        ),
        InlineKeyboardButton(
            '🔵 Аттестация помощника',
            callback_data=exam_callback.new(action='format', action_data='Со стажера L1 на сотрудника')
        )
    ]
    format_keyboard = InlineKeyboardMarkup(row_width=2)
    format_keyboard.add(*buttons)
    return format_keyboard


def get_status_keyboard():
    buttons = [
        InlineKeyboardButton(
            '😏 Прошел', callback_data=exam_callback.new(action='status', action_data='Аттестация пройдена ✅')
        ),
        InlineKeyboardButton(
            '😒 Не прошел', callback_data=exam_callback.new(action='status', action_data='Аттестация не пройдена ❌')
        )
    ]
    status_keyboard = InlineKeyboardMarkup(row_width=2)
    status_keyboard.add(*buttons)
    return status_keyboard

def get_delete_button(obj):
    buttons = [
        InlineKeyboardButton(
            'Удалить запись аттестации', callback_data=exam_callback.new(action='delete', action_data=obj)
        )
    ]
    delete_keyboard = InlineKeyboardMarkup(row_width=1)
    delete_keyboard.add(*buttons)
    return delete_keyboard

search_buttons = [
    InlineKeyboardButton('Поиск по фамилии', callback_data='name'),
    InlineKeyboardButton('Поиск по периоду', callback_data='date'),
]
search_button_case = InlineKeyboardMarkup(row_width=2).row(*search_buttons)