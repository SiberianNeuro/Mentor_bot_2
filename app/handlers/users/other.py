from datetime import datetime, date

from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher

from app.db.mysql_db import admins_ids
from app.filters.other import is_register
from app.utils.misc.sheets_append import add_user_array
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
                       reply_markup=await other_kb.get_register_button())


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
                               reply_markup=await other_kb.get_cancel_button())
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
async def get_fullname(m: types.Message, state: FSMContext):
    first_name = m.text.split()[1]
    await state.update_data(name=m.text.title())
    await FSMRegister.city.set()
    await m.answer(f'Приятно познакомиться, {first_name}!\n\nТеперь напиши город, в котором ты работаешь 🏙\n'
                   f'<i>Например: Новосибирск, Санкт-Петербург, Екатеринбург</i>')


@dp.message_handler(state=FSMRegister.city)
async def get_city(m: types.Message, state: FSMContext):
    city = m.text.title()
    await state.update_data(city=city)
    await FSMRegister.role.set()
    await m.answer(f'Замечательно 🤟\n\nТеперь выбери свою должность. Только честно 🗿',
                   reply_markup=await other_kb.get_pos_keyboard())


@dp.callback_query_handler(other_kb.register_callback.filter(stage='position'), state=FSMRegister.role)
async def get_role(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    role = int(callback_data.get('stage_data'))
    await state.update_data(role=role)
    if role in (5, 6, 7, 8):
        await FSMRegister.traineeship.set()
        await call.message.answer('Отлично, с этим определились. Тогда расскажи немного про ординатуру:\n'
                               'Выбери один из нескольких вариантов ответа:', reply_markup=await other_kb.get_spec_keyboard())
    if role in (9, 10, 11):
        await FSMRegister.med_education.set()
        await call.message.answer('Отлично, с этим определились. Скажи, пожалуйста, есть ли у тебя медицинское образование?',
                                  reply_markup=await other_kb.get_education_keyboard())


@dp.callback_query_handler(other_kb.register_callback.filter(stage='education'), state=FSMRegister.med_education)
async def get_education(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.update_data(
        traineeship=callback_data.get("stage_data"),
        profession=None,
        start_year=None,
        end_year=None
    )
    await FSMRegister.phone.set()
    await c.answer('Записал 👌\n\nТеперь пробежимся по формальностям:\nВведи своей номер телефона 📱')

@dp.callback_query_handler(other_kb.register_callback.filter(stage='spec'), state=FSMRegister.traineeship)
async def get_traineeship(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    if int(callback_data.get('stage_data')) in (2, 3, 4):
        await c.answer()
        await state.update_data(traineeship=int(callback_data.get('stage_data')))
        await FSMRegister.profession.set()
        await c.message.answer('Хорошо, а специальность известна?\n<i>Например, ЛОР или неврология</i>')
    elif int(callback_data.get('stage_data')) == 1:
        await c.answer()
        await state.update_data(
            traineeship=int(callback_data.get('stage_data')),
            profession=None,
            start_year=None,
            end_year=None,
        )
        await c.message.answer('Записал 👌\n\nТеперь пробежимся по формальностям:\nВведи своей номер телефона 📱')
        await FSMRegister.phone.set()


@dp.message_handler(state=FSMRegister.profession)
async def get_profession(m: types.Message, state: FSMContext):
    await state.update_data(profession=m.text)
    await FSMRegister.start_year.set()
    await m.answer('Отличный выбор 😎\n\nНапиши, пожалуйста, год поступления')


@dp.message_handler(state=FSMRegister.start_year)
async def get_start_year(m: types.Message, state: FSMContext):
    await state.update_data(start_year=m.text)
    await FSMRegister.end_year.set()
    await m.answer('Супер, теперь год окончания')


@dp.message_handler(state=FSMRegister.end_year)
async def get_end_year(m: types.Message, state: FSMContext):
    await state.update_data(end_year=m.text)
    await m.answer('Записал 👌\n\nТеперь пробежимся по формальностям:\nВведи своей номер телефона 📱')
    await FSMRegister.phone.set()


@dp.message_handler(state=FSMRegister.phone)
async def get_phone_number(m: types.Message, state: FSMContext):
    await state.update_data(phone=m.text)
    await FSMRegister.email.set()
    await m.answer('Принял, теперь напиши свою гугл-почту 📧\n(заканчивается на @gmail.com)')


@dp.message_handler(state=FSMRegister.email)
async def get_email(m: types.Message, state: FSMContext):
    await state.update_data(email=m.text)
    await FSMRegister.birthdate.set()
    await m.answer('Огонь, осталось только написать дату рождения в формате <i>ДД.ММ.ГГГГ</i>')


@dp.message_handler(state=FSMRegister.birthdate)
async def finish_register(m: types.Message, state: FSMContext):
    try:
        birthdate = datetime.strptime(m.text, "%d.%m.%Y")
        assert birthdate < date(1970, 1, 1), await m.answer("Пошутили и хватит 🙄\nВведи настоящую дату")
        await state.update_data(bdate=birthdate, username='@' + m.from_user.username, chat_id=m.from_user.id)
        user = await state.get_data()
        await mysql_db.add_user(tuple(user.values()))
        await m.answer('Регистрация завершена, добро пожаловать :)', reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    except ValueError:
        await m.answer("Это некорректная дата. Пожалуйста, введи дату по шаблону.")



def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(commands_start, CommandStart())
    dp.register_message_handler(start_register, other_kb.start_register.filter(status='yes'), state=None)
    dp.register_message_handler(cancel_handler, state='*', commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(get_fullname, state=FSMRegister.name)
    dp.register_message_handler(get_city, state=FSMRegister.city)
    dp.register_callback_query_handler(get_role, other_kb.register_callback.filter(stage='position'), state=FSMRegister.role)
    dp.register_message_handler(get_education, state=FSMRegister.med_education)
    dp.register_callback_query_handler(get_traineeship, other_kb.register_callback.filter(stage='spec'),
                                       state=FSMRegister.traineeship)
    dp.register_message_handler(get_profession, state=FSMRegister.profession)
    dp.register_message_handler(get_start_year, state=FSMRegister.start_year)
    dp.register_message_handler(get_end_year, state=FSMRegister.end_year)
    dp.register_message_handler(get_phone_number, state=FSMRegister.phone)
    dp.register_message_handler(get_email, state=FSMRegister.email)
    dp.register_message_handler(finish_register, state=FSMRegister.birthdate)



