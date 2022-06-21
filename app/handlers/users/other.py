from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher

from app.filters.other import is_register
from loader import dispatcher as dp, bot
from aiogram.dispatcher.filters import Text, CommandStart
from app.keyboards import other_kb
from app.utils.misc.states import FSMRegister
from app.db import mysql_db


@dp.message_handler(CommandStart(), state="*")
async def commands_start(m: types.Message, state: FSMContext):
    await state.finish()
    await m.delete()
    await m.answer_sticker('CAACAgIAAxkBAAIE4GKSGruXCE8S-gM_iIJyaTbM9TGYAAJPAAOtZbwUa5EcjYesr5MkBA')
    await m.answer('Привет ✌\n\nЯ помощник в медицинском отделе ДОК 🤖\n'
                                                     'Чтобы узнать список команд, введи <b>/help</b>')
    if await is_register(m.from_user.id):
        await m.answer('Вижу, что ты уже зарегистрирован 🤠\n\nЧем могу помочь?', reply_markup=types.ReplyKeyboardRemove())
    else:
        await m.answer('Вижу, что ты еще не проходил регистрацию 😱\n\n⬇️Скорее жми кнопку и начнём знакомиться⬇️',
                       reply_markup=other_kb.get_register_button())


@dp.callback_query_handler(other_kb.start_register.filter(status='yes'), state=None)
async def start_register(c: types.CallbackQuery):
    if await is_register(c.from_user.id):
        await c.answer()
        await c.message.answer('Ты уже регистрировался 👺')
        await c.message.delete()
    else:
        await c.answer()
        await FSMRegister.name.set()
        await c.message.answer('Давай знакомиться✌️\n\n'
                               'Если вдруг передумаешь регистрироваться, либо что-то напишешь не так,'
                               ' жми кнопку <b>"Отмена"</b>,'
                               'или снова напиши /start',
                               reply_markup=other_kb.get_cancel_button())
        await c.message.answer('Для начала напиши своё ФИО полностью кириллицей\n\n'
                               '<b><i>Например: Погребной Данила Олегович</i></b>')
        await c.message.delete()


@dp.message_handler(state='*', commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(m: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await m.reply('Принято 👌', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=FSMRegister.name)
async def get_city(m: types.Message, state: FSMContext):
    first_name = m.text.split()[1]
    async with state.proxy() as data:
        data['name'] = m.text.title()
    await FSMRegister.city.set()
    await m.answer(f'Приятно познакомиться, {first_name}!\n\nТеперь напиши, пожалуйста, город, в котором ты работаешь 🏙\n'
                   f'<i>Например: Новосибирск, Санкт-Петербург, Екатеринбург</i>')


@dp.message_handler(state=FSMRegister.city)
async def get_fullname(m: types.Message, state: FSMContext):
    city = m.text.title()
    async with state.proxy() as data:
        data['city'] = city
    await FSMRegister.next()
    await m.answer(f'Замечательно 🤟\n\nТеперь выбери, пожалуйста, свою должность. Только честно 🗿',
                           reply_markup= await other_kb.get_pos_keyboard())


@dp.register_callback_query_handler(state=FSMRegister.role)
async def get_role(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await c.answer()
    role = callback_data.get('data')
    async with state.proxy() as data:
        data['role'] = role
    if role in (5, 6, 7, 8):
        await FSMRegister.traineeship.set()
        await c.message.answer('Хорошечно, определились. Тогда расскажи немного про ординатуру:\n'
                               'Выбери один из нескольких вариантов ответа:', reply_markup=other_kb.get_spec_keyboard())
    if role in (9, 10, 11):
        await FSMRegister.med_education.set()
        await c.message.answer('Хорошечно, определились. Скажи, пожалуйста есть ли у тебя медицинское образование?\n'
                               'Можно просто "да" или "нет"')


@dp.callback_query_handler(lambda x: x.data and x.data.startswith(1) or x.data.startswith(2) or x.data.startswith(3),
                           state=FSMRegister.traineeship)
async def get_traineeship(c: types.CallbackQuery, state: FSMContext):
    await c.answer()
    async with state.proxy() as data:
        data['traineeship'] = c.data
    await FSMRegister.profession.set()
    await c.message.answer('Хорошо, а специальность?')

@dp.message_handler(state=FSMRegister.profession)
async def get_profession(m: types.Message, state: FSMContext):
    pass


@dp.callback_query_handler(other_kb.register_callback.filter(stage='position'), state=FSMRegister.position)
async def enter_position(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await c.answer()
    async with state.proxy() as data:
        data['pos'] = callback_data.get("data")
        data['username'] = '@' + c.from_user.username
        data['chat_id'] = c.from_user.id
    await c.message.answer('Регистрация завершена, добро пожаловать :)', reply_markup=types.ReplyKeyboardRemove())
    await mysql_db.add_user(state)
    await state.finish()


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(commands_start, CommandStart())
    dp.register_message_handler(start_register, other_kb.start_register.filter(status='yes'), state=None)
    dp.register_message_handler(cancel_handler, state='*', commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(get_fullname, state=FSMRegister.name)
    dp.register_callback_query_handler(enter_position, other_kb.register_callback.filter(status='position'), state=FSMRegister.position)


