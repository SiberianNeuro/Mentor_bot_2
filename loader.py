import pymysql
from aiogram import Bot
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from app.services.config import load_config

config = load_config(".env")

storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
conn = pymysql.connect(
            host=config.db.host,
            user=config.db.user,
            password=config.db.password,
            database=config.db.database,
            cursorclass=pymysql.cursors.Cursor,
            charset="utf8mb4",
        )
if conn:
    print('Database connected.')