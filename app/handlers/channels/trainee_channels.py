from aiogram import types, Dispatcher

from loguru import logger

async def new_member(msg: types.Message):
    await msg.answer(text=f"Привяу")
    link = await msg.bot.export_chat_invite_link(chat_id=msg.chat.id)
    await msg.answer(f'{link}')
    if msg.from_user not in msg.new_chat_members:
        logger.opt(lazy=True).info(
            'User {user} added new members in chat {chat}: {new_members}',
            user=lambda: msg.from_user.username,
            chat=lambda: msg.chat.title,
            new_members=lambda: ", ".join([str(u.username) for u in msg.new_chat_members])
        )

def setup(dp: Dispatcher):
    dp.register_message_handler(new_member, content_types=types.ContentTypes.NEW_CHAT_MEMBERS)