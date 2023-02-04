from datetime import datetime
from typing import Optional, Union, Dict, Any

from sqlalchemy.orm import sessionmaker

from app.models.views import UserView
from app.models.user import User
from app.models.exam import Exam


class ExamWrapper:
    document: str = None
    user: Union[int, str] = None
    stage_id: Union[int, str] = None
    result_id: Union[int, str] = None
    score: float = None
    exam_date: Union[datetime.date, str] = None
    retake_date: Union[datetime.date, None] = None
    calls: str = None
    exam_id: Union[int, str] = None
    wrapper: str = None

    def __init__(self, data: Union[Dict[str, Any], str], db: sessionmaker):
        self.db = db
        self.data = data
        if isinstance(self.data, str):
            self.user = self.data
        if isinstance(self.data, Dict):
            self.document = self.data['document']
            self.stage_id = self.data['stage_id']
            self.result_id = self.data['result_id']

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        del self

    async def _get_data(self):
        if isinstance(self.data, Dict):
            async with self.db.begin() as session:
                session.add(
                    Exam(
                        document_id=self.document,
                        user_id=self.data['user_id'],

                    )
                )

    async def _get_wrapper(self):

        for key, value in self.data.items():
            if value is None:
                self.data[key] = '-'

        wrapper = f'<b>{self.data["fullname"]}</b>\n' \
                  f'Формат опроса - {self.data["stage"]}\n' \
                  f'Статус аттестации - {self.data["result"]}\n' \
                  f'Набрано баллов - {self.data["score"]}\n' \
                  f'Ссылка YT: {self.data["link"]}\n'

        if self.data['result_id'] == 3 and self.data['stage_id'] == 3:
            wrapper += f'Звонки: \n{self.data["calls"]}'

        if self.data['result_id'] == 2:
            wrapper += f'Дата переаттестации - {self.data["retake_date"]}'

        if self.data['result_id'] == 1:
            wrapper += f'<i>Последняя аттестация. Увольнение сотрудника</i>\n'

        # self.document = self.data['document_id']
        # self.wrapper = wrapper
        # self.exam_id = self.data['id']
        # self.stage_id = self.data['stage_id']
        # self.result_id = self.data['result_id']

        # return {"document": data['document_id'], "wrapper": wrapper, "exam_id": data['id'],
        #         "stage_id": data['stage_id'],
        #         "result_id": data['result_id']}

    @staticmethod
    async def user_wrapper(user_info: UserView) -> dict:
        active = 'Активирован' if user_info.active == 1 else 'Деактивирован'
        wrapper = f'<b>{user_info.fullname}</b> {user_info.username}\n' \
                  f'Команда: {user_info.team or "-"}\n' \
                  f'<u>{active}</u>\n\n' \
                  f'Должность: {user_info.role}\n' \
                  f'Город: {user_info.city}\n'

        if user_info.role_id in (9, 10, 11):
            wrapper += f'Мед. образование: {user_info.traineeship}\n\n'

        elif user_info.role_id in (5, 6, 7, 8):
            wrapper += f'Ординатура: {user_info.traineeship}\n'
            if user_info.traineeship != "Не планирует поступать":
                wrapper += f'Специальность: {user_info.profession}\n' \
                           f'Год поступления: {user_info.start_year}\n' \
                           f'Год выпуска: {user_info.end_year}\n\n'

        wrapper += f'Контактный телефон: {user_info.phone_number}\n' \
                   f'e-mail: {user_info.email}'
        return {"wrapper": wrapper, "user_id": user_info.id, "active_id": user_info.active}

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


class Wrappers:
    pass
