from app.db.mysql_db import chat_id_check, admins_ids


async def is_register(obj):
    result = await chat_id_check()
    admins = await admins_ids()
    if obj is admins:
        return True
    elif obj in result:
        return True
    else:
        return False