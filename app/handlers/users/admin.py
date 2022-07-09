from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from loguru import logger

from app.db.mysql_db import exam_processing, db_search_exam, delete_exam, get_user_info
from app.utils.misc.wrappers import report_wrapper, search_wrapper, user_wrapper
from app.keyboards.other_kb import get_cancel_button
from app.keyboards.admin_kb import *
from app.utils.states import Exam
from app.utils.misc.file_parsing import file_parser


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
    await msg.bot.set_my_commands([
        types.BotCommand('moderator', 'Вернуться в админ-панель')
    ])

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
                       "Если нет, то узнай у руководителя актуальную версю, перепиши результаты туда, и снова отправь мне.")
    elif source == 1:
        await msg.answer("Я не нашел итоговое количество баллов.\n\nВнимательно посмотри, заполнил ли ты их. Если не заполнил - "
                       "заполняй и присылай мне протокол повторно.")
    elif source == 3:
        await msg.answer("Поле 'Дата проведения проф.опроса' заполнено некорректно.\n\nПожалуйста, введи дату в формате "
                       "<i>ДД.ММ.ГГГГ</i> и пришли мне повторно.")
    elif source == 4:
        await msg.answer("Не заполнено поле 'Дата проведения проф.опроса'.\n\nЗаполни его, пожалуйста, и пришли мне снова.")
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
        retake_date_to_sql = source[6]

        await state.update_data(
            document=msg.document.file_id,
            user_id=user_id,
            stage_id=stage_id,
            result_id=result_id,
            score=score,
            exam_date=exam_date,
            retake_date=retake_date_to_sql
        )
        stages = ["Опрос на 3-й день", "Опрос в середине цикла обучения", "Опрос на И.О.", "Опрос на врача", "Аттестация стажера L1"]
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
async def confirm_document(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    if int(callback_data.get('action_data')) == 1:
        await call.message.answer('Хорошо, тогда мне нужна ссылка на YouTube ⏩\n'
                               'Если ссылок много, то пришли их через Ctrl+Enter')
        await Exam.link.set()
    else:
        await call.message.answer('Хорошо, тогда жду документ 📜')
        await Exam.document.set()


# Загрузка ссылки, обёртка результатов загрузки
# @dp.message_handler(IsAdmin(), state=FSMAdmin.link)
async def load_link(msg: types.Message, state: FSMContext):
    await state.update_data(link=msg.text)
    to_sql = await state.get_data()
    wrapper = await exam_processing(to_sql)
    logger.log('DATABASE', f'@{msg.from_user.username} внес результаты опроса в базу данных.')
    await report_wrapper(wrapper, msg=msg)
    await state.finish()


# Команда на удаление опроса
# @dp.callback_query_handler(IsAdmin(), exam_callback.filter(action='delete'))
async def del_callback_run(call: types.CallbackQuery, callback_data: dict):
    await delete_exam(callback_data.get("action_data"))
    logger.info(f'@{call.from_user.username} удалил(-а) запись аттестации.')
    await call.answer(text='Информация удалена', show_alert=True)
    await call.message.delete()


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
    logger.info(f'{msg.from_user.username} выполнил поиск опросов по запросу {msg.text.title()}')


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
            await msg.answer(f'{user_data[1]}')
        await msg.answer('Готово!👌', reply_markup=await get_admin_kb())
    await state.finish()
    logger.info(f'{msg.from_user.username} выполнил поиск сотрудников по запросу {msg.text.title()}')


def setup(dp: Dispatcher):
    dp.register_message_handler(admin_start, is_admin=True, commands=['moderator'], chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(exam_start, Text(equals='Загрузить опрос ⏏'), is_admin=True, chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(cancel_handler_admin, state='*', commands='отмена')
    dp.register_message_handler(cancel_handler_admin, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(load_document, content_types=['document'], state=Exam.document, is_admin=True)
    dp.register_callback_query_handler(confirm_document, exam_callback.filter(action='overload'), state=Exam.confirm, is_admin=True)
    dp.register_message_handler(load_link, is_admin=True, state=Exam.link)
    dp.register_callback_query_handler(del_callback_run, exam_callback.filter(action='delete'), is_admin=True)
    dp.register_message_handler(exam_search_start, Text(equals='Найти опрос 👀'), is_admin=True, chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(exam_search_result, is_admin=True, state=Exam.exam_searching)
    dp.register_message_handler(employee_search_start, Text(equals='Найти сотрудника 👨‍⚕'), is_admin=True, chat_type=types.ChatType.PRIVATE)
    dp.register_message_handler(employee_search_result, is_admin=True, state=Exam.user_searching)