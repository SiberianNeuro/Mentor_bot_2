from aiogram import types
from loader import bot
from app.keyboards import admin_kb
from app.keyboards.admin_kb import get_delete_button
import datetime

async def report_wrapper(data, m: types.Message):
    data = data[0]
    if data[4] == "Аттестация пройдена ✅" and data[8] == None:
        await m.answer_document(data[1],
            caption=f'<b>{data[2]}</b>\n'
                    f'Формат опроса - {data[3]}\n'
                    f'Статус аттестации - {data[4]}\n'
                    f'Набрано баллов - {data[5]}\n'
                    f'Ссылка YT: {data[6]}',
            reply_markup=get_delete_button(data[0])
        )
        await m.answer('Мы закончили, мы молодцы 👌', reply_markup=admin_kb.button_case_admin)
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
            reply_markup=get_delete_button(data[0])
        )
        await m.answer('Мы закончили, мы молодцы 👌', reply_markup=admin_kb.button_case_admin)
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
    elif data[4] == "Аттестация не пройдена ❌" and data[8] != None:
        await m.answer_document(data[1],
                                caption=f'<b>{data[2]}</b>\n'
                                        f'Формат опроса - {data[3]}\n'
                                        f'Статус аттестации - {data[4]}\n'
                                        f'Набрано баллов - {data[5]}\n'
                                        f'Дата переаттестации - {data[8].strftime("%d.%m.%Y")}\n'
                                        f'Ссылка YT: {data[6]}',
                                reply_markup=get_delete_button(data[0])
                                )
        await m.answer('Мы закончили, мы молодцы 👌', reply_markup=admin_kb.button_case_admin)
        await bot.send_document(
            -1001776821827, data[1],
            caption=f'{data[2]}\n'
                    f'Формат опроса: {data[3]}\n'
                    f'Статус аттестации: {data[4]}\n'
                    f'Дата переаттестации - {data[8].datetime.strftime("%d.%m.%Y")}\n'
                    f'Ссылка YT: {data[6]}'
        )

async def search_wrapper(resp, m: types.Message):
    for data in resp:
        if data[4] == "Аттестация пройдена ✅" and data[8] == None:
            await m.answer_document(data[1],
                                    caption=f'<b>{data[2]}</b>\n'
                                            f'Формат опроса - {data[3]}\n'
                                            f'Статус аттестации - {data[4]}\n'
                                            f'Набрано баллов - {data[5]}\n'
                                            f'Ссылка YT: {data[6]}',
                                    reply_markup=get_delete_button(data[0])
                                    )
        elif data[4] == "Аттестация не пройдена ❌" and data[8] == None:
            await m.answer_document(data[1],
                                    caption=f'<b>{data[2]}</b>\n'
                                            f'Формат опроса - {data[3]}\n'
                                            f'Статус аттестации - {data[4]}\n'
                                            f'Набрано баллов - {data[5]}\n'
                                            f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
                                            f'Ссылка YT: {data[6]}',
                                    reply_markup=get_delete_button(data[0])
                                    )
        elif data[4] == "Аттестация не пройдена ❌" and data[8] != None:
            await m.answer_document(data[1],
                                    caption=f'<b>{data[2]}</b>\n'
                                            f'Формат опроса - {data[3]}\n'
                                            f'Статус аттестации - {data[4]}\n'
                                            f'Набрано баллов - {data[5]}\n'
                                            f'Дата переаттестации - {data[8].strftime("%d.%m.%Y")}\n'
                                            f'Ссылка YT: {data[6]}',
                                    reply_markup=get_delete_button(data[0])
                                    )