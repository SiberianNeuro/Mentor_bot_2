from aiogram import types

from aiogram.dispatcher.filters import BoundFilter

from app.db.mysql_db import chat_id_check


async def is_register(obj):
    result = await chat_id_check()
    check_list = []
    for i in result:
        check_list.append(int(i[0]))
    print(check_list)
    if obj in check_list:
        return True
    else:
        return False