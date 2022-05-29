import logging

from aiogram.utils import executor

from app.utils.misc.set_bot_commands import set_default_commands
from loader import dp

from app.db import mysql_db
from app.handlers.users import admin, other, overlord


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    logging.basicConfig(format=u"%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
                        level=logging.INFO,
                        # level=logging.DEBUG,  # Можно заменить на другой уровень логгирования.
                        )
    mysql_db.mysql_start()


admin.register_handlers_admin(dp)
other.register_handlers_other(dp)
overlord.register_handlers_overlord(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)