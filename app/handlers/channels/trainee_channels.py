from aiogram import types, Dispatcher

from loguru import logger


def setup(dp: Dispatcher):
    dp.register_message_handler()