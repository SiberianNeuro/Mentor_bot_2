from aiogram.utils import executor
from loguru import logger

from loader import dispatcher as dp

from app.utils.set_bot_commands import set_default_commands




async def on_startup(dp):
    from app import filters, middlewares


    await set_default_commands(dp)  # Установка меню команд
    middlewares.setup(dp)
    filters.setup(dp)

    from app.handlers.users import admin, mailing_admin, other
    from app.handlers.errors import error_handler
    logger.info("Configure handlers...")
    admin.setup(dp) # Регистрация админ-хэндлеров
    mailing_admin.setup(dp) # Регистрация хэндлеров админ-рассылки
    other.setup(dp) # Регистрация хэндлеров обычных пользователей
    error_handler.setup(dp) # Регистрация error-хэндлеров

if __name__ == '__main__':
    from app.utils.misc import logging

    logging.setup()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
