from aiogram import types

from aiogram.dispatcher.filters import BoundFilter

from app.db.mysql_db import chat_id_check


async def is_register(obj):
    result = await chat_id_check()
    counter = 0
    for i in result:
        if obj in i and i[1] == 1:
            counter += 1
    if counter > 0:
        return True
    else:
        return False