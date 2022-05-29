from aiogram import types

from aiogram.dispatcher.filters import BoundFilter

from app.services.config import load_config


class IsAdmin(BoundFilter):
    async def check(self, obj):
        config = load_config(".env")
        if obj.from_user.id not in config.tg_bot.admin_ids:
            return False
        else:
            return True