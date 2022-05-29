from aiogram import types, Dispatcher
from loader import dp, bot


overlords = [323123946]


@dp.message_handler(lambda message: message.text == '4 8 15 16 23 42')
async def say_hello_to_overlord(message: types.Message):
    if message.from_user.id in overlords:
        await bot.send_message(message.from_user.id, 'К твоим услугам, шеф.')


# @dp.message_handler(content_types=['animation'])
async def gif_id(message: types.Message):
    if message.from_user.id in overlords:
        await message.reply(message.animation.file_id)
    else:
        pass


# @dp.message_handler(content_types=['sticker'])
async def sticker_id(message: types.Message):
    if message.from_user.id in overlords:
        await message.reply(message.sticker.file_id)
    else:
        pass


def register_handlers_overlord(dp: Dispatcher):
    dp.register_message_handler(gif_id, content_types=['animation'])
    dp.register_message_handler(sticker_id, content_types=['sticker'])
