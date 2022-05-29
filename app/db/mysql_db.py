from loader import conn


"""Запросы от администратора"""


# Добавить опрос в БД
async def sql_add_command(state):
    async with state.proxy() as data:
        with conn.cursor() as cur:
            sql = "INSERT INTO exams (document_id, " \
                  "exam_score, fullname, exam_format, " \
                  "exam_status, retake_date, exam_YT_link, exam_date) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_DATE)"
            cur.execute(sql, tuple(data.values()))
            conn.commit()


# Найти опрос по айдишнику документа
async def item_search(data):
    with conn.cursor() as cur:
        sql = "SELECT * FROM exams WHERE document_id = %s"
        cur.execute(sql, (data,))
        result = cur.fetchall()
    return result
    # return cur.execute('SELECT * FROM at_list WHERE document == ?', (data,)).fetchall()

# Найти все опросы по ФИО стажера
async def name_search(data):
    with conn.cursor() as cur:
        sql = "SELECT * FROM exams WHERE fullname LIKE %s"
        cur.execute(sql, ('%' + data + '%',))
        result = cur.fetchall()
    return result

# Удалить запись об опросе
async def sql_delete_command(data):
    with conn.cursor() as cur:
        sql = "DELETE FROM exams WHERE exam_id = %s"
        cur.execute(sql, (data,))
        conn.commit()


"""Запросы к таблицам сотрудника"""


async def chat_id_check():
    with conn.cursor() as cur:
        sql = "SELECT chat_id FROM users"
        cur.execute(sql)
        result = cur.fetchall()
    return result


async def add_user(state):
    async with state.proxy() as data:
        with conn.cursor() as cur:
            sql = "INSERT INTO users (fullname, pos, username, chat_id, reg_date) VALUES (%s, %s, %s, %s, CURRENT_DATE)"
            cur.execute(sql, tuple(data.values()))
            conn.commit()