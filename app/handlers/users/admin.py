from datetime import datetime, date

from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from app.db.mysql_db import get_user_id
from app.utils.misc.wrappers import report_wrapper, search_wrapper
from loader import dispatcher, bot

from app.filters.admin import IsAdmin
from app.db import mysql_db
from app.keyboards import admin_kb, other_kb
from app.keyboards.admin_kb import get_stage_keyboard, get_result_keyboard, exam_callback, get_overload_keyboard
from app.utils.misc.states import FSMAdmin
from app.utils.misc.file_parsing import file_parser


# Команда входа в админку
async def admin_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(f'Приветствую тебя, обучатор! 🦾\n\n'
                    f'Что я умею:\n\n'
                    f'👉🏻 Нажми на кнопку <b>"Загрузить"</b>, чтобы передать мне информацию о прошедшей аттестации\n'
                    f'👉🏻 Нажми кнопку <b>"Найти"</b>, чтобы найти информацию о предыдущих аттестациях',
                         reply_markup=await admin_kb.get_admin_kb())
    await message.delete()

"""Загрузка опроса"""


# Начало загрузки опроса: документ
async def exam_start(m: types.Message):
    await FSMAdmin.document.set()
    await m.answer('<b>Начинаем загрузку результатов аттестации</b>\n'
                   'Чтобы выйти из режима загрузки, нажми кнопку <b>"Отмена"</b> или напиши /moderator',
                   reply_markup=await other_kb.get_cancel_button())
    await m.answer('Сейчас тебе нужно прислать мне протокол опроса 📜')


# Загрузка документа, парсинг документа, переход к выбору формата опроса
async def load_document(m: types.Message, state: FSMContext):
    source: tuple = await file_parser(m.document.file_id, m.document.file_name)
    if source is None:
        await m.answer("Не смог прочитать протокол. Перепроверь, пожалуйста, правильность заполнения.\n\n"
                       "В шапке должны быть заполнены следующие поля:\n"
                       "-ФИО сотрудника;\n"
                       "-Дата опроса;\n"
                       "-Итоговое количество баллов;\n"
                       "-Плюсик у результата опроса и дата пересдачи, если сотрудник идет на пересдачу.")
    elif source == 0:
        await m.answer("Я не распознал протокол. Проверь, актуальным ли протоколом ты пользуешься.\n"
                       "Если нет, то узнай у руководителя актуальную версю, перепиши результаты туда, и снова отправь мне.")
    elif source == 1:
        await m.answer("Я не нашел итоговое количество баллов. Внимательно посмотри, заполнил ли ты их. Если не заполнил - "
                       "заполняй и присылай мне протокол повторно.")
    elif source == 2:
        await m.answer("Итоги аттестации некорректные. Проверь, всё ли ты заполнил в этой таблице. Как поправишь - "
                       "присылай мне протокол повторно.")
    elif source == 3:
        await m.answer("Поле 'Дата проведения проф.опроса' заполнено некорректно. Пожалуйста, введи дату в формате "
                       "<i>ДД.ММ.ГГГГ</i> и пришли мне повторно.")
    elif source == 4:
        await m.answer("Не заполнено поле 'Дата проведения проф.опроса'. Заполни его, пожалуйста, и пришли мне снова.")
    elif source == 5:
        await m.answer("Неверно заполнено поле даты переаттестации. Пожалуйста, введи дату в формате "
                       "<i>ДД.ММ.ГГГГ</i> и пришли мне повторно. ")
    else:
        fullname, stage_id, result_id, score, exam_date, retake_date = source
        user_id = await get_user_id(fullname.strip())
        if user_id is None:
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
                retake_date=retake_date
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
                           f'Дата переопроса: {retake_date.strftime("%d.%m.%Y")}\n\n'
                           f'Если что-то не так, проверь протокол и скинь еще раз. Если все хорошо,'
                           f'то жми кнопку "Подтвердить"', reply_markup=await get_overload_keyboard())



async def confirm_document(c: types.CallbackQuery):
    await c.answer()
    await c.message.answer('Хорошо, тогда мне нужна ссылка на YouTube ⏩\n'
                           'Если ссылок много, то пришли их через Ctrl+Enter')
    await FSMAdmin.link.set()

# Выбор формата опроса, переход к выбору итога аттестации
# async def load_form(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
#     async with state.proxy() as data:
#         data['form'] = int(callback_data.get("action_data"))
#     await FSMAdmin.next()
#     await c.answer()
#     await c.message.answer('Здорово! Теперь выбери, прошел ли сотрудник опрос:',
#                            reply_markup=await get_result_keyboard())
#
#
# # Выбор итога аттестации, переход к загрузке ссылки
# async def load_status(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
#     result = int(callback_data.get('action_data'))
#     print(result)
#         # Если это была последняя аттестация
#     if result == 1:
#         async with state.proxy() as data:
#             data['status'] = result
#             data['retake'] = None
#             await FSMAdmin.link.set()
#             await c.message.answer_sticker('CAACAgIAAxkBAAIPJmKb0CyQJ2lmgYrfoM6MIj_--ZzTAAJIAAOtZbwUgHOKzxQtAAHcJAQ')
#             await c.message.answer('Мы почти закончили, осталась только ссылка на YouTube ⏩\n\n'
#                                    'Скопируй её и пришли мне')
#             await c.answer()
#         # Если чел едет на пересдачу
#     elif result == 2:
#         async with state.proxy() as data:
#             data['status'] = result
#             await FSMAdmin.retake.set()
#             await c.message.answer('Какая незадача 😔\n\nПожелаем ему удачи в другой раз :)')
#             await c.message.answer('К слову, если аттестация не пройдена - надо установить дату следующей аттестации\n\n'
#                                    'Пожалуйста, напиши мне её в формате <i>ДД.ММ.ГГГГ</i>')
#             await c.answer()
#         # Если все четко
#     else:
#         async with state.proxy() as data:
#             data['status'] = result
#             data['retake'] = None
#             await FSMAdmin.link.set()
#             await c.message.answer('Еще одна успешная аттестация 😎\n\nНе забудь поздравить умничку 🙃')
#             await c.message.answer('Мы почти закончили, осталась только ссылка на YouTube ⏩\n\n'
#                                    'Скопируй её и пришли мне')
#             await c.answer()
#
# # Ловим дату переаттестации
# async def load_retake(m: types.Message, state: FSMContext):
#     try:
#         retake_date = datetime.strptime(m.text, "%d.%m.%Y")
#         assert retake_date <= date.today(), await m.answer("Нельзя указывать сегодняшнюю или прошедшую дату.")
#         async with state.proxy() as data:
#             data['retake'] = retake_date.strftime("%Y-%m-%d")
#             await FSMAdmin.link.set()
#             await m.answer('Мы почти закончили, осталась только ссылка на YouTube ⏩\n\n'
#                             'Скопируй её и пришли мне')
#
#     except ValueError:
#         await m.answer("Это некорректная дата. Пожалуйста, введи дату по шаблону.")



# Загрузка ссылки, обёртка результатов загрузки
async def load_link(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = m.text
        if data['result_id'] == 3 and data['stage_id'] in (3, 4):
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
                            reply_markup=await other_kb.get_cancel_button())
    await FSMAdmin.trainee_name.set()


# Поиск ФИО по БД, вывод результатов
async def search_item(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['trainee_name'] = m.text.title()
    read = await mysql_db.name_search(data['trainee_name'])
    if not read:
        await bot.send_message(m.from_user.id, 'Информации об этом сотруднике нет 🤔',
                               reply_markup=await admin_kb.get_admin_kb())
    else:
        await search_wrapper(read, m=m)
        await bot.send_message(m.from_user.id, 'Готово!👌', reply_markup=admin_kb.button_case_admin)
    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, IsAdmin(), commands=['moderator'], state="*")
    dp.register_message_handler(exam_start, IsAdmin(), Text(equals='Загрузить'), state=None)
    dp.register_message_handler(load_document, IsAdmin(), content_types=['document'], state=FSMAdmin.document)
    dp.register_callback_query_handler(confirm_document, IsAdmin(), exam_callback.filter(action='overload'), state=FSMAdmin.link)
    # dp.register_callback_query_handler(load_form, IsAdmin(), exam_callback.filter(action='format'), state=FSMAdmin.form)
    # dp.register_callback_query_handler(load_status, IsAdmin(), exam_callback.filter(action='result'), state=FSMAdmin.status)
    # dp.register_message_handler(load_retake, IsAdmin(), state=FSMAdmin.retake)
    dp.register_message_handler(load_link, IsAdmin(), state=FSMAdmin.link)
    dp.register_callback_query_handler(del_callback_run, IsAdmin(), exam_callback.filter(action='delete'))
    dp.register_message_handler(start_search, IsAdmin(), Text(equals='Найти'), state=None)
    dp.register_message_handler(search_item, IsAdmin(), state=FSMAdmin.trainee_name)