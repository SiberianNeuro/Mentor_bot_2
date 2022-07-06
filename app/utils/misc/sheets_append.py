from loguru import logger

from app.models.google_api import google_api


async def add_user_array(state):
    prep = state

    service = google_api()

    spreadsheet_id = "1yEGI54xqiTVhdob6dReHhrQ0TG6XlQeXMhVE1V7cers"
    range = "Стажировка 2.0!A1:J1" if prep['role'] == 8 else "Обучение 1-ая линия 2.0!A1:J1"
    workday_duration = "10:30-17:00" if prep['traineeship'] == 3 else "8:30-17:00"

    values = [[
        prep['name'],
        prep['username'],
        prep['phone'],
        prep['city'],
        "медицинский консультант",
        prep['traineeship'],
        f"Специальность: {prep['profession']}\nГод поступления: {prep['start_year']}\nГод окончания: {prep['end_year']}",
        workday_duration
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
