from aiogram import types

from app.db.mysql_db import get_user
from loader import bot
from app.keyboards import admin_kb
from app.keyboards.admin_kb import get_delete_button
import datetime


async def report_wrapper(data: tuple, m: types.Message):
    """
    Оболочка для результатов опроса.
    param: data: результат запроса SQL
    param: m: объект телеграм API - сообщение
    """
    data = data[0]
    if data[4] == "Аттестация пройдена ✅" and data[7] == None:
        await m.answer_document(data[1],
            caption=f'<b>{data[2]}</b>\n'
                    f'Формат опроса - {data[3]}\n'
                    f'Статус аттестации - {data[4]}\n'
                    f'Набрано баллов - {data[5]}\n'
                    f'Ссылка YT: {data[6]}',
            reply_markup=await get_delete_button(data[0])
        )
        await m.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
        await bot.send_document(
            -781832035, data[1],
            caption=f'{data[2]}\nФормат опроса: {data[3]}\nСтатус аттестации: {data[4]}\nСсылка YT: {data[6]}'
        )
        await bot.send_document(
            -1001776821827, data[1],
            caption=f'{data[2]}\nФормат опроса: {data[3]}\nСтатус аттестации: {data[4]}\nСсылка YT: {data[6]}'
        )
    elif data[4] == "Аттестация не пройдена ❌" and data[8] == None:
        await m.answer_document(data[1],
            caption=f'<b>{data[2]}</b>\n'
                    f'Формат опроса - {data[3]}\n'
                    f'Статус аттестации - {data[4]}\n'
                    f'Набрано баллов - {data[5]}\n'
                    f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
                    f'Ссылка YT: {data[6]}',
            reply_markup=await get_delete_button(data[0])
        )
        await m.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
        await bot.send_document(
            -781832035, data[1],
            caption=f'{data[2]}\n'
                    f'Формат опроса: {data[3]}\n'
                    f'Статус аттестации: {data[4]}\n'
                    f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
                    f'Ссылка YT: {data[6]}'
        )
        await bot.send_document(
            -1001776821827, data[1],
            caption=f'{data[2]}\n'
                    f'Формат опроса: {data[3]}\n'
                    f'Статус аттестации: {data[4]}\n'
                    f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
                    f'Ссылка YT: {data[6]}'
        )
    elif data[4] == "На пересдачу ⚠️":
        await m.answer_document(data[1],
                                caption=f'<b>{data[2]}</b>\n'
                                        f'Формат опроса - {data[3]}\n'
                                        f'Статус аттестации - {data[4]}\n'
                                        f'Набрано баллов - {data[5]}\n'
                                        f'Дата переаттестации - {data[7].strftime("%d.%m.%Y")}\n'
                                        f'Ссылка YT: {data[6]}',
                                reply_markup=await get_delete_button(data[0])
                                )
        await m.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
        await bot.send_document(
            -1001776821827, data[1],
            caption=f'{data[2]}\n'
                    f'Формат опроса: {data[3]}\n'
                    f'Статус аттестации: {data[4]}\n'
                    f'Дата переаттестации - {data[7].datetime.strftime("%d.%m.%Y")}\n'
                    f'Ссылка YT: {data[6]}'
        )

async def search_wrapper(resp, m: types.Message):
    """
        Оболочка для результатов опроса.
        param: resp: результат запроса SQL
        param: m: объект телеграм API - сообщение
        """
    for data in resp:
        if data[4] == "Аттестация пройдена ✅":
            await m.answer_document(data[1],
                                    caption=f'<b>{data[2]}</b>\n'
                                            f'Формат опроса - {data[3]}\n'
                                            f'Статус аттестации - {data[4]}\n'
                                            f'Набрано баллов - {data[5]}\n'
                                            f'Ссылка YT: {data[6]}',
                                    reply_markup=await get_delete_button(data[0])
                                    )
        elif data[4] == "Аттестация не пройдена ❌":
            await m.answer_document(data[1],
                                    caption=f'<b>{data[2]}</b>\n'
                                            f'Формат опроса - {data[3]}\n'
                                            f'Статус аттестации - {data[4]}\n'
                                            f'Набрано баллов - {data[5]}\n'
                                            f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
                                            f'Ссылка YT: {data[6]}',
                                    reply_markup=await get_delete_button(data[0])
                                    )
        elif data[4] == "На пересдачу ⚠️":
            await m.answer_document(data[1],
                                    caption=f'<b>{data[2]}</b>\n'
                                            f'Формат опроса - {data[3]}\n'
                                            f'Статус аттестации - {data[4]}\n'
                                            f'Набрано баллов - {data[5]}\n'
                                            f'Дата переаттестации - {data[7].strftime("%d.%m.%Y")}\n'
                                            f'Ссылка YT: {data[6]}',
                                    reply_markup=await get_delete_button(data[0])
                                    )

async def user_wrapper(name):
    user = await get_user(name)
    if user[3] == "Врач-стажер":
        string = f'<b>{user[1]}</b> {user[2]}\n' \
                 f'Должность: {user[3]}\n' \
                 f'Город: {user[4]}\n' \
                 f'Ординатура: {user[5]}\n' \
                 f'Специальность: {"-" if user[6] == None else user[6]}\n' \
                 f'Год поступления: {"-" if user[7] == None else user[7]}\n' \
                 f'Год выпуска: {"-" if user[8] == None else user[8]}\n' \
                 f'Номер телефона: {user[9]}' \
                 f'E-mail: {user[10]}'
    elif user[3] == "Стажер L1":
        string = f'<b>{user[1]}</b> {user[2]}\n' \
                 f'Должность: {user[3]}\n' \
                 f'Город: {user[4]}\n' \
                 f'Образование: {user[4]}\n' \
                 f'Номер телефона: {user[9]}\n' \
                 f'E-mail: {user[10]}'
    return string
