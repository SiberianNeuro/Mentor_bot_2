from aiogram import types
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
    print(data)
    id, document_id, fullname, stage, result, score, link = data[:7]
    retake_date = data[7].strftime("%d.%m.%Y") if data[7] is not None else "-"
    if result == "Аттестация пройдена ✅":
        await m.answer_document(document_id,
            caption=f'<b>{fullname}</b>\n'
                    f'Формат опроса - {stage}\n'
                    f'Статус аттестации - {result}\n'
                    f'Набрано баллов - {score}\n'
                    f'Ссылка YT: {link}',
            reply_markup=await get_delete_button(id)
        )
        await m.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
        if stage in ("Опрос на И.О.", "Опрос на врача", "Аттестация стажера L1"):
            await bot.send_document(
                -781832035, document_id,
                caption=f'<b>{fullname}</b>\nФормат опроса: {stage}\nСтатус аттестации: {result}\nСсылка YT: {link}'
            )
        await bot.send_document(
            -1001776821827, document_id,
            caption=f'<b>{fullname}</b>\nФормат опроса: {stage}\nСтатус аттестации: {result}\nСсылка YT: {link}'
        )
    elif result == "Аттестация не пройдена ❌":
        await m.answer_document(document_id,
            caption=f'<b>{fullname}</b>\n'
                    f'Формат опроса - {stage}\n'
                    f'Статус аттестации - {result}\n'
                    f'Набрано баллов - {score}\n'
                    f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
                    f'Ссылка YT: {link}',
            reply_markup=await get_delete_button(id))
        await m.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
        await bot.send_document(
            -781832035, document_id,
            caption=f'<b>{fullname}</b>\n'
                    f'Формат опроса: {stage}\n'
                    f'Статус аттестации: {result}\n'
                    f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
                    f'Ссылка YT: {link}'
        )
        await bot.send_document(
            -1001776821827, document_id,
            caption=f'<b>{fullname}</b>\n'
                    f'Формат опроса: {stage}\n'
                    f'Статус аттестации: {result}\n'
                    f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
                    f'Ссылка YT: {link}'
        )
    elif data[4] == "На пересдачу ⚠️":
        await m.answer_document(document_id,
                                caption=f'<b>{fullname}</b>\n'
                                        f'Формат опроса - {stage}\n'
                                        f'Статус аттестации - {result}\n'
                                        f'Набрано баллов - {score}\n'
                                        f'Дата переаттестации - {retake_date}\n'
                                        f'Ссылка YT: {link}',
                                reply_markup=await get_delete_button(id)
                                )
        await m.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
        await bot.send_document(
            -1001776821827, document_id,
            caption=f'<b>{fullname}</b>\n'
                    f'Формат опроса: {stage}\n'
                    f'Статус аттестации: {result}\n'
                    f'Дата переаттестации - {retake_date}\n'
                    f'Ссылка YT: {link}'
        )

async def search_wrapper(resp, m: types.Message):
    """
        Оболочка для результатов опроса.
        param: resp: результат запроса SQL
        param: m: объект телеграм API - сообщение
        """
    for data in resp:
        retake_date = data[7].strftime("%d.%m.%Y") if data[7] is not None else "-"
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
                                            f'Дата переаттестации - {retake_date}\n'
                                            f'Ссылка YT: {data[6]}',
                                    reply_markup=await get_delete_button(data[0])
                                    )

async def user_wrapper():
    pass