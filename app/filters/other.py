from aiogram import types
from app.db.mysql_db import chat_id_check


async def is_register(obj):
    result = await chat_id_check()
    if obj in result:
        return True
    else:
        return False
