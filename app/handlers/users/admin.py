from datetime import datetime, date

from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher

from app.utils.misc.exam_wrapper import report_wrapper, search_wrapper
from loader import dp, bot

from app.filters.admin import IsAdmin
from app.db import mysql_db
from app.keyboards import admin_kb
from app.keyboards.admin_kb import get_format_keyboard, get_status_keyboard, exam_callback
from app.utils.misc.states import FSMAdmin
from app.utils.misc.file_parsing import file_parser


# Команда входа в админку
async def admin_start(m: types.Message, state: FSMContext):
    await state.finish()
    await m.answer(f'Приветствую тебя, обучатор! 🦾\n\n'
                    f'Что я умею:\n\n'
                    f'👉🏻 Нажми на кнопку <b>"Загрузить"</b>, чтобы передать мне информацию о прошедшей аттестации\n'
                    f'👉🏻 Нажми кнопку <b>"Найти"</b>, чтобы найти информацию о предыдущих аттестациях',
                    reply_markup=admin_kb.button_case_admin)
    await m.delete()

"""Загрузка опроса"""


# Начало загрузки опроса: документ
async def exam_start(m: types.Message):
    await FSMAdmin.document.set()
    await m.answer('<b>Начинаем загрузку результатов аттестации</b>\n'
                   'Чтобы выйти из режима загрузки, нажми кнопку <b>"Отмена"</b> или напиши /moderator',
                   reply_markup=admin_kb.button_case_cancel
                   )
    await m.answer('Сейчас тебе нужно прислать мне протокол опроса 📜')


# Загрузка документа, парсинг документа, переход к выбору формата опроса
async def load_document(m: types.Message, state: FSMContext):
    source = await file_parser(m.document.file_id, m.document.file_name)
    async with state.proxy() as data:
        data['document'] = m.document.file_id
        data['score'] = source[0]
        data['fullname'] = source[1]
    await FSMAdmin.next()
    await m.answer(
        f'Давай-ка посмотрим:\n\nОпрошенный стажер - <b>{source[1]}</b>\n'
        f'А результат аттестации в баллах - <u>{source[0]}</u>\n\n'
        f'Если это неверно - срочно жми <b>"Отмена"</b> и перепроверяй файл!\n\n'
        f'Ну а если все в порядке - выбирай формат опроса ⬇️',
        reply_markup=get_format_keyboard()
    )


# Выбор формата опроса, переход к выбору итога аттестации
async def load_form(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    async with state.proxy() as data:
        data['form'] = callback_data.get("action_data")
    await FSMAdmin.next()
    await c.answer()
    await c.message.answer('Здорово! Теперь выбери, прошел ли сотрудник опрос:',
                           reply_markup=get_status_keyboard())


# Выбор итога аттестации, переход к загрузке ссылки
async def load_status(c: types.CallbackQuery, state: FSMContext, callback_data: dict):
    async with state.proxy() as data:
        data['status'] = callback_data.get("action_data")

        if data['status'] == 'Аттестация не пройдена ❌':
            await FSMAdmin.retake.set()
            await c.answer()
            await c.message.answer('Какая незадача 😔\n\nПожелаем ему удачи в другой раз :)')
            await c.message.answer('К слову, если аттестация не пройдена - надо установить дату следующей аттестации\n\n'
                                   'Пожалуйста, напиши мне её в формате <i>ДД.ММ.ГГГГ</i>\n\n'
                                   'Если это была последняя аттестация, напиши "увольнение"')

        else:
            data['retake'] = None
            await FSMAdmin.link.set()
            await c.answer()
            await c.message.answer('Еще одна успешная аттестация 😎\n\nНе забудь поздравить умничку 🙃')
            await c.message.answer('Мы почти закончили, осталась только ссылка на YouTube ⏩\n\n'
                                   'Скопируй её и пришли мне')


# Ловим дату переаттестации или сообщение об увольнении
async def load_retake(m: types.Message, state: FSMContext):
    retake_date = datetime.strptime(m.text, "%d.%m.%Y")
    async with state.proxy() as data:
        if m.text.lower() == 'увольнение':
            data['retake'] = None
            await FSMAdmin.link.set()
            await m.answer('Мы почти закончили, осталась только ссылка на YouTube ⏩\n\n'
                           'Скопируй её и пришли мне')
        else:
            assert retake_date > datetime.now(), await m.answer("Нельзя указывать сегодняшнюю или прошедшую дату.")
            try:
                data['retake'] = retake_date.strftime("%Y-%m-%d")
                await FSMAdmin.link.set()
                await m.answer('Мы почти закончили, осталась только ссылка на YouTube ⏩\n\n'
                               'Скопируй её и пришли мне')
            except ValueError:
                await m.answer("Это некорректная дата. Пожалуйста, введи дату по шаблону.")



# Загрузка ссылки, обёртка результатов загрузки
async def load_link(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = m.text
    await mysql_db.sql_add_command(state)
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
                            reply_markup=admin_kb.button_case_cancel)
    await FSMAdmin.trainee_name.set()


# Поиск ФИО по БД, вывод результатов
async def search_item(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['trainee_name'] = m.text.title()
    read = await mysql_db.name_search(data['trainee_name'])
    if not read:
        await bot.send_message(m.from_user.id, 'Информации об этом сотруднике нет 🤔',
                               reply_markup=admin_kb.button_case_admin)
    else:
        await search_wrapper(read, m=m)
        await bot.send_message(m.from_user.id, 'Готово!👌', reply_markup=admin_kb.button_case_admin)
    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, IsAdmin(), commands=['moderator'], state="*")
    dp.register_message_handler(exam_start, IsAdmin(), text='Загрузить', state=None)
    dp.register_message_handler(load_document, IsAdmin(), content_types=['document'], state=FSMAdmin.document)
    dp.register_callback_query_handler(load_form, IsAdmin(), exam_callback.filter(action='format'), state=FSMAdmin.form)
    dp.register_callback_query_handler(load_status, IsAdmin(), exam_callback.filter(action='status'), state=FSMAdmin.status)
    dp.register_message_handler(load_retake, IsAdmin(), state=FSMAdmin.retake)
    dp.register_message_handler(load_link, IsAdmin(), state=FSMAdmin.link)
    dp.register_callback_query_handler(del_callback_run, IsAdmin(), exam_callback.filter(action='delete'))
    dp.register_message_handler(start_search, IsAdmin(), text='Найти', state=None)
    dp.register_message_handler(search_item, IsAdmin(), state=FSMAdmin.trainee_name)
