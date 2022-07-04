from app.db.mysql_db import chat_id_check, admins_ids

from loguru import logger

async def is_register(obj):
    result = await chat_id_check()
    admins = await admins_ids()
    if obj in admins:
        logger.info(f"{obj} succesfully started bot")
        return True
    elif obj in result:
        logger.info(f"{obj} succesfully started bot")
        return True
    else:
        logger.info(f"{obj} started bot first time")
        return False