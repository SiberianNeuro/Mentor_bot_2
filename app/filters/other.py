from app.db.mysql_db import chat_id_check, admins_ids

from loguru import logger

async def is_register(obj):
    result = await chat_id_check()
    admins = await admins_ids()
    if obj in admins:
        return True
    elif obj in result:
        return True
    else:
        return False