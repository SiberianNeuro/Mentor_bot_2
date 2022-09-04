from loguru import logger

from app.models.google_api import GoogleSheetsApi

from datetime import date, timedelta

from app.services.config import load_config

config = load_config('.env')


async def add_user_array(user_info: dict, mentor_name: str):
    fullname, username = user_info['fullname'], user_info['username']
    city, stage = user_info['city'], user_info['stage']
    profession = f'Специальность: {user_info["profession"]}\n' \
                 f'Год поступления: {user_info["start_year"]}\n' \
                 f'Год выпуска: {user_info["end_year"]}'
    phone, email, role_id = user_info['phone'], user_info['email'], user_info['role_id']

    mentor_fullname = mentor_name.split(' ')
    mentor_shortname = f'{mentor_fullname[0]} {mentor_fullname[1][0]}.{mentor_fullname[2][0]}.'
    api = GoogleSheetsApi(spreadsheet_id=config.misc.mentor_table,
                          spreadsheet_range="'Стажировка 2.0'!A3:L3"
                          if role_id == 8 else "'Обучение 1-ая линия 2.0'!A3:H3")

    workday_duration = "10:30-17:00" if stage == "Учится сейчас" else "08:30-17:00"
    delta = (date.today() + timedelta(days=30)) if role_id == 8 else (date.today() + timedelta(days=15))

    values = [[
        fullname,
        username,
        phone,
        email,
        mentor_shortname,
        city,
        "медицинский консультант",
        stage,
        profession,
        workday_duration,
        date.today().strftime('%d.%m.%Y'),
        delta.strftime('%d.%m.%Y')
    ]] if role_id == 8 else [[
        fullname, username, phone, email, city, stage, date.today().strftime('%d.%m.%Y'), delta.strftime('%d.%m.%Y')
    ]]

    api.append_values(values=values)
