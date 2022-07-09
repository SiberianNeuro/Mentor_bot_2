from loguru import logger

from app.models.google_api import google_api

from datetime import date, timedelta, datetime


async def add_user_array(user_info: tuple, mentor_name: str):

    fullname, username = user_info[1:3]
    city, stage = user_info[4:6]
    profession = f'Специальность: {user_info[6]}\n' \
                 f'Год поступления: {user_info[7]}\n' \
                 f'Год выпуска: {user_info[8]}'
    phone, email, role_id = user_info[9:]

    mentor_fullname = mentor_name.split(' ')
    mentor_shortname = f'{mentor_fullname[0]} {mentor_fullname[1][0]}.{mentor_fullname[2][0]}.'
    service = google_api()

    spreadsheet_id = "1SNA51rlReIonDCVryC_T3v0wzhU0QrMBfoL_Kxq3Z6w"
    range = "'Стажировка 2.0'!A3:K3" if role_id == 8 else "'Обучение 1-ая линия 2.0'!A3:H3"
    workday_duration = "10:30-17:00" if stage == "Учится сейчас" else "08:30-17:00"
    delta = (date.today() + timedelta(days=30)) if role_id == 8 else (date.today() + timedelta(days=15))

    values = [[
        fullname,
        username,
        phone,
        mentor_shortname,
        city,
        "медицинский консультант",
        stage,
        profession,
        workday_duration,
        date.today().strftime('%d.%m.%Y'),
        delta.strftime('%d.%m.%Y')
    ]] if role_id == 8 else [[
        fullname, username, phone, city, stage, date.today().strftime('%d.%m.%Y'), delta.strftime('%d.%m.%Y')
    ]]

    body = {
        'majorDimension': "ROWS",
        'values': values
    }

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range, body=body, valueInputOption="USER_ENTERED"
    ).execute()

    logger.log(
        'GOOGLE',
        '{0} cells appended to {1}: {2}'.format(result.get('updates').get('updatedCells'), range, str(*values))
    )
