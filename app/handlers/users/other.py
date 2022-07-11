from datetime import datetime
from loguru import logger
import random


from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text, CommandStart


from app.keyboards.other_kb import *
from app.keyboards.admin_kb import get_mentors_keyboard
from app.utils.misc.wrappers import user_wrapper

from app.utils.states import FSMRegister

from app.db.mysql_db import is_register, user_db_roundtrip, get_admin

from app.models.simple_answers import answers


# @dp.message_handler(CommandStart(), state="*")
async def commands_start(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.delete()
    await msg.answer_sticker('CAACAgIAAxkBAAIE4GKSGruXCE8S-gM_iIJyaTbM9TGYAAJPAAOtZbwUa5EcjYesr5MkBA')
    await msg.answer('Привет ✌\n\nЯ помощник в медицинском отделе ДОК 🤖')
    if await is_register(msg.from_user.id):
        await msg.answer('Вижу, что ты уже зарегистрирован 🤠\n\nЧем могу помочь?', reply_markup=types.ReplyKeyboardRemove())
    else:
        await msg.answer('Вижу, что ты еще не проходил регистрацию 😱\n\n⬇️Скорее жми кнопку и начнём знакомиться⬇️',
                         reply_markup=await get_register_button())


# @dp.callback_query_handler(other_kb.start_register.filter(status='yes'), state=None)
async def start_register(call: types.CallbackQuery):
    if await is_register(call.from_user.id):
        await call.answer()
        await call.message.answer('Ты уже регистрировался 👺')
        await call.message.delete()
        logger.debug(f"{call.from_user.username} - попытка повторной регистрации")
    else:
        await call.answer()
        await FSMRegister.name.set()
        await call.message.answer('Давай знакомиться✌️\n\n'
                               'Если вдруг передумаешь регистрироваться, либо что-то напишешь не так,'
                               ' жми кнопку <b>"Отмена"</b>,'
                               'или снова напиши /start',
                                  reply_markup=await get_cancel_button())
        await call.message.answer('Для начала напиши своё ФИО полностью кириллицей\n\n'
                               '<b><i>Например: Погребной Данила Олегович</i></b>')
        await call.message.delete()
        logger.log('REGISTRATION', f'@{call.from_user.username} started registration process...')


# @dp.message_handler(state='*', commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await msg.reply('Принято 👌', reply_markup=types.ReplyKeyboardRemove())


# @dp.message_handler(state=FSMRegister.name)
async def get_fullname(msg: types.Message, state: FSMContext):
    first_name = msg.text.split()[1]
    await state.update_data(name=msg.text.title())
    await FSMRegister.city.set()
    await msg.answer(f'Приятно познакомиться, {first_name}!\n\nТеперь напиши город, в котором ты работаешь 🏙\n'
                   f'<i>Например: Новосибирск, Санкт-Петербург, Екатеринбург</i>')


# @dp.message_handler(state=FSMRegister.city)
async def get_city(msg: types.Message, state: FSMContext):
    city = msg.text.title()
    await state.update_data(city=city)
    await FSMRegister.role.set()
    await msg.answer('Замечательно 🤟\nТеперь выбери свою должность:\n\n'
                   '<b>Врач-стажер:</b> ты только что трудоустроился в "ПризываНет" на ставку врача и еще проходишь обучение\n\n'
                   '<b>И.О. врача:</b> ты закончил обучение и работаешь в кластере, но не проходил аттестацию на врача\n\n'
                   '<b>Врач:</b> ты прошел аттестацию на врача и полностью закончил стажировку\n\n'
                   '<b>Сеньор врачей:</b> ты руководишь врачами своего кластера\n\n'
                   '<b>Стажер L1:</b> ты только что трудоустроился в "ПризываНет" на должность младшего специалиста поддержки клиентов\n\n'
                   '<b>Сотрудник L1:</b> ты прошел стажировку и состоишь в команде специалистов поддержки\n\n'
                   '<b>Сеньор L1:</b> ты руководишь командой специалистов поддержки\n\n'
                   'Выбирай честно 🗿',
                     reply_markup=await get_pos_keyboard())


# @dp.callback_query_handler(other_kb.register_callback.filter(stage='position'), state=FSMRegister.role)
async def get_role(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    role = int(callback_data.get('stage_data'))
    await state.update_data(role=role)
    if role in (5, 6, 7, 8):
        await FSMRegister.traineeship.set()
        await call.message.answer('Отлично, с этим определились. Тогда расскажи немного про ординатуру:\n'
                                  'Выбери один из нескольких вариантов ответа:\n\n'
                                  '<b>Не поступал и не собираюсь:</b> ты не был в ординатуре и не хочешь туда\n\n'
                                  '<b>Не поступал, но собираюсь:</b> ты не был в ординатуре, но хочешь и будешь туда поступать\n\n'
                                  '<b>Учусь прямо сейчас:</b> ты обучаешься в ординатуре на данный момент\n\n'
                                  '<b>Закончил обучение:</b> ты уже выпустился из ординатуры с дипломом на руках',
                                  reply_markup=await get_spec_keyboard())
        await call.message.delete()
    if role in (9, 10, 11):
        await FSMRegister.med_education.set()
        await call.message.answer('Отлично, с этим определились. Скажи, пожалуйста, есть ли у тебя медицинское образование?',
                                  reply_markup=await get_education_keyboard())
        await call.message.delete()


# @dp.callback_query_handler(other_kb.register_callback.filter(stage='education'), state=FSMRegister.med_education)
async def get_education(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    await state.update_data(
        traineeship=int(callback_data.get("stage_data")),
        profession=None,
        start_year=None,
        end_year=None
    )
    await FSMRegister.phone.set()
    await call.message.answer('Записал 👌\n\nТеперь пробежимся по формальностям:\nВведи своей номер телефона 📱')
    await call.message.delete()


# @dp.callback_query_handler(other_kb.register_callback.filter(stage='spec'), state=FSMRegister.traineeship)
async def get_traineeship(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    if int(callback_data.get('stage_data')) in (2, 3, 4):
        await call.answer()
        await state.update_data(traineeship=int(callback_data.get('stage_data')))
        await FSMRegister.profession.set()
        await call.message.answer('Хорошо, а специальность известна?\n<i>Например, ЛОР или неврология</i>')
        await call.message.delete()
    elif int(callback_data.get('stage_data')) == 1:
        await call.answer()
        await state.update_data(
            traineeship=int(callback_data.get('stage_data')),
            profession=None,
            start_year=None,
            end_year=None,
        )
        await call.message.answer('Записал 👌\n\nТеперь пробежимся по формальностям:\nВведи своей номер телефона 📱')
        await FSMRegister.phone.set()
        await call.message.delete()


# @dp.message_handler(state=FSMRegister.profession)
async def get_profession(msg: types.Message, state: FSMContext):
    await state.update_data(profession=msg.text)
    await FSMRegister.start_year.set()
    await msg.answer('Отличный выбор 😎\n\nНапиши, пожалуйста, год поступления')


# @dp.message_handler(state=FSMRegister.start_year)
async def get_start_year(msg: types.Message, state: FSMContext):
    await state.update_data(start_year=msg.text)
    await FSMRegister.end_year.set()
    await msg.answer('Супер, теперь год окончания')


# @dp.message_handler(state=FSMRegister.end_year)
async def get_end_year(msg: types.Message, state: FSMContext):
    await state.update_data(end_year=msg.text)
    await msg.answer('Записал 👌\n\nТеперь пробежимся по формальностям:\nВведи своей номер телефона 📱')
    await FSMRegister.phone.set()


# @dp.message_handler(state=FSMRegister.phone)
async def get_phone_number(msg: types.Message, state: FSMContext):
    await state.update_data(phone=msg.text)
    await FSMRegister.email.set()
    await msg.answer('Принял, теперь напиши свою гугл-почту 📧\n(заканчивается на @gmail.com)')


# @dp.message_handler(state=FSMRegister.email)
async def get_email(msg: types.Message, state: FSMContext):
    await state.update_data(email=msg.text)
    await FSMRegister.birthdate.set()
    await msg.answer('Огонь, осталось только написать дату рождения в формате <i>ДД.ММ.ГГГГ</i>')


# @dp.message_handler(state=FSMRegister.birthdate)
async def finish_register(msg: types.Message, state: FSMContext):
    try:
        birthdate = datetime.strptime(msg.text, "%d.%m.%Y")
        await state.update_data(bdate=birthdate, username='@' + msg.from_user.username, chat_id=msg.from_user.id)
        user = await state.get_data()
        user_info = await user_db_roundtrip(tuple(user.values()))
        await msg.answer('Спасибо, что уделил мне время 👏\nРегистрация завершена :)', reply_markup=types.ReplyKeyboardRemove())
        if user['role'] not in (8, 9):
            await state.finish()
            return
        new_trainee, trainee_id = await user_wrapper(user_info)
        await msg.bot.send_message(
            chat_id=323123946, text=f'Новый стажер прошел регистрацию:\n\n{new_trainee}\n\nКому распределяем?',
            reply_markup=await get_mentors_keyboard(msg.from_user.id)
        )
        await state.finish()
        logger.log('REGISTRATION', f'@{msg.from_user.username} completed registration.')
    except ValueError:
        await msg.answer("Это некорректная дата. Пожалуйста, введи дату по шаблону.")


async def echo(msg: types.Message):
    if "привет" in msg.text.lower():
        await msg.reply(random.choice(answers['hello']))
    else:
        await msg.reply(random.choice(answers['others']))


def setup(dp: Dispatcher):
    dp.register_message_handler(commands_start, CommandStart(), state="*", chat_type=types.ChatType.PRIVATE)
    dp.register_callback_query_handler(start_register, register_callback.filter(stage='yes'), chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(cancel_handler, state='*', commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(get_fullname, state=FSMRegister.name)
    dp.register_message_handler(get_city, state=FSMRegister.city)
    dp.register_callback_query_handler(get_role, register_callback.filter(stage='position'), state=FSMRegister.role)
    dp.register_callback_query_handler(get_education, register_callback.filter(stage='education'), state=FSMRegister.med_education)
    dp.register_callback_query_handler(get_traineeship, register_callback.filter(stage='spec'),
                                       state=FSMRegister.traineeship)
    dp.register_message_handler(get_profession, state=FSMRegister.profession)
    dp.register_message_handler(get_start_year, state=FSMRegister.start_year)
    dp.register_message_handler(get_end_year, state=FSMRegister.end_year)
    dp.register_message_handler(get_phone_number, state=FSMRegister.phone)
    dp.register_message_handler(get_email, state=FSMRegister.email)
    dp.register_message_handler(finish_register, state=FSMRegister.birthdate)
    dp.register_message_handler(echo, chat_type=types.ChatType.PRIVATE)


