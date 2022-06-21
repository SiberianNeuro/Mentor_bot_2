import urllib.request
import docx
import os

from loader import config, bot


async def file_parser(fileid, filename, with_retake: bool = False) -> tuple:
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

    document = docx.Document(filename)
    parse_1 = document.tables[2]
    parse_2 = document.tables[0]
    names = []
    text = []
    for row in parse_1.rows:
        text.append([cell.text for cell in row.cells])
    for row in parse_2.rows:
        names.append([cell.text for cell in row.cells])
    name = names[0][1]
    score = text[-1][2]
    try:
        score = float(score)
    except ValueError:
        score = float(score.replace(',', '.'))
    finally:
        os.remove(filename)
        return score, name
