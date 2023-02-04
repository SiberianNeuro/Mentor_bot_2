from aiogram import Router, Bot, types
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from magic_filter import F

from loguru import logger

from app.models.user import User

router = Router()
router.chat_member.filter(F.chat.type.in_({'group', 'supergroup'}))


@router.message(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def on_user_join(msg: types.Message, db):
    if msg.from_user not in msg.new_chat_members:
        logger.opt(lazy=True).info(
            'User {user} added new members in chat {chat}: {new_members}',
            user=lambda: msg.from_user.username,
            chat=lambda: msg.chat.title,
            new_members=lambda: ', '.join(
                new_member.username for new_member in msg.new_chat_members
            ))
    else:
        logger.opt(lazy=True).info(
            "New chat members in chat {chat}: {new_members}",
            chat=lambda: msg.chat.title,
            new_members=lambda: ', '.join(
                new_member.username for new_member in msg.new_chat_members
            ))
    if len(msg.new_chat_members) > 1:
        welcome_string = f'Поприветствуем новоприбывших!\n'
        async with db.begin() as db_session:
            for user in msg.new_chat_members:
                user: User = await db_session.get(User, user.id)

                if user:
                    welcome_string += f'<b>{user.fullname}</b>, город {user.city}\n'

        welcome_string += f'\nПрошу любить и жаловать 😎'

    else:
        async with db.begin() as db_session:
            user: User = await db_session.get(User, msg.new_chat_members[0].id)
            if user:
                await msg.answer(f'К нам присоединяется <b>{user.fullname}</b> из города {user.city}\n'
                                 f'Прошу любить и жаловать 😎')
