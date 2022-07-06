from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from loguru import logger

from app.db.mysql_db import exam_processing, search_exam
from app.utils.misc.wrappers import report_wrapper, search_wrapper
from app.keyboards.other_kb import get_cancel_button
from app.keyboards.admin_kb import *
from app.utils.states import Exam
from app.utils.misc.file_parsing import file_parser


# Команда входа в админку
# @dp.message_handler(IsAdmin(), commands=['moderator'], state="*")
async def admin_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(f'Приветствую тебя, обучатор! 🦾\n\n'
                    f'Что я умею:\n\n'
                    f'👉🏻 Нажми на кнопку <b>"Загрузить"</b>, чтобы передать мне информацию о прошедшей аттестации\n'
                    f'👉🏻 Нажми кнопку <b>"Найти"</b>, чтобы найти информацию о предыдущих аттестациях\n'
                         f'👉🏻 Нажми кнопку <b>"Рассылка"</b>, если нужна помощь в рассылке тестов',
                         reply_markup=await get_admin_kb())
    await message.delete()
    await message.bot.set_my_commands([
        types.BotCommand('moderator', 'Вернуться в админ-панель')
    ])

"""Загрузка опроса"""


# Начало загрузки опроса: документ
# @dp.message_handler(IsAdmin(), Text(equals='Загрузить ⏏'), state=None)
async def exam_start(m: types.Message):
    await Exam.document.set()
    await m.answer('<b>Начинаем загрузку результатов аттестации</b>\n'
                   'Чтобы выйти из режима загрузки, нажми кнопку <b>"Отмена"</b> или напиши /moderator',
                   reply_markup=await get_cancel_button())
    await m.answer('Сейчас тебе нужно прислать мне протокол опроса 📜')


# Загрузка документа, парсинг документа, переход к выбору формата опроса
# @dp.message_handler(IsAdmin(), content_types=['document'], state=FSMAdmin.document)
async def load_document(m: types.Message, state: FSMContext):
    source: tuple = await file_parser(m.document.file_id, m.document.file_name)

    if source == 0:
        await m.answer("Я не распознал протокол.\n\nПроверь, актуальным ли протоколом ты пользуешься.\n"
                       "Если нет, то узнай у руководителя актуальную версю, перепиши результаты туда, и снова отправь мне.")
    elif source == 1:
        await m.answer("Я не нашел итоговое количество баллов.\n\nВнимательно посмотри, заполнил ли ты их. Если не заполнил - "
                       "заполняй и присылай мне протокол повторно.")
    elif source == 3:
        await m.answer("Поле 'Дата проведения проф.опроса' заполнено некорректно.\n\nПожалуйста, введи дату в формате "
                       "<i>ДД.ММ.ГГГГ</i> и пришли мне повторно.")
    elif source == 4:
        await m.answer("Не заполнено поле 'Дата проведения проф.опроса'.\n\nЗаполни его, пожалуйста, и пришли мне снова.")
    elif source == 5:
        await m.answer("Неверно заполнено поле даты переаттестации.\n\nПожалуйста, введи дату в формате "
                       "<i>ДД.ММ.ГГГГ</i> и пришли мне повторно. ")
    elif source == 6:
        await m.answer("Не распознал расширение протокола. Я кушаю протоколы только в формате .docx")
    elif source == 7:
        await m.answer('Я не нашел такого стажера в базе данных. Проверь, пожалуйста, правильно ли заполнено ФИО.\n\n'
                       'Если все правильно, уточни у стажера, проходил ли он у меня регистрацию.')

    else:
        fullname, user_id, stage_id, result_id, score, exam_date = source[:6]
        try:
            retake_date = source[6].strftime("%d.%m.%Y")
        except AttributeError:
            retake_date = "-"
        retake_date_to_sql = source[6]

        await state.update_data(
            document=m.document.file_id,
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
        await m.answer(f'Что получилось на выходе:\n\n'
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
async def confirm_document(c: types.CallbackQuery, callback_data: dict):
    await c.answer()
    if int(callback_data.get('action_data')) == 1:
        await c.message.answer('Хорошо, тогда мне нужна ссылка на YouTube ⏩\n'
                               'Если ссылок много, то пришли их через Ctrl+Enter')
        await Exam.link.set()
    else:
        await c.message.answer('Хорошо, тогда жду документ 📜')
        await Exam.document.set()


# Загрузка ссылки, обёртка результатов загрузки
# @dp.message_handler(IsAdmin(), state=FSMAdmin.link)
async def load_link(m: types.Message, state: FSMContext):
    await state.update_data(link=m.text)
    to_sql = await state.get_data()
    wrapper = await exam_processing(to_sql)
    logger.log('DATABASE', f'@{m.from_user.username} внес результаты опроса в базу данных.')
    await report_wrapper(wrapper, m=m)
    await state.finish()


# Команда на удаление опроса
# @dp.callback_query_handler(IsAdmin(), exam_callback.filter(action='delete'))
async def del_callback_run(c: types.CallbackQuery, callback_data: dict):
    await mysql_db.delete_exam(callback_data.get("action_data"))
    logger.info(f'@{c.from_user.username} удалил(-а) запись аттестации.')
    await c.answer(text='Информация удалена', show_alert=True)
    await c.message.delete()


"""Старт поиска по базе опросов"""


# Начало поиска: запрос ФИО
# @dp.message_handler(IsAdmin(), Text(equals='Найти 👀'), state=None)
async def start_search(message: types.Message):
    await message.reply('👇🏼 Введи Ф.И.О. сотрудника полностью или по отдельности',
                            reply_markup=await get_cancel_button())
    await Exam.trainee_name.set()


# Поиск ФИО по БД, вывод результатов
# @dp.message_handler(IsAdmin(), state=FSMAdmin.trainee_name)
async def search_item(m: types.Message, state: FSMContext):
    read = await search_exam(m.text.title())
    logger.info(f'{m.from_user.username} выполнил поиск опросов по запросу {m.text.title()}')
    if not read:
        await m.answer('Информации об этом сотруднике нет 🤔',
                               reply_markup=await get_admin_kb())
    else:
        await search_wrapper(read, m=m)
        await m.answer('Готово!👌', reply_markup=await get_admin_kb())
    await state.finish()


def setup(dp: Dispatcher):
    dp.register_message_handler(admin_start, is_admin=True, commands=['moderator'])
    dp.register_message_handler(exam_start, Text(equals='Загрузить ⏏'), is_admin=True)
    dp.register_message_handler(load_document, content_types=['document'], state=Exam.document, is_admin=True)
    dp.register_callback_query_handler(confirm_document, exam_callback.filter(action='overload'), state=Exam.confirm, is_admin=True)
    dp.register_message_handler(load_link, is_admin=True, state=Exam.link)
    dp.register_callback_query_handler(del_callback_run, exam_callback.filter(action='delete'), is_admin=True)
    dp.register_message_handler(start_search, Text(equals='Найти 👀'), is_admin=True)
    dp.register_message_handler(search_item, is_admin=True, state=Exam.trainee_name)
