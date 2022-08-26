from aiogram import types

from loader import bot
from app.keyboards import admin_kb
from app.keyboards.admin_kb import get_delete_button


async def report_wrapper(data: tuple, msg: types.Message):
    """
    Оболочка для результатов опроса.
    param: data: результат запроса SQL
    param: m: объект телеграм API - сообщение
    """
    print(data)
    id, document_id, fullname, stage, result, score, link, calls = data[:8]
    retake_date = data[8] if data[8] is not None else "-"
    if result == "Аттестация пройдена ✅":
        await msg.answer_document(document_id,
                                  caption=f'<b>{fullname}</b>\n'
                                          f'Формат опроса - {stage}\n'
                                          f'Статус аттестации - {result}\n'
                                          f'Набрано баллов - {score}\n'
                                          f'Ссылка YT: {link}\n'
                                          f'Звонки: \n{calls}',
                                  reply_markup=await get_delete_button(id)
                                  )
        await msg.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
        if stage in ("Опрос на И.О.", "Опрос на врача", "Аттестация стажера L1"):
            await bot.send_document(
                -781832035, document_id,
                caption=f'<b>{fullname}</b>\nФормат опроса: {stage}\nСтатус аттестации: {result}\nСсылка YT: {link}\nЗвонки:\n{calls}'
            )
        await bot.send_document(
            -1001776821827, document_id,
            caption=f'<b>{fullname}</b>\nФормат опроса: {stage}\nСтатус аттестации: {result}\nСсылка YT: {link}\nЗвонки:\n{calls}'
        )
    elif result == "Аттестация не пройдена ❌":
        await msg.answer_document(document_id,
                                  caption=f'<b>{fullname}</b>\n'
                                          f'Формат опроса - {stage}\n'
                                          f'Статус аттестации - {result}\n'
                                          f'Набрано баллов - {score}\n'
                                          f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
                                          f'Ссылка YT: {link}',
                                  reply_markup=await get_delete_button(id))
        await msg.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
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
        await msg.answer_document(document_id,
                                  caption=f'<b>{fullname}</b>\n'
                                          f'Формат опроса - {stage}\n'
                                          f'Статус аттестации - {result}\n'
                                          f'Набрано баллов - {score}\n'
                                          f'Дата переаттестации - {retake_date}\n'
                                          f'Ссылка YT: {link}',
                                  reply_markup=await get_delete_button(id)
                                  )
        await msg.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
        await bot.send_document(
            -1001776821827, document_id,
            caption=f'<b>{fullname}</b>\n'
                    f'Формат опроса: {stage}\n'
                    f'Статус аттестации: {result}\n'
                    f'Дата переаттестации - {retake_date}\n'
                    f'Ссылка YT: {link}'
        )


async def search_wrapper(resp, msg: types.Message):
    """
        Оболочка для результатов опроса.
        param: resp: результат запроса SQL
        param: m: объект телеграм API - сообщение
        """
    for data in resp:
        retake_date = data[8] if data[8] is not None else "-"
        if data[4] == "Аттестация пройдена ✅":
            await msg.answer_document(data[1],
                                      caption=f'<b>{data[2]}</b>\n'
                                              f'Формат опроса - {data[3]}\n'
                                              f'Статус аттестации - {data[4]}\n'
                                              f'Набрано баллов - {data[5]}\n'
                                              f'Ссылка YT: {data[6]}\n'
                                              f'Звонки: \n{data[7]}',
                                      reply_markup=await get_delete_button(data[0])
                                      )
        elif data[4] == "Аттестация не пройдена ❌":
            await msg.answer_document(data[1],
                                      caption=f'<b>{data[2]}</b>\n'
                                              f'Формат опроса - {data[3]}\n'
                                              f'Статус аттестации - {data[4]}\n'
                                              f'Набрано баллов - {data[5]}\n'
                                              f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
                                              f'Ссылка YT: {data[6]}',
                                      reply_markup=await get_delete_button(data[0])
                                      )
        elif data[4] == "На пересдачу ⚠️":
            await msg.answer_document(data[1],
                                      caption=f'<b>{data[2]}</b>\n'
                                              f'Формат опроса - {data[3]}\n'
                                              f'Статус аттестации - {data[4]}\n'
                                              f'Набрано баллов - {data[5]}\n'
                                              f'Дата переаттестации - {retake_date}\n'
                                              f'Ссылка YT: {data[6]}',
                                      reply_markup=await get_delete_button(data[0])
                                      )


async def user_wrapper(user_data: dict):
    """

    :param user_data: собранные данные по пользователю
    :return: обработанные данные по пользователю
    """
    user_info = user_data
    user_id = user_info['id']
    active = 'Активирован' if user_info['active'] == 1 else 'Деактивирован'
    string = ''
    if user_info["role_id"] in (9, 10, 11):
        string = f'<b>{user_info["fullname"]}</b> {user_info["username"]}\n<u>{active}</u>\n\n' \
                 f'Должность: {user_info["name"]}\n' \
                 f'Город: {user_info["city"]}\n' \
                 f'Мед. образование: {user_info["stage"]}\n\n' \
                 f'Контактный телефон: {user_info["phone"]}\n' \
                 f'e-mail: {user_info["email"]}'
    elif user_info["role_id"] in (5, 6, 7, 8):
        string = f'<b>{user_info["fullname"]}</b> {user_info["username"]}\n<u>{active}</u>\n\n' \
                 f'Должность: {user_info["name"]}\n' \
                 f'Город: {user_info["city"]}\n' \
                 f'Ординатура: {user_info["stage"]}\n' \
                 f'Специальность: {user_info["profession"]}\n' \
                 f'Год поступления: {user_info["start_year"]}\n' \
                 f'Год выпуска: {user_info["end_year"]}\n\n' \
                 f'Контактный телефон: {user_info["phone"]}\n' \
                 f'e-mail: {user_info["email"]}'
    return string, user_id, user_info['active']
