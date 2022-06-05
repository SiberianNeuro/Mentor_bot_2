from aiogram import types

from aiogram.dispatcher.filters import BoundFilter

from app.db.mysql_db import admins_ids


class IsAdmin(BoundFilter):
    async def check(self, obj):
        ids = await admins_ids()
        for i in ids:
            if obj.from_user.id in i:
                return True
            else:
                return False
