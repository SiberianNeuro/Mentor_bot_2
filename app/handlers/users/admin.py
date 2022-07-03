from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from app.db.mysql_db import get_user_id
from app.utils.misc.wrappers import report_wrapper, search_wrapper

from app.filters.admin import IsAdmin
from app.db import mysql_db
from app.keyboards.other_kb import get_cancel_button
from app.keyboards.admin_kb import *
from app.utils.states import FSMAdmin
from app.utils.misc.file_parsing import file_parser


# Команда входа в админку
async def admin_start(message: types.Message, state: FSMContext):
    await message.bot.set_my_commands([
        types.BotCommand('moderator', 'Вернуться в админ-панель'),
        types.BotCommand('mailing', 'Рассылка тестов')
    ])
    await state.finish()
    await message.answer(f'Приветствую тебя, обучатор! 🦾\n\n'
                    f'Что я умею:\n\n'
                    f'👉🏻 Нажми на кнопку <b>"Загрузить"</b>, чтобы передать мне информацию о прошедшей аттестации\n'
                    f'👉🏻 Нажми кнопку <b>"Найти"</b>, чтобы найти информацию о предыдущих аттестациях',
                         reply_markup=await get_admin_kb())
    await message.delete()

"""Загрузка опроса"""


# Начало загрузки опроса: документ
async def exam_start(m: types.Message):
    await FSMAdmin.document.set()
    await m.answer('<b>Начинаем загрузку результатов аттестации</b>\n'
                   'Чтобы выйти из режима загрузки, нажми кнопку <b>"Отмена"</b> или напиши /moderator',
                   reply_markup=await get_cancel_button())
    await m.answer('Сейчас тебе нужно прислать мне протокол опроса 📜')

# Загрузка документа, парсинг документа, переход к выбору формата опроса
async def load_document(m: types.Message, state: FSMContext):
    source: tuple = await file_parser(m.document.file_id, m.document.file_name)
    if source == 0:
        await m.answer("Я не распознал протокол. Проверь, актуальным ли протоколом ты пользуешься.\n"
                       "Если нет, то узнай у руководителя актуальную версю, перепиши результаты туда, и снова отправь мне.")
    elif source == 1:
        await m.answer("Я не нашел итоговое количество баллов. Внимательно посмотри, заполнил ли ты их. Если не заполнил - "
                       "заполняй и присылай мне протокол повторно.")
    elif source == 3:
        await m.answer("Поле 'Дата проведения проф.опроса' заполнено некорректно. Пожалуйста, введи дату в формате "
                       "<i>ДД.ММ.ГГГГ</i> и пришли мне повторно.")
    elif source == 4:
        await m.answer("Не заполнено поле 'Дата проведения проф.опроса'. Заполни его, пожалуйста, и пришли мне снова.")
    elif source == 5:
        await m.answer("Неверно заполнено поле даты переаттестации. Пожалуйста, введи дату в формате "
                       "<i>ДД.ММ.ГГГГ</i> и пришли мне повторно. ")
    else:
        fullname, stage_id, result_id, score, exam_date = source[:5]
        try:
            retake_date = source[5].strftime("%d.%m.%Y")
        except AttributeError:
            retake_date = "-"
        retake_date_to_sql = source[5]
        user_id = await get_user_id(fullname.strip())
        if user_id == ():
            await m.answer('Я не нашел такого стажера в базе данных. Проверь, пожалуйста, правильно ли заполнено ФИО.\n\n'
                           'Если все правильно, уточни у стажера, проходил ли он у меня регистрацию.')
        else:
            await state.update_data(
                document=m.document.file_id,
                user_id=user_id[0][0],
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
            await FSMAdmin.confirm.set()


async def confirm_document(c: types.CallbackQuery, callback_data: dict):
    await c.answer()
    if int(callback_data.get('action_data')) == 1:
        await c.message.answer('Хорошо, тогда мне нужна ссылка на YouTube ⏩\n'
                               'Если ссылок много, то пришли их через Ctrl+Enter')
        await FSMAdmin.link.set()
    else:
        await c.message.answer('Хорошо, тогда жду документ 📜')
        await FSMAdmin.document.set()


# Загрузка ссылки, обёртка результатов загрузки
async def load_link(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = m.text
        if data['result_id'] == 3 and data['stage_id'] in (3, 4, 5):
            await mysql_db.get_raise_user(data['user_id'])
    await mysql_db.append_exam(state)
    read = await mysql_db.item_search(data["document"])
    await report_wrapper(read, m=m)
    await state.finish()


# Команда на удаление опроса
async def del_callback_run(c: types.CallbackQuery, callback_data: dict):
    await mysql_db.sql_delete_command(callback_data.get("action_data"))
    await c.answer(text='Информация удалена', show_alert=True)
    await c.message.delete()


"""Старт поиска по базе опросов"""


# Начало поиска: запрос ФИО
async def start_search(message: types.Message):
    await message.reply('👇🏼 Введи Ф.И.О. сотрудника полностью или по отдельности',
                            reply_markup=await get_cancel_button())
    await FSMAdmin.trainee_name.set()


# Поиск ФИО по БД, вывод результатов
async def search_item(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['trainee_name'] = m.text.title()
    read = await mysql_db.name_search(data['trainee_name'])
    if not read:
        await m.answer('Информации об этом сотруднике нет 🤔',
                               reply_markup=await get_admin_kb())
    else:
        await search_wrapper(read, m=m)
        await m.answer('Готово!👌', reply_markup=await get_admin_kb())
    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, IsAdmin(), commands=['moderator'], state="*")
    dp.register_message_handler(exam_start, IsAdmin(), Text(equals='Загрузить ⏏'), state=None)
    dp.register_message_handler(load_document, IsAdmin(), content_types=['document'], state=FSMAdmin.document)
    dp.register_callback_query_handler(confirm_document, IsAdmin(), exam_callback.filter(action='overload'), state=FSMAdmin.confirm)
    dp.register_message_handler(load_link, IsAdmin(), state=FSMAdmin.link)
    dp.register_callback_query_handler(del_callback_run, IsAdmin(), exam_callback.filter(action='delete'))
    dp.register_message_handler(start_search, IsAdmin(), Text(equals='Найти 👀'), state=None)
    dp.register_message_handler(search_item, IsAdmin(), state=FSMAdmin.trainee_name)
