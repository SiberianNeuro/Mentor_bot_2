from .admin import IsAdminFilter
from aiogram import Dispatcher
from loguru import logger

def setup(dp: Dispatcher):
    logger.info("Configure filters...")
    dp.filters_factory.bind(IsAdminFilter)
