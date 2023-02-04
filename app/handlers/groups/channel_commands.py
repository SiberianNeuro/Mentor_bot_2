from aiogram import types, Router

from app.utils.misc.wrappers import Wrappers

router = Router()


@router.message(commands=['user'], commands_prefix='!')
async def emp_search(msg: types.Message):
    user = ' '.join(msg.text.split(' ')[1:]).title()
    users = await get_user_info(user)
    if not users:
        await msg.answer('Информации об этом сотруднике нет 🤔')
    else:
        for user in users:
            user_info = await Wrappers.user_wrapper(user)
            await msg.reply(text=user_info['wrapper'])


