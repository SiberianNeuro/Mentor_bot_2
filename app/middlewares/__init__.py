from aiogram import Dispatcher
# from aiogram.dispatcher.middlewares.manager import M
from loguru import logger

# from app.middlewares.acl import ACLMiddleware


def setup(dp: Dispatcher):
    logger.info("Configure middlewares...")

    # dp.middleware.setup(LoggingMiddleware("bot"))
    # dp.middleware.setup(ACLMiddleware())
