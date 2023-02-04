from aiogram.utils.keyboard import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton
from app.models.user import User


async def keyboard_generator(user):

    mentor_buttons = [
        [
            KeyboardButton(text='Загрузить опрос ⏏'),
            KeyboardButton(text='Найти опрос 👀'),
            KeyboardButton(text='Рассылка тестов 🔊')
        ],
        [
            KeyboardButton(text='Найти сотрудника 👨‍⚕'),
            KeyboardButton(text='Звонки стажеров 📞')
        ]
    ]

    dutyline_doc_buttons = [
        KeyboardButton(text='Заглушка')
    ]

    doc_L3_buttons = [
        KeyboardButton(text='Заглушка')
    ]

    doc_L1_buttons = [
        KeyboardButton(text='Заглушка')
    ]
    target_buttons = mentor_buttons

    keyboard = ReplyKeyboardMarkup(keyboard=target_buttons, resize_keyboard=True)

    return keyboard


async def get_cancel_button():
    button = [
        [
            KeyboardButton(text='Отмена')
        ]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)

    return keyboard