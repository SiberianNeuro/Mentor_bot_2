from aiogram.utils import executor

from app.utils.set_bot_commands import set_default_commands
from loader import dispatcher as dp

from app.handlers.users import admin, mailing_admin, other
from app.handlers.errors import error_handler


async def on_startup(dp):
    await set_default_commands(dp)  # Установка меню команд

    admin.register_handlers_admin(dp) # Регистрация админ-хэндлеров
    mailing_admin.register_mailing_handlers(dp) # Регистрация хэндлеров админ-рассылки
    other.register_handlers_other(dp) # Регистрация хэндлеров обычных пользователей
    error_handler.register_error_handler(dp) # Регистрация error-хэндлеров

if __name__ == '__main__':
    from app.utils.misc import logging

    logging.setup()  # Установка уровня логгирования
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
