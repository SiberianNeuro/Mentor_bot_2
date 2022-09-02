class Wrappers:

    @staticmethod
    async def exam_wrapper(data: dict) -> dict:
        for key, value in data.items():
            if value is None:
                data[key] = '-'

        wrapper = f'<b>{data["fullname"]}</b>\n'
        f'Формат опроса - {data["stage"]}\n'
        f'Статус аттестации - {data["result"]}\n'
        f'Набрано баллов - {data["score"]}\n'
        f'Ссылка YT: {data["link"]}\n'

        if data['result_id'] and data['stage_id'] == 3:
            wrapper += f'Звонки: \n{data["calls"]}'

        if data['result_id'] == 2:
            wrapper += f'Дата переаттестации - {data["retake_date"]}'

        if data['result_id'] == 1:
            wrapper += f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'

        return {"document": data['document_id'], "wrapper": wrapper, "exam_id": data['id']}

    @staticmethod
    async def user_wrapper(user_info: dict) -> dict:
        for key, value in user_info.items():
            if value is None:
                user_info[key] = '-'
        active = 'Активирован' if user_info['active'] == 1 else 'Деактивирован'
        wrapper = f'<b>{user_info["fullname"]}</b> {user_info["username"]}\n<u>{active}</u>\n\n' \
                  f'Должность: {user_info["name"]}\n' \
                  f'Город: {user_info["city"]}\n'

        if user_info["role_id"] in (9, 10, 11):
            wrapper += f'Мед. образование: {user_info["stage"]}\n\n'

        elif user_info["role_id"] in (5, 6, 7, 8):
            wrapper += f'Ординатура: {user_info["stage"]}\n' \
                       f'Специальность: {user_info["profession"]}\n' \
                       f'Год поступления: {user_info["start_year"]}\n' \
                       f'Год выпуска: {user_info["end_year"]}\n\n'

        wrapper += f'Контактный телефон: {user_info["phone"]}\n' \
                   f'e-mail: {user_info["email"]}'
        return {"wrapper": wrapper, "user_id": user_info['id'], "active_id": user_info['active']}

    @staticmethod
    async def welcome_wrapper(welcome_info: dict) -> str:
        wrapper = f'Теперь я покажу тебе необходимые telegram-группы 👻\n\n'

        if welcome_info['role_id'] != 12:
            wrapper += f'<b>{welcome_info["doctors_chat"]}</b>\n' \
                       f'Эта ссылка приведет тебя на канал, где общаются все наши доктора 🧑‍⚕\n\n' \
                       f'<b>{welcome_info["headmaster_chat"]}</b>\n' \
                       f'Эта ссылка приведет тебя в группу, где общаются все стажеры 😉'

        wrapper += f'<b>{welcome_info["mentor_chat"]}</b>\n' \
                   f'По этой ссылке ты попадешь в чат своей учебной группы 👩‍🎓\n' \
                   f'Твой наставник, {welcome_info["mentor_name"]} {welcome_info["mentor_username"]}, ' \
                   f'будет на связи с тобой всегда и по любым вопросам 🤩\n' \
                   f'Обязательно нажми на каждую ссылку, чтобы попасть чат 😇'

        return wrapper

#             await msg.answer_document(document_id,
#                                       caption=f'<b>{fullname}</b>\n'
#                                               f'Формат опроса - {stage}\n'
#                                               f'Статус аттестации - {result}\n'
#                                               f'Набрано баллов - {score}\n'
#                                               f'Ссылка YT: {link}\n'
#                                               f'Звонки: \n{calls}',
#                                       reply_markup=await get_delete_button(id)
#                                       )
#             await msg.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
#             if stage in ("Опрос на И.О.", "Опрос на врача", "Аттестация стажера L1"):
#                 await bot.send_document(
#                     -781832035, document_id,
#                     caption=f'<b>{fullname}</b>\nФормат опроса: {stage}\nСтатус аттестации: {result}\nСсылка YT: {link}\nЗвонки:\n{calls}'
#                 )
#             await bot.send_document(
#                 -1001776821827, document_id,
#                 caption=f'<b>{fullname}</b>\nФормат опроса: {stage}\nСтатус аттестации: {result}\nСсылка YT: {link}\nЗвонки:\n{calls}'
#             )
#         elif result == "Аттестация не пройдена ❌":
#             await msg.answer_document(document_id,
#                                       caption=f'<b>{fullname}</b>\n'
#                                               f'Формат опроса - {stage}\n'
#                                               f'Статус аттестации - {result}\n'
#                                               f'Набрано баллов - {score}\n'
#                                               f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
#                                               f'Ссылка YT: {link}',
#                                       reply_markup=await get_delete_button(id))
#             await msg.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
#             await bot.send_document(
#                 -781832035, document_id,
#                 caption=f'<b>{fullname}</b>\n'
#                         f'Формат опроса: {stage}\n'
#                         f'Статус аттестации: {result}\n'
#                         f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
#                         f'Ссылка YT: {link}'
#             )
#             await bot.send_document(
#                 -1001776821827, document_id,
#                 caption=f'<b>{fullname}</b>\n'
#                         f'Формат опроса: {stage}\n'
#                         f'Статус аттестации: {result}\n'
#                         f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
#                         f'Ссылка YT: {link}'
#             )
#         elif data[4] == "На пересдачу ⚠️":
#             await msg.answer_document(document_id,
#                                       caption=f'<b>{fullname}</b>\n'
#                                               f'Формат опроса - {stage}\n'
#                                               f'Статус аттестации - {result}\n'
#                                               f'Набрано баллов - {score}\n'
#                                               f'Дата переаттестации - {retake_date}\n'
#                                               f'Ссылка YT: {link}',
#                                       reply_markup=await get_delete_button(id)
#                                       )
#             await msg.answer('Мы закончили, мы молодцы 👌', reply_markup=await admin_kb.get_admin_kb())
#             await bot.send_document(
#                 -1001776821827, document_id,
#                 caption=f'<b>{fullname}</b>\n'
#                         f'Формат опроса: {stage}\n'
#                         f'Статус аттестации: {result}\n'
#                         f'Дата переаттестации - {retake_date}\n'
#                         f'Ссылка YT: {link}'
#             )
#
#
# async def search_wrapper(resp, msg: types.Message):
#     """
#         Оболочка для результатов опроса.
#         param: resp: результат запроса SQL
#         param: m: объект телеграм API - сообщение
#         """
#     for data in resp:
#         retake_date = data[8] if data[8] is not None else "-"
#         if data[4] == "Аттестация пройдена ✅":
#             await msg.answer_document(data[1],
#                                       caption=f'<b>{data[2]}</b>\n'
#                                               f'Формат опроса - {data[3]}\n'
#                                               f'Статус аттестации - {data[4]}\n'
#                                               f'Набрано баллов - {data[5]}\n'
#                                               f'Ссылка YT: {data[6]}\n'
#                                               f'Звонки: \n{data[7]}',
#                                       reply_markup=await get_delete_button(data[0])
#                                       )
#         elif data[4] == "Аттестация не пройдена ❌":
#             await msg.answer_document(data[1],
#                                       caption=f'<b>{data[2]}</b>\n'
#                                               f'Формат опроса - {data[3]}\n'
#                                               f'Статус аттестации - {data[4]}\n'
#                                               f'Набрано баллов - {data[5]}\n'
#                                               f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'
#                                               f'Ссылка YT: {data[6]}',
#                                       reply_markup=await get_delete_button(data[0])
#                                       )
#         elif data[4] == "На пересдачу ⚠️":
#             await msg.answer_document(data[1],
#                                       caption=f'<b>{data[2]}</b>\n'
#                                               f'Формат опроса - {data[3]}\n'
#                                               f'Статус аттестации - {data[4]}\n'
#                                               f'Набрано баллов - {data[5]}\n'
#                                               f'Дата переаттестации - {retake_date}\n'
#                                               f'Ссылка YT: {data[6]}',
#                                       reply_markup=await get_delete_button(data[0])
#                                       )
