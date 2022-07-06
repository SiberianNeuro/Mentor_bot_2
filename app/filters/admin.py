from dataclasses import dataclass

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data

from app.db.mysql_db import admin_check


@dataclass
class IsAdminFilter(BoundFilter):
    key = "is_admin"
    is_admin: bool

    async def check(self, obj) -> bool:
        data = ctx_data.get()
        is_admin = data['user']
        return is_admin
