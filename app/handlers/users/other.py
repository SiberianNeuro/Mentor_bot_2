import random
from datetime import datetime
from loguru import logger

from aiogram import F, Bot, types, Router
from aiogram.filters import CommandStart, Text
from aiogram.fsm.context import FSMContext

from app.keyboards.common_kb import keyboard_generator
from app.keyboards.register_kb import *
from app.utils.misc.wrappers import Wrappers
from app.models.states import Register
from app.models.user import User
from app.models.views import UserView
from app.models.simple_answers import answers

router = Router()
router.message.filter(F.chat.type == 'private')
router.callback_query.filter(F.chat.type == 'private')


@router.message(CommandStart(), state="*")
async def commands_start(msg: types.Message, state: FSMContext, user):
    await state.clear()
    await msg.delete()
    await msg.answer_sticker('CAACAgIAAxkBAAIE4GKSGruXCE8S-gM_iIJyaTbM9TGYAAJPAAOtZbwUa5EcjYesr5MkBA')
    await msg.answer('Привет ✌\n\nЯ помощник в медицинском отделе ДОК 🤖')
    if user:
        await msg.answer('Вижу, что ты уже зарегистрирован 🤠\n\nЧем могу помочь?',
                         reply_markup=await keyboard_generator(user))
    else:
        await msg.answer('Вижу, что ты еще не проходил регистрацию 😱\n\n⬇️Скорее жми кнопку и начнём знакомиться⬇️',
                         reply_markup=await get_register_button())


@router.callback_query(RegisterCallback.filter(F.stage == 'register_start'), state=None)
async def start_register(call: types.CallbackQuery, state: FSMContext, user: User):
    if user:
        await call.answer()
        await call.message.answer('Ты уже регистрировался 👺')
        await call.message.delete()
        logger.debug(f"{call.from_user.username} - попытка повторной регистрации")
    else:
        await call.answer()
        await state.set_state(Register.name)
        await call.message.answer('Давай знакомиться✌️\n\n'
                                  'Если вдруг передумаешь регистрироваться, либо что-то напишешь не так,'
                                  ' жми кнопку <b>"Отмена"</b>,'
                                  'или снова напиши /start',
                                  reply_markup=await get_cancel_button())
        await call.message.answer('Для начала напиши своё ФИО полностью кириллицей\n\n'
                                  '<b><i>Например: Погребной Данила Олегович</i></b>')
        await call.message.delete()
        logger.log('REGISTRATION', f'@{call.from_user.username} started registration process...')


@router.message(state='*', commands='Отмена')
@router.message(Text(text='Отмена', ignore_case=True), state='*')
async def cancel_handler(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await msg.reply('Принято 👌', reply_markup=types.ReplyKeyboardRemove())


@router.message(state=Register.name)
async def get_fullname(msg: types.Message, state: FSMContext):
    try:
        first_name = msg.text.split()[1]
        await state.update_data(fullname=msg.text.title())
        await state.set_state(Register.city)
        await msg.answer(f'Приятно познакомиться, {first_name}!\n\nТеперь напиши город, в котором ты работаешь 🏙\n'
                         f'<i>Например: Новосибирск, Санкт-Петербург, Екатеринбург</i>')
    except IndexError:
        await msg.answer('Уверен, что ввел имя, как я тебя попросил? Попробуй еще раз :)')


@router.message(state=Register.city)
async def get_city(msg: types.Message, state: FSMContext, db):
    city = msg.text.title()
    await state.update_data(city=city)
    await state.set_state(Register.role)
    await msg.answer('Замечательно 🤟\nТеперь выбери свою должность:\n\n'
                     '🎓 <b>Врач-стажер:</b> ты только что трудоустроился в "ПризываНет" '
                     'на ставку врача и еще проходишь обучение\n\n'
                     '👩🏻‍⚕ <b>Врач:</b> ты прошел аттестацию на врача и полностью закончил стажировку\n\n'
                     '🧑🏻‍💻 <b>Стажер L1:</b> ты только что трудоустроился в "ПризываНет" '
                     'на должность младшего специалиста поддержки клиентов\n\n '
                     'Выбирай честно 🗿',
                     reply_markup=await get_pos_keyboard(db))


@router.callback_query(RegisterCallback.filter(F.stage == 'position'), state=Register.role)
async def get_role(call: types.CallbackQuery, state: FSMContext, callback_data: RegisterCallback, db):
    await call.answer()
    role = callback_data.value
    await state.update_data(role=role)
    if role in (6, 8):
        await state.set_state(Register.traineeship)
        await call.message.answer('Отлично, с этим определились. Тогда расскажи немного про ординатуру:\n'
                                  'Выбери один из нескольких вариантов ответа:\n\n'
                                  '😎 <b>Не поступал и не собираюсь:</b> ты не был в ординатуре и не хочешь туда\n\n'
                                  '😏 <b>Не поступал, но собираюсь:</b> ты не был в ординатуре, но хочешь и будешь туда '
                                  'поступать\n\n'
                                  '🤯 <b>Учусь прямо сейчас:</b> ты обучаешься в ординатуре на данный момент\n\n'
                                  '😷 <b>Закончил обучение:</b> ты уже выпустился из ординатуры с дипломом на руках',
                                  reply_markup=await get_spec_keyboard())
        await call.message.delete()
    if role == 9:
        await state.set_state(Register.med_education)
        await call.message.answer(
            'Отлично, с этим определились. Скажи, пожалуйста, есть ли у тебя медицинское образование?',
            reply_markup=await get_education_keyboard(db))
        await call.message.delete()


@router.callback_query(RegisterCallback.filter(F.stage == 'education'), state=Register.med_education)
async def get_education(call: types.CallbackQuery, state: FSMContext, callback_data: RegisterCallback):
    await call.answer()
    await state.update_data(
        traineeship=callback_data.value,
        profession=None,
        start_year=None,
        end_year=None
    )
    await state.set_state(Register.phone)
    await call.message.answer('Записал 👌\n\nТеперь пробежимся по формальностям:\nВведи своей номер телефона 📱')
    await call.message.delete()


@router.callback_query(RegisterCallback.filter(F.stage == 'spec'), state=Register.traineeship)
async def get_traineeship(call: types.CallbackQuery, state: FSMContext, callback_data: RegisterCallback):
    if callback_data.value in (2, 3, 4):
        await call.answer()
        await state.update_data(traineeship=callback_data.value)
        await state.set_state(Register.profession)
        await call.message.answer('Хорошо, а специальность известна?\n<i>Например, ЛОР или неврология</i>')
        await call.message.delete()
    elif callback_data.value == 1:
        await call.answer()
        await state.update_data(
            traineeship=callback_data.value,
            profession=None,
            start_year=None,
            end_year=None,
        )
        await call.message.answer('Записал 👌\n\nТеперь пробежимся по формальностям:\nВведи своей номер телефона 📱')
        await state.set_state(Register.phone)
        await call.message.delete()


@router.message(state=Register.profession)
async def get_profession(msg: types.Message, state: FSMContext):
    await state.update_data(profession=msg.text)
    await state.set_state(Register.start_year)
    await msg.answer('Отличный выбор 😎\n\nНапиши, пожалуйста, год поступления')


@router.message(state=Register.start_year)
async def get_start_year(msg: types.Message, state: FSMContext):
    await state.update_data(start_year=msg.text)
    await state.set_state(Register.end_year)
    await msg.answer('Супер, теперь год окончания')


@router.message(state=Register.end_year)
async def get_end_year(msg: types.Message, state: FSMContext):
    await state.update_data(end_year=msg.text)
    await msg.answer('Записал 👌\n\nТеперь пробежимся по формальностям:\nВведи своей номер телефона 📱')
    await state.set_state(Register.phone)


@router.message(state=Register.phone)
async def get_phone_number(msg: types.Message, state: FSMContext):
    entities = msg.entities or []
    phone_number = ''
    for item in entities:
        if item.type == 'phone_number':
            phone_number = item.extract_from(msg.text)
    if phone_number != '':
        await state.update_data(phone=phone_number)
        await state.set_state(Register.email)
        await msg.answer('Принял, теперь напиши свою гугл-почту 📧\n(заканчивается на @gmail.com)')
    else:
        await msg.answer('Не распознал номер телефона :( Пожалуйста, проверь правильность заполнения. '
                         'Например, <i>89997776655</i>')


@router.message(state=Register.email)
async def get_email(msg: types.Message, state: FSMContext):
    entities = msg.entities or []
    email = ''
    for item in entities:
        if item.type == 'email':
            email = item.extract_from(msg.text)
    if email != '':
        await state.update_data(email=email)
        await state.set_state(Register.birthdate)
        await msg.answer('Огонь, осталось только написать дату рождения в формате <i>ДД.ММ.ГГГГ</i>')
    else:
        await msg.answer('Не распознал email :( Пожалуйста, проверь правильность заполнения. '
                         'Например, <i>example@gmail.com</i>')


@router.message(state=Register.birthdate)
async def finish_register(msg: types.Message, state: FSMContext, db, config, bot: Bot):
    try:
        username = "@" + msg.from_user.username
    except Exception:
        await msg.answer('Не нашел твой юзернейм :( Тебе обязательно нужно его создать!')
        return
    try:
        birthdate = datetime.date(datetime.strptime(msg.text, "%d.%m.%Y"))
    except ValueError:
        await msg.answer("Это некорректная дата. Пожалуйста, введи дату по шаблону.")
        return

    user_params = await state.get_data()
    new_user = User(
        id=msg.from_user.id,
        fullname=user_params['fullname'],
        username=username,
        city=user_params['city'],
        role_id=user_params['role'],
        traineeship_id=user_params['traineeship'],
        profession=user_params['profession'],
        start_year=user_params['start_year'],
        end_year=user_params['end_year'],
        phone=user_params['phone'],
        email=user_params['email'],
        birthdate=birthdate,
        reg_date=datetime.utcnow(),
        active=1
    )

    async with db.begin() as session:
        await session.merge(new_user)
        user_info: UserView = await session.get(UserView, msg.from_user.id)
        await session.commit()

    await msg.answer('Спасибо, что уделил мне время 👏\nРегистрация завершена :)',
                     reply_markup=types.ReplyKeyboardRemove())
    if user_params['role'] not in (8, 9):
        await state.clear()
        return
    user_wrapper = await Wrappers.user_wrapper(user_info)
    await bot.send_message(
        chat_id=config.misc.router_chat, text=f'Новый стажер прошел регистрацию:\n\n{user_wrapper["wrapper"]}\n\nКому '
                                              f'распределяем?',
        # reply_markup=await get_mentors_keyboard(msg.from_user.id)
    )
    await state.clear()
    logger.log('REGISTRATION', f'@{msg.from_user.username} completed registration.')


@router.message()
async def echo(msg: types.Message):
    if "привет" in msg.text.lower():
        await msg.reply(random.choice(answers['hello']))
    else:
        await msg.reply(random.choice(answers['others']))
