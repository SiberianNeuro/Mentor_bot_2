import logging

from aiogram.utils import executor

from app.utils.set_bot_commands import set_default_commands
from loader import dispatcher

from app.handlers.users import admin, other, overlord, mailing_admin
from app.handlers.errors import error_handler


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    logging.basicConfig(#filename="logfile.log",
                        #filemode="w",
                        format=u"%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
                        # level=logging.INFO,
                        level=logging.DEBUG,  # Можно заменить на другой уровень логгирования.
                        )
    admin.register_handlers_admin(dispatcher)
    mailing_admin.register_mailing_handlers(dispatcher)
    overlord.register_handlers_overlord(dispatcher)
    other.register_handlers_other(dispatcher)
    error_handler.register_error_handler(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True, on_startup=on_startup)