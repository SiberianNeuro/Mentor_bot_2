import asyncio
import logging

from app.db.mysql_db import active_users, get_current_roles
from loader import bot
from app.utils.states import Mailing
from app.keyboards.admin_kb import get_mailing_keyboard, mailing_callback, get_execute_button, \
    get_roles_keyboard, text_switch_button

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import ChatNotFound
from aiogram.dispatcher.filters import Text

"""Стартовая команда и загрузка ролей"""


# Стартовый хэндлер, вход в состояние загрузки ролей
# @dp.message_handler(IsAdmin(), commands=['mailing'])
async def mailing(m: types.Message, state: FSMContext):
    await state.finish()
    await m.answer("📣 <b>Начинаем подготовку к рассылке тестов</b>\n\nДля начала выбери должности, которым будем рассылать тесты."
                   "Если передумаешь, напиши <b>'отмена'</b> или <b>/start</b>", reply_markup=await get_roles_keyboard())
    await Mailing.workers.set()


# Загрузка первой роли, потом предложение выбрать дополнительную роль или подтвердить текущие
# @dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='worker'), state=Mailing.workers)
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
# @dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='load'), state=Mailing.workers)
# @dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='confirm'), state=Mailing.workers)
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
            roles = await get_current_roles(data['roles'])
        await c.message.answer('Давай проверим роли:')
        for role in roles:
            await c.message.answer(f'{role[0]}')
        await c.message.answer('Если все верно, нажимай подтвердить, если нет, то снова напиши <b>/mailing</b>',
                               reply_markup=await text_switch_button())
        await c.message.delete()


# Загрузка второй и последующих ролей, смена FSM состояния
# @dp.callback_query_handler(mailing_callback.filter(action='worker'), state=Mailing.process_workers)
async def more_workers(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await c.answer()
    async with state.proxy() as data:
        data['roles'].append(callback_data.get('c_data'))
        logging.info(f'{data["roles"]}')
    await c.message.answer('Хорошо, должность принял, сотрудников нашел. Добавим еще одну, или переходим к ссылкам на тест?',
                           reply_markup=await get_mailing_keyboard())
    await Mailing.workers.set()
    await c.message.delete()

"""Переход в состояние загрузки ссылок на тест"""


# После подтверждения проверки ролей высылаем запрос на ССЫЛКУ на тест
# @dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='execute'), state=Mailing.workers)
async def start_text(c: types.CallbackQuery):
    await c.answer()
    await c.message.answer('Хорошо, пришли мне ссылку на тест 🔗')
    await Mailing.start_mailing.set()


# Прием первой ссылки на тест текстовым сообщением, развилка на подтверждение или повторную загрузку
# @dp.message_handler(IsAdmin(), state=Mailing.start_mailing)
async def start_mailing(m: types.Message, state: FSMContext):
    text_list = []
    text_list.append(m.text)
    await state.update_data(text_list=text_list)
    await m.answer("Супер, ссылку вижу. Добавляем еще, или переходим к рассылке?",
                   reply_markup=await get_mailing_keyboard())
    await Mailing.confirm_mailing.set()


# Переходный хэндлер: если была нажата кнопка "подтвердить", то начинается проверка ссылок,
# если кнопка "загрузить", то предлагается добавить еще один текст
# @dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='load'), state=Mailing.confirm_mailing)
# @dp.callback_query_handler(IsAdmin(), mailing_callback.filter(action='confirm'), state=Mailing.confirm_mailing)
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
                await c.message.answer(text=f'Привет! Приготовил тебе <a href="{text}">ссылку</a> '
                                                              f'на тест ⚡\n\n'
                                                              f'⏰ Длительность тестирования 30 минут, после чего форма '
                                                              f'для отправки ответов будет закрыта\n\n'
                                                              f'Не забудь свой гугл-аккаунт 📲\n\n'
                                                              f'Удачи 🍀')
            await c.message.answer('Если тексты верны, жми кнопку отправить. Если передумал, напиши <b>/mailing</b>,'
                                   'Или напиши <b>отмена</b>',
                                   reply_markup=await get_execute_button())
        await c.message.delete()


# Загрузка второго и последующих текстов
# @dp.message_handler(state=Mailing.process_mailing)
async def process_mailing(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text_list'].append(m.text)
        logging.info(f'{data["text_list"]}')
    await m.answer("Супер, ссылку вижу. Добавляем еще, или переходим к рассылке?",
                       reply_markup=await get_mailing_keyboard())
    await Mailing.confirm_mailing.set()


# После подтверждения текстов и ролей забираем из БД все ID с соответствующими ролями, затем умножаем массив с
# ссылками до длинны списка пользователей и рассылаем по порядку
# @dp.callback_query_handler(mailing_callback.filter(action='execute'), state=Mailing.confirm_mailing)
async def execute_mailing(c: types.CallbackQuery, state: FSMContext):
    await c.answer()
    await c.message.answer('Пристегните ремни, начинаем рассылку 😎')
    async with state.proxy() as data:
        text_list = data['text_list']
        user_list = await active_users(data['roles'])
    counter = 0
    text_list = text_list * (len(user_list) // len(text_list)) + text_list[:(len(user_list) % len(text_list))]
    logging.info(f'{text_list}')
    logging.info(f'{user_list}')
    for i in range(len(user_list)):
        try:
            await bot.send_message(chat_id=user_list[i][0], text=f'Привет! Приготовил тебе <a href="{text_list[i]}">ссылку</a>'
                                                              f'на тест ⚡\n\n'
                                                              f'⏰ Длительность тестирования 30 минут, после чего форма '
                                                              f'для отправки ответов будет закрыта\n\n'
                                                              f'Не забудь свой гугл-аккаунт 📲\n\n'
                                                              f'Удачи 🍀')
            counter += 1
        except ChatNotFound as e:
            logging.exception(f"{user_list[i][1]}: {e}")
            await c.message.answer(f"{user_list[i][1]}: тест не получен. Пользователь отключил меня, либо не регистрировался.")
        await asyncio.sleep(0.2)
    await c.message.answer(f'Рассылка завершена, всего отправлено: {counter}')
    await state.finish()


def setup(dp: Dispatcher):
    dp.register_message_handler(mailing, Text(equals='Рассылка 🔊'), state="*", is_admin=True)
    dp.register_callback_query_handler(get_workers, mailing_callback.filter(action='worker'), state=Mailing.workers, is_admin=True)
    dp.register_callback_query_handler(chose_workers, mailing_callback.filter(action='load'), state=Mailing.workers, is_admin=True)
    dp.register_callback_query_handler(chose_workers, mailing_callback.filter(action='confirm'), state=Mailing.workers, is_admin=True)
    dp.register_callback_query_handler(more_workers, mailing_callback.filter(action='worker'), state=Mailing.process_workers, is_admin=True)
    dp.register_callback_query_handler(start_text, mailing_callback.filter(action='execute'), state=Mailing.workers, is_admin=True)
    dp.register_message_handler(start_mailing, state=Mailing.start_mailing)
    dp.register_callback_query_handler(chose_mailing, mailing_callback.filter(action='load'), state=Mailing.confirm_mailing, is_admin=True)
    dp.register_callback_query_handler(chose_mailing, mailing_callback.filter(action='confirm'), state=Mailing.confirm_mailing, is_admin=True)
    dp.register_message_handler(process_mailing, state=Mailing.process_mailing, is_admin=True)
    dp.register_callback_query_handler(execute_mailing, mailing_callback.filter(action='execute'), state=Mailing.confirm_mailing, is_admin=True)