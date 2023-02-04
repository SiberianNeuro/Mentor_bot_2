from loguru import logger

from aiogram import types, Router, F, Bot
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext

from app.filters import RoleFilter
from app.models.states import FSMExam
from app.models.exam import Exam, ExamStage, ExamResult
from app.utils.misc.sheets_append import add_user_array
from app.utils.misc.wrappers import ExamWrapper
from app.utils.misc.file_parsing import file_parser, Protocol
from app.services.get_trainee_calls import get_calls
from app.keyboards.exam_kb import *
from app.keyboards.common_kb import get_cancel_button, keyboard_generator

from sqlalchemy import select, and_
from sqlalchemy.orm import sessionmaker

router = Router()
router.message.filter(F.chat.type == "private", RoleFilter(role=[3, 4, 12], team=[5, 17, 18, 19]))
router.callback_query.filter(F.message.chat.type == "private", RoleFilter(role=[3, 4, 12], team=[5, 17, 18, 19]))


"""Загрузка опроса"""


# Начало загрузки опроса: документ
@router.message(F.text == 'Загрузить опрос ⏏')
async def exam_start(msg: types.Message, state: FSMContext, db: sessionmaker):
    await state.set_state(FSMExam.document)
    await msg.answer('<b>Начинаем загрузку результатов аттестации</b>\n'
                     'Чтобы выйти из режима загрузки, нажми кнопку <b>"Отмена"</b> или напиши /moderator',
                     reply_markup=await get_cancel_button())
    await msg.answer('Сейчас тебе нужно прислать мне протокол опроса 📜')


@router.message(state='*', commands='Отмена')
@router.message(Text(text='Отмена', ignore_case=True), state='*')
async def cancel_handler_admin(msg: types.Message, state: FSMContext, user):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await msg.reply('Принято 👌', reply_markup=await keyboard_generator(user))


# Загрузка документа, парсинг документа, переход к выбору формата опроса
@router.message(content_types=types.ContentType.DOCUMENT, state=FSMExam.document)
async def load_document(msg: types.Message, state: FSMContext, bot: Bot, db: sessionmaker):
    protocol: Protocol | str = await file_parser(msg.document, bot, db)
    if isinstance(protocol, str):
        await msg.answer(text=protocol)

    elif isinstance(protocol, Protocol):
        await state.update_data(
            document=msg.document.file_id,
            user_id=protocol.user,
            stage_id=protocol.stage_id,
            result_id=protocol.result_id,
            score=protocol.score,
            exam_date=str(protocol.exam_date),
            retake_date=protocol.retake_date
        )
        async with db.begin() as session:
            stmt = select(ExamStage.stage, ExamResult.result).where(
                and_(
                    ExamStage.id == protocol.stage_id,
                    ExamResult.id == protocol.result_id
                )
            )
            query = await session.execute(stmt)
            stage_result = query.mappings().first()
            stage, result = stage_result.stage, stage_result.result
        await msg.answer(f'Что получилось на выходе:\n\n'
                         f'Сотрудник: <b>{protocol.fullname}</b>\n'
                         f'Формат опроса: {stage}\n'
                         f'Результат опроса: {result}\n'
                         f'Набрано баллов: {protocol.score}\n'
                         f'Дата опроса: {protocol.exam_date.strftime("%d.%m.%Y")}\n'
                         f'Дата переопроса: {protocol.retake_date.strftime("%d.%m.%Y") if protocol.retake_date else "-"}\n\n'
                         f'Если что-то не так, проверь протокол и нажми перезагрузить. Если все хорошо,'
                         f'то жми кнопку "Подтвердить"', reply_markup=await get_overload_keyboard())
        await state.set_state(FSMExam.confirm)


@router.callback_query(ExamCallback.filter(F.action == "overload"), state=FSMExam.confirm)
async def confirm_document(call: types.CallbackQuery, state: FSMContext, callback_data: ExamCallback):
    exam_data = await state.get_data()
    if callback_data.value == 1:
        if exam_data['stage_id'] == 3 and exam_data['result_id'] == 3:
            await call.message.answer('Ну раз это ИОшка, тогда давай и звоночки подтянем! Скинь мне ссылки на звонки '
                                      '<b>через Ctrl+Enter</b>.')
            await state.set_state(FSMExam.calls)
        else:
            await state.update_data(calls=None)
            await call.message.answer('Хорошо, тогда мне нужна ссылка на YouTube ⏩\n'
                                      'Если ссылок много, то пришли их через Ctrl+Enter')
            await state.set_state(FSMExam.link)
    else:
        await call.message.answer('Хорошо, тогда жду документ 📜')
        await state.set_state(FSMExam.document)
    await call.answer()


@router.message(state=FSMExam.calls)
async def load_calls(msg: types.Message, state: FSMContext):
    await state.update_data(calls=msg.text)
    await msg.answer('Хорошо, тогда мне нужна ссылка на YouTube ⏩\n'
                     'Если ссылок много, то пришли их через Ctrl+Enter')
    await state.set_state(FSMExam.link)


# Загрузка ссылки, обёртка результатов загрузки
@router.message(state=FSMExam.link)
async def load_link(msg: types.Message, state: FSMContext, db: sessionmaker, config, bot: Bot):
    await state.update_data(link=msg.text)
    exam = await state.get_data()
    async with ExamWrapper(data=exam, db=db) as w:
        await w._get_wrapper()
        print(w.wrapper)
    w: ExamWrapper = await ExamWrapper().wrapper()
    wrapper = await exam_processing(to_sql)
    logger.log('DATABASE', f'@{msg.from_user.username} append exam results to database')
    exam_info = await Wrappers.exam_wrapper(wrapper)
    try:
        await msg.answer_document(
            document=exam_info['document'],
            caption=exam_info['wrapper'],
            reply_markup=await get_delete_button(exam_info['exam_id'])
        )
        if (exam_info['stage_id'] in (3, 4) and exam_info['result_id'] == 3) or exam_info['result_id'] == 1:
            await bot.send_document(
                chat_id=config.misc.exam_chat,
                document=exam_info['document'],
                caption=exam_info['wrapper'],
            )
        if exam_info['stage_id'] == 3 and exam_info['result_id'] == 3:
            user_info = await get_user_info(wrapper['fullname'])

            await msg.bot.send_message(
                chat_id=config.misc.doc_lead_chat,
                text=f'Требуется распределение ИО врача в кластер:\n'
                     f'{user_wrapper["wrapper"]}',
                reply_markup=await get_clusters_keyboard(to_sql['user_id'])
            )
    except Exception as e:
        logger.exception(e)
    finally:
        await state.finish()


# Команда на удаление опроса
# @dp.callback_query_handler(IsAdmin(), exam_callback.filter(action='delete'))
async def delete_exam_callback(call: types.CallbackQuery, callback_data: dict):
    await delete_exam(callback_data.get("action_data"))
    logger.warning(f'@{call.from_user.username} delete exam.')
    await call.answer(text='Информация удалена', show_alert=True)
    await call.message.delete()


async def change_active_callback(call: types.CallbackQuery, callback_data: dict):
    active = callback_data.get('active_now')
    user = await change_user_active_status(callback_data.get("user_id"), active)
    message_text = f'Пользователь {user["username"]} '
    message_text += 'деактивирован' if active == '1' else 'активирован'

    await call.answer(text=message_text, show_alert=True)
    user_info = await Wrappers.user_wrapper(user)
    logger.warning(f'@{call.from_user.username} changed user {user["user_fullname"]} status to {user_info["active"]}')
    await call.message.edit_text(
        text=user_info['wrapper'], reply_markup=await change_active_button(
            user_info['user_id'], user_info['active']
        )
    )


"""Поиск"""


# Начало поиска: запрос ФИО
# @dp.message_handler(IsAdmin(), Text(equals='Найти 👀'), state=None)
async def exam_search_start(msg: types.Message):
    await msg.reply('👇🏼 Введи Ф.И.О. сотрудника полностью или по отдельности',
                    reply_markup=await get_cancel_button())
    await FSMExam.exam_searching.set()


# Поиск ФИО по БД, вывод результатов
# @dp.message_handler(IsAdmin(), state=FSMAdmin.trainee_name)
async def exam_search_result(msg: types.Message, state: FSMContext):
    exams = await db_search_exam(msg.text.title())
    if not exams:
        await msg.answer('Информации об этом сотруднике нет 🤔',
                         reply_markup=await get_admin_kb())
    else:
        for exam in exams:
            exam_info = await Wrappers.exam_wrapper(exam)
            await msg.answer_document(
                document=exam_info['document'],
                caption=exam_info['wrapper'],
                reply_markup=await get_delete_button(exam_info['exam_id'])
            )
        await msg.answer('Готово!👌', reply_markup=await get_admin_kb())
    await state.finish()


async def employee_search_start(msg: types.Message):
    await msg.reply('👇🏼 Введи Ф.И.О. сотрудника полностью или по отдельности',
                    reply_markup=await get_cancel_button())
    await FSMExam.user_searching.set()


async def employee_search_result(msg: types.Message, state: FSMContext):
    users = await get_user_info(msg.text)
    if not users:
        await msg.answer('Информации об этом сотруднике нет 🤔',
                         reply_markup=await get_admin_kb())
    else:
        for user in users:
            user_info = await Wrappers.user_wrapper(user)
            await msg.answer(
                text=user_info['wrapper'],
                reply_markup=await change_active_button(
                    id=user_info['user_id'],
                    active=user_info['active_id']
                )
            )
        await msg.answer('Готово!👌', reply_markup=await get_admin_kb())
    await state.finish()


async def get_trainee_calls(msg: types.Message):
    await msg.answer(
        'Я пришлю тебе ссылки на звонки с одного из номеров стажеров за сегодняшний день. Если передумаешь - нажми '
        '<b>Отмена</b>.',
        reply_markup=await get_cancel_button()
    )
    await msg.answer('Выбери номер:', reply_markup=await get_trainee_phones())
    await FSMExam.calls_searching.set()


async def get_calls_date(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await state.update_data(phone=callback_data.get('action_data'))
    await call.message.answer('Хорошо, за какой день берем звонки?',
                              reply_markup=await SimpleCalendar().start_calendar())
    await call.answer()
    await call.message.delete()


async def calls_result(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, phone_date = await SimpleCalendar().process_selection(call, callback_data)
    if selected:
        from datetime import date
        try:
            assert phone_date.date() <= date.today()
            phones = await state.get_data()
            calls = await get_calls(phone_number=phones['phone'], call_date=phone_date.strftime("%Y-%m-%d"))
            await call.message.answer(text=calls, reply_markup=await get_admin_kb())
            await call.answer()
            await call.message.delete()
            logger.info(f'Requested calls for {phone_date.strftime("%Y-%m-%d")} by {call.from_user.username}')
            await state.finish()
        except AssertionError:
            await call.message.edit_text('Я не могу заглянуть в будущее 👻',
                                         reply_markup=await SimpleCalendar().start_calendar())


"""Распределение"""


async def route_teams(call: types.CallbackQuery, callback_data: dict):
    team = callback_data.get('team_id')
    user_id = callback_data.get('user_id')

    info = await define_team(team=team, user_id=user_id)
    user_wrapper = await Wrappers.user_wrapper(info['user_info'])
    await call.message.answer('Стажер распределен!')
    await call.bot.send_message(
        chat_id=info['chat_id'],
        text=f'{info["fullname"].split(" ")[1]}, тебе определен новый врач:\n\n{user_wrapper["wrapper"]}'
    )
    await call.bot.send_message(
        chat_id=config.misc.exam_chat,
        text='ИО врача {0} назначен в команду {1}'.format(
            user_wrapper["wrapper"].split("\n")[0], user_wrapper["wrapper"].split("\n")[1]
        )
    )


async def route_trainees(call: types.CallbackQuery, callback_data: dict):
    mentor_id = int(callback_data.get('mentor_id'))
    role_id = int(callback_data.get('role_id'))
    user_chat_id = int(callback_data.get('user_id'))

    doctors_chat = await call.bot.get_chat(chat_id=config.misc.doctors_chat)
    headmaster_chat = await call.bot.get_chat(chat_id=config.misc.headmaster_chat)
    l3_chat = await call.bot.get_chat(
        chat_id=config.misc.kis_chat if mentor_id == 5 else config.misc.kor_chat
    )
    l1_chat = await call.bot.get_chat(chat_id=config.misc.l1_chat)
    mentor_info = await get_admin(mentor_id)
    welcome_info = {
        "role_id": role_id,
        "doctors_chat": doctors_chat['invite_link'],
        "headmaster_chat": headmaster_chat['invite_link'],
        "l3_chat": l3_chat['invite_link'],
        "l1_chat": l1_chat['invite_link'],
        "mentor_chat": mentor_info['chat_id'],
        "mentor_name": mentor_info['fullname'],
        "mentor_username": mentor_info['username']
    }
    welcome_wrapper = await Wrappers.welcome_wrapper(welcome_info=welcome_info)
    await call.message.answer('Отравляюсь радовать стажера 🦾')
    await call.bot.send_message(
        chat_id=user_chat_id, text=welcome_wrapper
    )

    user_info = await get_user_info(user_chat_id)
    user = await Wrappers.user_wrapper(user_info)
    await call.bot.send_message(
        chat_id=mentor_info['chat_id'], text=f'{mentor_info["fullname"].split()[1]}, тебе определен новый стажер:\n'
                                             f'{user["wrapper"]}'
    )
    await call.message.delete()
    await call.answer()

    await add_user_array(user_info=user_info, mentor_name=mentor_info['fullname'])

# def setup(dp: Dispatcher):
#     dp.register_message_handler(admin_start, is_admin=True, commands=['moderator'], chat_type=types.ChatType.PRIVATE)
#     dp.register_message_handler(exam_start, Text(equals='Загрузить опрос ⏏'), is_admin=True,
#                                 chat_type=types.ChatType.PRIVATE)
#     dp.register_message_handler(cancel_handler_admin, state='*', commands='отмена')
#     dp.register_message_handler(cancel_handler_admin, Text(equals='отмена', ignore_case=True), state='*')
#     dp.register_message_handler(load_document, content_types=['document'], state=Exam.document, is_admin=True)
#     dp.register_callback_query_handler(confirm_document, exam_callback.filter(action='overload'), state=Exam.confirm,
#                                        is_admin=True)
#     dp.register_message_handler(load_calls, state=Exam.calls, is_admin=True)
#     dp.register_message_handler(load_link, is_admin=True, state=Exam.link)
#     dp.register_callback_query_handler(delete_exam_callback, exam_callback.filter(action='delete'), is_admin=True)
#     dp.register_callback_query_handler(change_active_callback, active_callback.filter(active_action='change'),
#                                        is_admin=True)
#     dp.register_message_handler(exam_search_start, Text(equals='Найти опрос 👀'), is_admin=True,
#                                 chat_type=types.ChatType.PRIVATE)
#     dp.register_message_handler(exam_search_result, is_admin=True, state=Exam.exam_searching)
#     dp.register_message_handler(employee_search_start, Text(equals='Найти сотрудника 👨‍⚕'), is_admin=True,
#                                 chat_type=types.ChatType.PRIVATE)
#     dp.register_message_handler(employee_search_result, is_admin=True, state=Exam.user_searching)
#     dp.register_message_handler(get_trainee_calls, Text(equals="Звонки стажеров 📞"), chat_type=types.ChatType.PRIVATE,
#                                 is_admin=True)
#     dp.register_callback_query_handler(get_calls_date, exam_callback.filter(action='phones'), is_admin=True,
#                                        state=Exam.calls_searching)
#     dp.register_callback_query_handler(calls_result, simple_cal_callback.filter(), is_admin=True,
#                                        state=Exam.calls_searching)
#     dp.register_callback_query_handler(route_teams, mentor_callback.filter(mentor_id='clusters'), is_admin=True)
#     dp.register_callback_query_handler(route_trainees, mentor_callback.filter(), is_admin=True)
