import urllib.request
import docx
from docx.opc.exceptions import PackageNotFoundError
import os
from datetime import datetime, date


from loader import config, bot

# Парсер для протоколов опроса
async def file_parser(fileid, filename):
    """

    :param fileid: ИД файла в телеге
    :param filename: имя файла в телеге
    :return: тапл из полного имени пользователя, айди формата опроса, айди результата опроса,
    баллы за опрос, дата опроса и дата пересдачи
    """

    file_info = await bot.get_file(fileid)
    fi = file_info.file_path
    name = filename
    urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{config.tg_bot.token}/{fi}',f'./{name}')

    try:
        d = docx.Document(filename)
    except PackageNotFoundError:
        os.remove(filename)
        return 6

    general_table = d.tables[0]
    retake_date = None
    if "Призывные мероприятия" in d.paragraphs[3].text:
        stage_id = 1
    elif "в середине теоретического цикла" in d.paragraphs[3].text:
        stage_id = 2
    elif "при аттестации" in d.paragraphs[3].text:
        stage_id = 3
    elif "при переводе" in d.paragraphs[3].text:
        stage_id = 4
    elif "при экзаменации" in d.paragraphs[3].text:
        stage_id = 5
    else:
        return 0  # Не распознал протокол опроса

    scores_table = d.tables[2] if stage_id == 3 else d.tables[1]
    results_table = d.tables[3] if stage_id == 3 else d.tables[2]
    general = []
    scores = []
    results = []

    for r in general_table.rows:
        general.append([cell.text for cell in r.cells])
    for r in scores_table.rows:
        scores.append([cell.text for cell in r.cells])
    for r in results_table.rows:
        results.append([cell.text for cell in r.cells])

    fullname = general[0][1]
    if stage_id == 4:
        score = 0.0
    else:
        score = scores[-1][2]
        if score == '':
            return 1  # Не нашел итоговое количество баллов
    if stage_id == 1:
        result_id = 3
    else:
        if results[-1][2] != "":
            result_id = 1
        elif results[-2][2] != "":
            result_id = 2
            try:
                retake_date = datetime.strptime(results[-2][3], "%d.%m.%Y")
            except ValueError:
                return 5 # Неверно записана дата переопроса
        else:
            result_id = 3
    if general[-1][1] != '':
        try:
            exam_date = datetime.strptime(general[-1][1], "%d.%m.%Y")
        except ValueError:
            return 3  # Неверно написана дата опроса
    else:
        return 4  # Нет даты опроса
    try:
        score = float(score.replace(',', '.'))
    except AttributeError:
        score = float(score)
    finally:
        os.remove(filename)
        return fullname, stage_id, result_id, score, exam_date, retake_date
