from typing import Optional

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from app.db.mysql_db import admin_check


class ACLMiddleware(BaseMiddleware):
    async def setup_chat(self, data: dict, user: types.User, chat: Optional[types.Chat] = None):
        user_id = user.id
        chat_id = chat.id if chat else user.id
        chat_type = chat.type if chat else "private"

        user = False if await admin_check(user_id) is None else True

        data["user"] = user
        # data["chat"] = chat

    async def on_pre_process_message(self, message: types.Message, data: dict):
        await self.setup_chat(data, message.from_user, message.chat)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        await self.setup_chat(data, query.from_user, query.message.chat if query.message else None)