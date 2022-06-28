import urllib.request
import docx
import os
from datetime import datetime

from loader import config, bot


async def file_parser(fileid, filename):
    """
    Скачиваем документ с сервера телеграма и парсим его
    param: fileid:  айдишник файла на сервере телеграм (не уникальный)
    param: filename: наименование файла на сервере телеграм
    param: with_retake: если стажер идет на пересдачу, дополнительно парсим дату пересдачи.
    По умолчанию не парсим.
    """
    file_info = await bot.get_file(fileid)
    fi = file_info.file_path
    name = filename
    urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{config.tg_bot.token}/{fi}',f'./{name}')

    d = docx.Document(filename)
    general_table = d.tables[0]
    if "Призывные мероприятия" in d.paragraphs[3].text:
        stage_id = 1
        scores_table = d.tables[1]
        result_id = 3
        retake_date = None
    elif "в середине теоретического цикла обучения" in d.paragraphs[3].text:
        stage_id = 2
        scores_table = d.tables[1]
        results_table = d.tables[2]
    elif "при аттестации" in d.paragraphs[3].text:
        stage_id = 3
        scores_table = d.tables[2]
        results_table = d.tables[3]
    elif "при переводе" in d.paragraphs[3].text:
        stage_id = 4
        score = 0.0
        results_table = d.tables[2]
    else:
        return 0

    general = []
    scores = []
    results = []

    for r in general_table.rows:
        general.append([cell.text for cell in r.cells])
    if stage_id != 4:
        for r in scores_table.rows:
            scores.append([cell.text for cell in r.cells])
    if stage_id != 1:
        for r in results_table.rows:
            results.append([cell.text for cell in r.cells])

    fullname = general[0][1]
    if stage_id != 4:
        score = scores[-1][2]
        if score == '':
            return 1
    elif stage_id != 1:
        if results[-1][2] != "":
            result_id = 1
            retake_date = None
        elif results[-2][2] != "":
            result_id = 2
            try:
                retake_date = datetime.strptime(results[-2][3], "%d.%m.%Y")
            except ValueError:
                return 5
        elif results[-3][2] != "" or results[-4][2] != "":
            result_id = 3
            retake_date = None
        else:
            return 2
    if general[-1][1] != '':
        try:
            exam_date = datetime.strptime(general[-1][1], "%d.%m.%Y")
        except ValueError:
            return 3
    else:
        return 4
    try:
        score = float(score.replace(',', '.'))
    except AttributeError:
        score = float(score)
    finally:
        os.remove(filename)
        return fullname, stage_id, result_id, score, exam_date, retake_date
