from loader import conn


"""Запросы от администратора"""
#Вытащить айдишник юзера
async def get_user_id(data):
    with conn.cursor() as cur:
        sql = "SELECT id FROM users WHERE fullname = %s"
        cur.execute(sql, (data,))
        result = cur.fetchall()
    return result

#Лист админских ИД
async def admins_ids():
    with conn.cursor() as cur:
        sql = "SELECT chat_id FROM users WHERE role_id <= 4"
        cur.execute(sql)
        result = cur.fetchall()
    return result

# Добавить опрос в БД
async def sql_add_command(state):
    async with state.proxy() as data:
        with conn.cursor() as cur:
            sql = "INSERT INTO exams (document_id, " \
                  "score, user_id, stage_id, " \
                  "result_id, retake_date, link, date) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, current_timestamp)"
            cur.execute(sql, tuple(data.values()))
            conn.commit()


# Найти опрос по айдишнику документа
async def item_search(data):
    with conn.cursor() as cur:
        sql = "SELECT exams.id, exams.document_id, users.fullname, stages.stage, results.result, " \
              "exams.score, exams.link, exams.retake_date " \
              "FROM mentor_base.exams " \
              "JOIN mentor_base.users ON exams.user_id = users.id " \
              "JOIN mentor_base.stages ON exams.stage_id = stages.id " \
              "JOIN mentor_base.results ON exams.result_id = results.id " \
              "WHERE document_id = %s"
        cur.execute(sql, (data,))
        result = cur.fetchall()
        print(result)
    return result
    # return cur.execute('SELECT * FROM at_list WHERE document == ?', (data,)).fetchall()

# Найти все опросы по ФИО стажера
async def name_search(data):
    with conn.cursor() as cur:
        sql = "SELECT exams.id, exams.document_id, users.fullname, stages.stage, results.result, " \
              "exams.score, exams.link, exams.retake_date " \
              "FROM mentor_base.exams " \
              "JOIN mentor_base.users ON exams.user_id = users.id " \
              "JOIN mentor_base.stages ON exams.stage_id = stages.id " \
              "JOIN mentor_base.results ON exams.result_id = results.id " \
              "WHERE users.fullname LIKE %s"
        cur.execute(sql, ('%' + data + '%',))
        result = cur.fetchall()
        print(result)
    return result

# Удалить запись об опросе
async def sql_delete_command(data):
    with conn.cursor() as cur:
        sql = "DELETE FROM exams WHERE id = %s"
        cur.execute(sql, (data,))
        conn.commit()

# Повышение
async def get_raise_user(id: int):
    with conn.cursor() as cur:
        sql = "UPDATE mentor_base.users " \
              "SET role_id = IF(role_id > 6, role_id -1, role_id) " \
              "WHERE id = %s"
        cur.execute(sql, (id,))
        conn.commit()


"""Запросы к таблицам сотрудника"""


async def chat_id_check():
    with conn.cursor() as cur:
        sql = "SELECT chat_id, active FROM users"
        cur.execute(sql)
        result = cur.fetchall()
    return result


async def add_user(state):
    async with state.proxy() as data:
        with conn.cursor() as cur:
            sql = "INSERT INTO users (fullname, role_id, username, chat_id, reg_date, active) VALUES (%s, %s, %s, %s, CURRENT_DATE, 1)"
            cur.execute(sql, tuple(data.values()))
            conn.commit()


async def active_users(data):
    with conn.cursor() as cur:
        if len(data) != 1:
            cur.execute(f"SELECT chat_id FROM users WHERE role_id IN {data}")
        else:
            cur.execute(f'SELECT chat_id FROM users WHERE role_id = {data[0]}')
        result = cur.fetchall()
    return result

async def get_current_roles(data):
    with conn.cursor() as cur:
        if len(data) != 1:
            cur.execute(f"SELECT name FROM roles WHERE id IN {data}")
        else:
            cur.execute(f'SELECT name FROM roles WHERE id = {data[0]}')
        result = cur.fetchall()
    return result
