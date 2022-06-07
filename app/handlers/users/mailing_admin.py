from app.db.mysql_db import active_users
from loader import dispatcher as dp, bot
from app.filters.admin import IsAdmin
from app.utils.misc.states import Mailing
from app.keyboards.admin_kb import get_mailing_keyboard, mailing_callback, button_case_cancel, get_execute_button

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

@dp.message_handler(IsAdmin(), commands=['mailing'], state="*")
async def mailing(m: types.Message, state: FSMContext):
    await state.finish()
    await m.answer("Начинаем загрузку рассылки тестов")
    await m.answer("Пришли мне текст. Если передумаешь, жми отмена", reply_markup=button_case_cancel)
    await Mailing.start_mailing.set()


@dp.message_handler(IsAdmin(), state=Mailing.start_mailing)
async def start_mailing(m: types.Message, state: FSMContext):
    text_list = []
    text_list.append(m.text)
    await state.update_data(text_list=text_list)
    await m.answer("Если это все тексты, нажми кнопку 'Подтвердить', если нет, нажми 'Загрузить'",
                   reply_markup=get_mailing_keyboard())


@dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='load'), state=Mailing.start_mailing)
@dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='confirm'), state=Mailing.start_mailing)
async def chose_mailing(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    if callback_data.get("action") == 'load':
        await c.answer()
        await c.message.answer("Пришли мне следующий текст рассылки.")
        await Mailing.process_mailing.set()
    elif callback_data.get("action") == 'confirm':
        await c.answer()
        async with state.proxy() as data:
            await c.message.answer('Проверим тексты:')
            for text in data['text_list']:
                await c.message.answer(f'А вот и ссылка на <a href="{text}">тест</a>')
            await c.message.answer('Если тексты верны, жми кнопку отправить. Или отмену',
                                   reply_markup=get_execute_button())


@dp.message_handler(IsAdmin(), state=Mailing.process_mailing)
async def process_mailing(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # text_list = data['text_list']
        # text_list.append(m.text)
        data['text_list'].append(m.text)
    await m.answer("Если это все тексты, нажми кнопку 'Подтвердить', если нет, нажми 'Загрузить'",
                       reply_markup=get_mailing_keyboard())
    await Mailing.start_mailing.set()

@dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='execute'), state="*")
async def execute_mailing(c: types.CallbackQuery, state: FSMContext):
    user_list = await active_users()
    async with state.proxy() as data:
        text_list = data['text_list']
    text_list = text_list * (len(user_list) // len(text_list)) + text_list[:(len(user_list) % len(text_list))]
    print(text_list)
    print(user_list)
    for id, active in user_list:
        if active == 1:
            await bot.send_message()


def register_mailing_handlers(dp: Dispatcher):
    dp.register_message_handler(mailing, IsAdmin(), commands=['mailing'])
    dp.register_message_handler(start_mailing, IsAdmin(), state=Mailing.start_mailing)
    dp.register_callback_query_handler(chose_mailing, IsAdmin(), mailing_callback.filter(action='load'), state=Mailing.start_mailing)
    dp.register_callback_query_handler(chose_mailing, IsAdmin(), mailing_callback.filter(action='confirm'), state=Mailing.start_mailing)
    dp.register_message_handler(process_mailing, IsAdmin(), state=Mailing.process_mailing)
    dp.register_callback_query_handler(execute_mailing, IsAdmin(), mailing_callback.filter(action='execute'), state="*")