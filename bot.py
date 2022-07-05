from aiogram.utils import executor

from app.utils.set_bot_commands import set_default_commands
from loader import dispatcher as dp

from app.handlers.users import admin, other, overlord, mailing_admin
from app.handlers.errors import error_handler



async def on_startup(dp):
    await set_default_commands(dp)

    admin.register_handlers_admin(dp)
    mailing_admin.register_mailing_handlers(dp)
    overlord.register_handlers_overlord(dp)
    other.register_handlers_other(dp)
    error_handler.register_error_handler(dp)

    from app.utils.misc import logging
    logging.setup()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
