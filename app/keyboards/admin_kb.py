from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

button_load = KeyboardButton('Загрузить')
button_cancel = KeyboardButton('Отмена')
button_search = KeyboardButton('Найти')

button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).row(button_load, button_search)
button_case_cancel = ReplyKeyboardMarkup(resize_keyboard=True).row(button_cancel)

exam_callback = CallbackData('exam', 'action', 'action_data')

def get_format_keyboard():
    buttons = (
        ('🟢 Аттестация на 4 день', 'Опрос 4-го дня'),
        ('🟡 Внутренняя аттестация', 'Внутренний опрос'),
        ('🟠 На И.О.', 'Со стажера на И.О.'),
        ('🔴 На врача', 'С И.О. на врача'),
        ('🔵 Аттестация помощника', 'Со стажера L1 на сотрудника')
    )
    format_keyboard = InlineKeyboardMarkup(row_width=2)
    for text, data in buttons:
        format_keyboard.insert(InlineKeyboardButton(
            text=text, callback_data=exam_callback.new(action='format', action_data=data)
        ))
    return format_keyboard


def get_status_keyboard():
    buttons = (
        InlineKeyboardButton(
            '😏 Прошел', callback_data=exam_callback.new(action='status', action_data='Аттестация пройдена ✅')
        ),
        InlineKeyboardButton(
            '😒 Не прошел', callback_data=exam_callback.new(action='status', action_data='Аттестация не пройдена ❌')
        )
    )
    status_keyboard = InlineKeyboardMarkup(row_width=2)
    status_keyboard.add(*buttons)
    return status_keyboard

def get_delete_button(obj):
    buttons = (
        InlineKeyboardButton(
            'Удалить запись аттестации', callback_data=exam_callback.new(action='delete', action_data=obj)
        )
    )
    delete_keyboard = InlineKeyboardMarkup(row_width=1)
    delete_keyboard.add(*buttons)
    return delete_keyboard
