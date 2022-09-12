import asyncio

from aiogram.utils import executor
from loguru import logger

from loader import dispatcher as dp

from app.utils.set_bot_commands import set_default_commands


async def on_startup(dp):
    from app.services.scheduler import scheduler
    logger.info("Configure scheduler tasks...")
    asyncio.create_task(scheduler())

    logger.info("Configure default commands...")
    await set_default_commands(dp)

    from app import filters, middlewares
    middlewares.setup(dp)
    filters.setup(dp)

    from app.handlers.users import admin, mailing_admin, other, duty_line_doc
    from app.handlers.errors import error_handler
    from app.handlers.channels import trainee_channels
    logger.info("Configure handlers...")
    trainee_channels.setup(dp)
    admin.setup(dp)
    mailing_admin.setup(dp)
    other.setup(dp)
    error_handler.setup(dp)

if __name__ == '__main__':
    from app.utils import logging

    logging.setup()

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
