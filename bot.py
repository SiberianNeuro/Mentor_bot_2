import asyncio
from loguru import logger

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.services.config import load_config
from app.models.user import Base
from app.models.redis import BaseRedis
from app.middlewares.acl import Middleware


async def on_startup():
    from app.utils import logging

    logging.setup()

    config = load_config('.env')

    engine = create_async_engine(
        f'mysql+aiomysql://{config.db.db_user}:{config.db.db_pass}@{config.db.db_host}/{config.db.db_name}',
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.reflect)

    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    redis = BaseRedis
    storage = RedisStorage(redis=redis) if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage)
    await bot.set_my_commands(
        [
            types.BotCommand(command='start', description='Запустить'),
        ]
    )

    logger.info('Configure middlewares...')
    dp.update.outer_middleware(Middleware(config=config, db_session=async_sessionmaker))

    from app.handlers.users import mentors, mailing_admin, other
    from app.handlers.groups import channel_commands, trainee_channels

    dp.include_router(mentors.router)
    dp.include_router(trainee_channels.router)
    dp.include_router(other.router)
    # from app.services.scheduler import scheduler
    logger.info("Configure scheduler tasks...")
    # asyncio.create_task(scheduler())

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(on_startup())
