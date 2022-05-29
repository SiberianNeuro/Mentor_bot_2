from aiogram.types import ReplyKeyboardMarkup, KeyboardButton#, ReplyKeyboardRemove

b1 = KeyboardButton('/Режим_работы')
# b2 = KeyboardButton('Расположение')
# b3 = KeyboardButton('Меню')

kb_trainee = ReplyKeyboardMarkup(resize_keyboard=True)

kb_trainee.add(b1)