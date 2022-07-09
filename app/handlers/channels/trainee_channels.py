from aiogram import types, Dispatcher

from loguru import logger

from app.db.mysql_db import get_chat_members


async def new_member(msg: types.Message):
    if msg.from_user not in msg.new_chat_members:
        logger.opt(lazy=True).info(
            'User {user} added new members in chat {chat}: {new_members}',
            user=lambda: msg.from_user.username,
            chat=lambda: msg.chat.title,
            new_members=lambda: ", ".join([str(u.username) for u in msg.new_chat_members])
        )
    else:
        logger.opt(lazy=True).info(
            "New chat members in chat {chat}: {new_members}",
            chat=lambda: msg.chat.title,
            new_members=lambda: ", ".join([str(u.username) for u in msg.new_chat_members]),
        )

    users = []
    user_string = ""
    for new_member in msg.new_chat_members:
        chat_member = await msg.chat.get_member(new_member.id)
        users.append(chat_member['user']['id'])

    users_info = await get_chat_members(users)

    if users_info == ():
        return

    else:
        for user in users_info:
            user_string += f"<b>{user['fullname']}</b>, 🏙 город {user['city']}\n"

    await msg.answer(f'К нам пришли новые сотрудники!👨‍⚕\n\n'
                     f'{user_string}\n'
                     f'Прошу любить и жаловать 😎')


def setup(dp: Dispatcher):
    dp.register_message_handler(new_member, content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
