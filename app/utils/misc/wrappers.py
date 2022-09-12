class Wrappers:

    @staticmethod
    async def exam_wrapper(data: dict) -> dict:
        for key, value in data.items():
            if value is None:
                data[key] = '-'

        wrapper = f'<b>{data["fullname"]}</b>\n' \
                  f'Формат опроса - {data["stage"]}\n' \
                  f'Статус аттестации - {data["result"]}\n' \
                  f'Набрано баллов - {data["score"]}\n' \
                  f'Ссылка YT: {data["link"]}\n'

        if data['result_id'] == 3 and data['stage_id'] == 3:
            wrapper += f'Звонки: \n{data["calls"]}'

        if data['result_id'] == 2:
            wrapper += f'Дата переаттестации - {data["retake_date"]}'

        if data['result_id'] == 1:
            wrapper += f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'

        return {"document": data['document_id'], "wrapper": wrapper, "exam_id": data['id'],
                "stage_id": data['stage_id'],
                "result_id": data['result_id']}

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

        mentor_chat_link = welcome_info['l1_chat'] if welcome_info['role_id'] == 12 else welcome_info['l3_chat']

        if welcome_info['role_id'] != 12:
            wrapper += f'<b>{welcome_info["doctors_chat"]}</b>\n' \
                       f'Эта ссылка приведет тебя на канал, где общаются все наши доктора 🧑‍⚕\n\n' \
                       f'<b>{welcome_info["headmaster_chat"]}</b>\n' \
                       f'Эта ссылка приведет тебя в группу, где общаются все стажеры 😉'

        wrapper += f'<b>{mentor_chat_link}</b>\n' \
                   f'По этой ссылке ты попадешь в чат своей учебной группы 👩‍🎓\n' \
                   f'Твой наставник, {welcome_info["mentor_name"]} {welcome_info["mentor_username"]}, ' \
                   f'будет на связи с тобой всегда и по любым вопросам 🤩\n' \
                   f'Обязательно нажми на каждую ссылку, чтобы попасть чат 😇'

        return wrapper
