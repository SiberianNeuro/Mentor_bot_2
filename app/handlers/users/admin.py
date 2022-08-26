from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram_calendar import SimpleCalendar, simple_cal_callback

from loguru import logger

from app.db.mysql_db import exam_processing, db_search_exam, delete_exam, get_user_info, get_admin, change_user_active_status
from app.utils.misc.sheets_append import add_user_array
from app.utils.misc.wrappers import report_wrapper, search_wrapper, user_wrapper
from app.utils.states import Exam
from app.utils.misc.file_parsing import file_parser
from app.utils.misc.get_trainee_calls import get_calls
from app.keyboards.other_kb import get_cancel_button
from app.keyboards.admin_kb import *
from app.services.config import load_config

config = load_config(".env")


# Команда входа в админку
# @dp.message_handler(IsAdmin(), commands=['moderator'], state="*")
async def admin_start(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer(f'Приветствую тебя, обучатор! 🦾\n\n'
                     f'Что я умею:\n\n'
                     f'👉🏻 Нажми на кнопку <b>"Загрузить"</b>, чтобы передать мне информацию о прошедшей аттестации\n'
                     f'👉🏻 Нажми кнопку <b>"Найти"</b>, чтобы найти информацию о предыдущих аттестациях\n'
                     f'👉🏻 Нажми кнопку <b>"Рассылка"</b>, если нужна помощь в рассылке тестов',
                     reply_markup=await get_admin_kb())
    await msg.delete()


"""Загрузка опроса"""


# Начало загрузки опроса: документ
# @dp.message_handler(IsAdmin(), Text(equals='Загрузить ⏏'), state=None)
async def exam_start(msg: types.Message):
    await Exam.document.set()
    await msg.answer('<b>Начинаем загрузку результатов аттестации</b>\n'
                     'Чтобы выйти из режима загрузки, нажми кнопку <b>"Отмена"</b> или напиши /moderator',
                     reply_markup=await get_cancel_button())
    await msg.answer('Сейчас тебе нужно прислать мне протокол опроса 📜')


# @dp.message_handler(state='*', commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler_admin(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await msg.reply('Принято 👌', reply_markup=await get_admin_kb())


# Загрузка документа, парсинг документа, переход к выбору формата опроса
# @dp.message_handler(IsAdmin(), content_types=['document'], state=FSMAdmin.document)
async def load_document(msg: types.Message, state: FSMContext):
    source: tuple = await file_parser(msg.document.file_id, msg.document.file_name)

    if source == 0:
        await msg.answer("Я не распознал протокол.\n\nПроверь, актуальным ли протоколом ты пользуешься.\n"
                         "Если нет, то узнай у руководителя актуальную версю, перепиши результаты туда, и снова "
                         "отправь мне.")
    elif source == 1:
        await msg.answer(
            "Я не нашел итоговое количество баллов.\n\nВнимательно посмотри, заполнил ли ты их. Если не заполнил - "
            "заполняй и присылай мне протокол повторно.")
    elif source == 3:
        await msg.answer(
            "Поле 'Дата проведения проф.опроса' заполнено некорректно.\n\nПожалуйста, введи дату в формате "
            "<i>ДД.ММ.ГГГГ</i> и пришли мне повторно.")
    elif source == 4:
        await msg.answer("Не заполнено поле 'Дата проведения проф.опроса'.\n\nЗаполни его, пожалуйста, и пришли мне "
                         "снова.")
    elif source == 5:
        await msg.answer("Неверно заполнено поле даты переаттестации.\n\nПожалуйста, введи дату в формате "
                         "<i>ДД.ММ.ГГГГ</i> и пришли мне повторно. ")
    elif source == 6:
        await msg.answer("Не распознал расширение протокола. Я кушаю протоколы только в формате .docx")
    elif source == 7:
        await msg.answer('Я не нашел такого стажера в базе данных. Проверь, пожалуйста, правильно ли заполнено ФИО.\n\n'
                         'Если все правильно, уточни у стажера, проходил ли он у меня регистрацию.')

    else:
        fullname, user_id, stage_id, result_id, score, exam_date = source[:6]
        try:
            retake_date = source[6].strftime("%d.%m.%Y")
        except AttributeError:
            retake_date = "-"
        retake_date_to_sql = str(source[6])

        await state.update_data(
            document=msg.document.file_id,
            user_id=user_id,
            stage_id=stage_id,
            result_id=result_id,
            score=score,
            exam_date=str(exam_date),
            retake_date=retake_date_to_sql
        )
        stages = ["Опрос на 3-й день", "Опрос в середине цикла обучения", "Опрос на И.О.", "Опрос на врача",
                  "Аттестация стажера L1"]
        stage = stages[stage_id - 1]
        results = ["Аттестация не пройдена ❌", "На пересдачу ⚠️", "Аттестация пройдена ✅"]
        result = results[result_id - 1]
        await msg.answer(f'Что получилось на выходе:\n\n'
                         f'Сотрудник: <b>{fullname}</b>\n'
                         f'Формат опроса: {stage}\n'
                         f'Результат опроса: {result}\n'
                         f'Набрано баллов: {score}\n'
                         f'Дата опроса: {exam_date.strftime("%d.%m.%Y")}\n'
                         f'Дата переопроса: {retake_date}\n\n'
                         f'Если что-то не так, проверь протокол и нажми перезагрузить. Если все хорошо,'
                         f'то жми кнопку "Подтвердить"', reply_markup=await get_overload_keyboard())
        await Exam.confirm.set()


# @dp.callback_query_handler(IsAdmin(), exam_callback.filter(action='overload'), state=FSMAdmin.confirm)
async def confirm_document(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    exam_data = await state.get_data()
    if int(callback_data.get('action_data')) == 1:
        if exam_data['stage_id'] == 3 and exam_data['result_id'] == 3:
            await call.message.answer('Ну раз это ИОшка, тогда давай и звоночки подтянем! Скинь мне ссылки на звонки '
                                      '<b>через Ctrl+Enter</b>.')
            await Exam.calls.set()
        else:
            await state.update_data(calls=None)
            await call.message.answer('Хорошо, тогда мне нужна ссылка на YouTube ⏩\n'
                                      'Если ссылок много, то пришли их через Ctrl+Enter')
            await Exam.link.set()
    else:
        await call.message.answer('Хорошо, тогда жду документ 📜')
        await Exam.document.set()
    await call.answer()


async def load_calls(msg: types.Message, state: FSMContext):
    await state.update_data(calls=msg.text)
    await msg.answer('Хорошо, тогда мне нужна ссылка на YouTube ⏩\n'
                     'Если ссылок много, то пришли их через Ctrl+Enter')
    await Exam.link.set()


# Загрузка ссылки, обёртка результатов загрузки
# @dp.message_handler(IsAdmin(), state=FSMAdmin.link)
async def load_link(msg: types.Message, state: FSMContext):
    await state.update_data(link=msg.text)
    to_sql = await state.get_data()
    wrapper = await exam_processing(to_sql)
    logger.log('DATABASE', f'@{msg.from_user.username} append exam results to database')
    await report_wrapper(wrapper, msg=msg)
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
    message_text = f'Пользователь {user["user_fullname"]} деактивирован' if active == '1' else f'Пользователь {user["user_fullname"]} активирован'
    logger.warning(f'@{call.from_user.username} changed user {user["user_fullname"]} status to {active}')
    await call.answer(text=message_text, show_alert=True)
    new_user_info, user_id, new_active = await user_wrapper(user['user_info'])
    await call.message.edit_text(text=new_user_info, reply_markup=await change_active_button(user_id, new_active))

"""Поиск"""


# Начало поиска: запрос ФИО
# @dp.message_handler(IsAdmin(), Text(equals='Найти 👀'), state=None)
async def exam_search_start(msg: types.Message):
    await msg.reply('👇🏼 Введи Ф.И.О. сотрудника полностью или по отдельности',
                    reply_markup=await get_cancel_button())
    await Exam.exam_searching.set()


# Поиск ФИО по БД, вывод результатов
# @dp.message_handler(IsAdmin(), state=FSMAdmin.trainee_name)
async def exam_search_result(msg: types.Message, state: FSMContext):
    read = await db_search_exam(msg.text.title())
    if not read:
        await msg.answer('Информации об этом сотруднике нет 🤔',
                         reply_markup=await get_admin_kb())
    else:
        await search_wrapper(read, msg=msg)
        await msg.answer('Готово!👌', reply_markup=await get_admin_kb())
    await state.finish()


async def employee_search_start(msg: types.Message):
    await msg.reply('👇🏼 Введи Ф.И.О. сотрудника полностью или по отдельности',
                    reply_markup=await get_cancel_button())
    await Exam.user_searching.set()


async def employee_search_result(msg: types.Message, state: FSMContext):
    result = await get_user_info(msg.text)
    if not result:
        await msg.answer('Информации об этом сотруднике нет 🤔',
                         reply_markup=await get_admin_kb())
    else:
        for user in result:
            user_data = await user_wrapper(user)
            await msg.answer(f'{user_data[0]}', reply_markup=await change_active_button(user_data[1], user_data[2]))
        await msg.answer('Готово!👌', reply_markup=await get_admin_kb())
    await state.finish()


async def get_trainee_calls(msg: types.Message):
    await msg.answer(
        'Я пришлю тебе ссылки на звонки с одного из номеров стажеров за сегодняшний день. Если передумаешь - нажми '
        '<b>Отмена</b>.',
        reply_markup=await get_cancel_button()
    )
    await msg.answer('Выбери номер:', reply_markup=await get_trainee_phones(msg.from_user.id))
    await Exam.calls_searching.set()


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


async def route_trainees(call: types.CallbackQuery, callback_data: dict):
    await call.answer()

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
    mentor_name = mentor_info['fullname']
    mentor_username = mentor_info['username']
    mentor_chat_id = mentor_info['chat_id']

    await call.message.answer('Отравляюсь радовать стажера 🦾')
    if role_id != 12:
        await call.bot.send_message(
            chat_id=user_chat_id, text=f'Теперь я покажу тебе необходимые telegram-группы 👻\n\n'
                                       f'<b>{doctors_chat["invite_link"]}</b>\n'
                                       f'Эта ссылка приведет тебя на канал, где общаются все наши доктора 🧑‍⚕\n\n'
                                       f'<b>{headmaster_chat["invite_link"]}</b>\n'
                                       f'Эта ссылка приведет тебя в группу, где общаются все стажеры - и опытные, '
                                       f'и новички 😉\n\n '
                                       f'<b>{l3_chat["invite_link"]}</b>\n'
                                       f'А по этой ссылке ты попадешь в чат своей учебной группы 👩‍🎓\n'
                                       f'Твой наставник, {mentor_name} {mentor_username}, будет на связи с тобой '
                                       f'всегда и по любым вопросам 🤩\n'
                                       f'Обязательно нажми на каждую ссылку, чтобы попасть чат 😇'
        )
    else:
        await call.bot.send_message(
            chat_id=user_chat_id, text=f'Теперь я покажу тебе необходимые telegram-группы 👻\n\n'
                                       f'<b>{l1_chat["invite_link"]}</b>\n'
                                       f'По этой ссылке ты попадешь в чат своей учебной группы 👩‍🎓\n'
                                       f'Твой наставник, {mentor_name} {mentor_username}, будет на связи с тобой '
                                       f'всегда и по любым вопросам 🤩\n'
                                       f'Обязательно нажми на каждую ссылку, чтобы попасть чат 😇'
        )
    user_info = await get_user_info(user_chat_id)
    user = await user_wrapper(user_info)
    await call.bot.send_message(
        chat_id=mentor_chat_id, text=f'{mentor_name.split()[1]}, тебе определен новый стажер:\n'
                                     f'{user[0]}'
    )
    await call.message.delete()
    await add_user_array(user_info=user_info, mentor_name=mentor_name)


def setup(dp: Dispatcher):
    dp.register_message_handler(admin_start, is_admin=True, commands=['moderator'], chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(exam_start, Text(equals='Загрузить опрос ⏏'), is_admin=True,
                                chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(cancel_handler_admin, state='*', commands='отмена')
    dp.register_message_handler(cancel_handler_admin, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(load_document, content_types=['document'], state=Exam.document, is_admin=True)
    dp.register_callback_query_handler(confirm_document, exam_callback.filter(action='overload'), state=Exam.confirm,
                                       is_admin=True)
    dp.register_message_handler(load_calls, state=Exam.calls, is_admin=True)
    dp.register_message_handler(load_link, is_admin=True, state=Exam.link)
    dp.register_callback_query_handler(delete_exam_callback, exam_callback.filter(action='delete'), is_admin=True)
    dp.register_callback_query_handler(change_active_callback, active_callback.filter(active_action='change'), is_admin=True)
    dp.register_message_handler(exam_search_start, Text(equals='Найти опрос 👀'), is_admin=True,
                                chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(exam_search_result, is_admin=True, state=Exam.exam_searching)
    dp.register_message_handler(employee_search_start, Text(equals='Найти сотрудника 👨‍⚕'), is_admin=True,
                                chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(employee_search_result, is_admin=True, state=Exam.user_searching)
    dp.register_message_handler(get_trainee_calls, Text(equals="Звонки стажеров 📞"), chat_type=types.ChatType.PRIVATE,
                                is_admin=True)
    dp.register_callback_query_handler(get_calls_date, exam_callback.filter(action='phones'), is_admin=True,
                                       state=Exam.calls_searching)
    dp.register_callback_query_handler(calls_result, simple_cal_callback.filter(), is_admin=True,
                                       state=Exam.calls_searching)
    dp.register_callback_query_handler(route_trainees, mentor_callback.filter(), is_admin=True)
