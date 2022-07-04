import asyncio

from app.db.mysql_db import active_users, get_current_roles
from loader import bot, dispatcher as dp
from app.filters.admin import IsAdmin
from app.utils.states import Mailing
from app.keyboards.admin_kb import get_mailing_keyboard, mailing_callback, get_execute_button, \
    get_roles_keyboard, text_switch_button

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

"""Стартовая команда и загрузка ролей"""


# Стартовый хэндлер, вход в состояние загрузки ролей
@dp.message_handler(IsAdmin(), commands=['mailing'])
async def mailing(m: types.Message, state: FSMContext):
    await state.finish()
    await m.answer("📣 <b>Начинаем подготовку к рассылке тестов</b>\n\nДля начала выбери должности, которым будем рассылать тесты."
                   "Если передумаешь, напиши <b>'отмена'</b> или <b>/start</b>", reply_markup=await get_roles_keyboard())
    await Mailing.workers.set()


# Загрузка первой роли, потом предложение выбрать дополнительную роль или подтвердить текущие
@dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='worker'), state=Mailing.workers)
async def get_workers(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    roles = []
    roles.append(callback_data.get('c_data'))
    await state.update_data(roles=roles)
    await c.answer()
    await c.message.answer('Хорошо, должность принял, сотрудников нашел. Добавим еще одну, или переходим к ссылкам на тест?',
                           reply_markup=await get_mailing_keyboard())
    await c.message.delete()


# Переходный хэндлер: если была нажата кнопка "подтвердить", то начинается проверка ролей,
# если кнопка "загрузить", то предлагается выбрать еще одну роль
@dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='load'), state=Mailing.workers)
@dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='confirm'), state=Mailing.workers)
async def chose_workers(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    if callback_data.get("action") == 'load':
        await c.answer()
        await c.message.answer('Хорошо, выбери еще одну должность 🔰',
                               reply_markup=await get_roles_keyboard())
        await Mailing.process_workers.set()
        await c.message.delete()
    elif callback_data.get("action") == 'confirm':
        await c.answer()
        async with state.proxy() as data:
            data['roles'] = tuple(map(int, data['roles']))
            print(data['roles'])
            roles = await get_current_roles(data['roles'])
        await c.message.answer('Давай проверим роли:')
        for role in roles:
            await c.message.answer(f'{role[0]}')
        await c.message.answer('Если все верно, нажимай подтвердить, если нет, то снова напиши <b>/mailing</b>',
                               reply_markup=await text_switch_button())
        await c.message.delete()


# Загрузка второй и последующих ролей, смена FSM состояния
@dp.callback_query_handler(mailing_callback.filter(action='worker'), state=Mailing.process_workers)
async def more_workers(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await c.answer()
    async with state.proxy() as data:
        data['roles'].append(callback_data.get('c_data'))
    await c.message.answer('Хорошо, должность принял, сотрудников нашел. Добавим еще одну, или переходим к ссылкам на тест?',
                           reply_markup=await get_mailing_keyboard())
    await Mailing.workers.set()
    await c.message.delete()

"""Переход в состояние загрузки ссылок на тест"""


# После подтверждения проверки ролей высылаем запрос на ССЫЛКУ на тест
@dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='execute'), state=Mailing.workers)
async def start_text(c: types.CallbackQuery):
    await c.answer()
    await c.message.answer('Хорошо, пришли мне ссылку на тест 🔗')
    await Mailing.start_mailing.set()


# Прием первой ссылки на тест текстовым сообщением, развилка на подтверждение или повторную загрузку
@dp.message_handler(IsAdmin(), state=Mailing.start_mailing)
async def start_mailing(m: types.Message, state: FSMContext):
    text_list = []
    text_list.append(m.text)
    await state.update_data(text_list=text_list)
    await m.answer("Супер, ссылку вижу. Добавляем еще, или переходим к рассылке?",
                   reply_markup=await get_mailing_keyboard())


# Переходный хэндлер: если была нажата кнопка "подтвердить", то начинается проверка ссылок,
# если кнопка "загрузить", то предлагается добавить еще один текст
@dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='load'), state=Mailing.start_mailing)
@dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='confirm'), state=Mailing.start_mailing)
async def chose_mailing(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    if callback_data.get("action") == 'load':
        await c.answer()
        await c.message.answer("Хорошо, пришли мне ссылку на тест 🔗")
        await Mailing.process_mailing.set()
        await c.message.delete()
    elif callback_data.get("action") == 'confirm':
        await c.answer()
        async with state.proxy() as data:
            await c.message.answer('Давай проверим, что получилось:')
            for text in data['text_list']:
                await c.message.answer(f'А вот и ссылка на <a href="{text}">тест</a>', disable_web_page_preview=False)
            await c.message.answer('Если тексты верны, жми кнопку отправить. Если передумал, напиши <b>/mailing</b>,'
                                   'Или напиши <b>отмена</b>',
                                   reply_markup=await get_execute_button())
        await c.message.delete()


# Загрузка второго и последующих текстов
@dp.message_handler(state=Mailing.process_mailing)
async def process_mailing(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text_list'].append(m.text)
    await m.answer("Супер, ссылку вижу. Добавляем еще, или переходим к рассылке?",
                       reply_markup=await get_mailing_keyboard())
    await Mailing.start_mailing.set()


# После подтверждения текстов и ролей забираем из БД все ID с соответствующими ролями, затем умножаем массив с
# ссылками до длинны списка пользователей и рассылаем по порядку
@dp.callback_query_handler(mailing_callback.filter(action='execute'), state="*")
async def execute_mailing(c: types.CallbackQuery, state: FSMContext):
    await c.message.answer('Пристегните ремни, начинаем рассылку 😎')
    async with state.proxy() as data:
        text_list = data['text_list']
        user_list = await active_users(data['roles'])
    counter = 0
    text_list = text_list * (len(user_list) // len(text_list)) + text_list[:(len(user_list) % len(text_list))]
    for i in range(len(user_list)):
        await bot.send_message(user_list[i][0], text=f'Твоя ссылка - <a href="{text_list[i]}">держи</a>')
        counter += 1
        await asyncio.sleep(0.2)
    await c.message.answer(f'Рассылка завершена, всего отправлено: {counter}')
    await state.finish()


def register_mailing_handlers(dp: Dispatcher):
    dp.register_message_handler(mailing, IsAdmin(), commands=['mailing'])
    dp.register_callback_query_handler(get_workers, IsAdmin(), mailing_callback.filter(action='worker'), state=Mailing.workers)
    dp.register_callback_query_handler(chose_workers, IsAdmin(), mailing_callback.filter(action='load'), state=Mailing.workers)
    dp.register_callback_query_handler(chose_workers, IsAdmin(), mailing_callback.filter(action='confirm'), state=Mailing.workers)
    dp.register_callback_query_handler(more_workers, IsAdmin(), mailing_callback.filter(action='worker'), state=Mailing.process_workers)
    dp.register_callback_query_handler(start_text, IsAdmin(), mailing_callback.filter(action='execute'), state=Mailing.workers)
    dp.register_message_handler(start_mailing, IsAdmin(), state=Mailing.start_mailing)
    dp.register_callback_query_handler(chose_mailing, IsAdmin(), mailing_callback.filter(action='load'), state=Mailing.start_mailing)
    dp.register_callback_query_handler(chose_mailing, IsAdmin(), mailing_callback.filter(action='confirm'), state=Mailing.start_mailing)
    dp.register_message_handler(process_mailing, IsAdmin(), state=Mailing.process_mailing)
    dp.register_callback_query_handler(execute_mailing, IsAdmin(), mailing_callback.filter(action='execute'), state="*")