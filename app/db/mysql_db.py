from app.models.database import mysql_connection

"""Запросы от администратора"""
#Вытащить айдишник юзера
async def get_user_id(data):
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT id FROM staffs WHERE fullname = %s"
        cur.execute(sql, (data,))
        result = cur.fetchall()
    return result

#Лист админских ИД
async def admins_ids():
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT chat_id FROM admins"
        cur.execute(sql)
        result = [i[0] for i in cur.fetchall()]
    return result

# Добавить опрос в БД
async def append_exam(state):
    async with state.proxy() as data:
        with mysql_connection() as conn:
            cur = conn.cursor()
            sql = "INSERT INTO exams (document_id, " \
                  "user_id, stage_id, result_id, " \
                  "score, date, retake_date, link) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(sql, tuple(data.values()))
            conn.commit()


# Найти опрос по айдишнику документа
async def item_search(data):
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT ex.id, ex.document_id, s.fullname, st.stage, r.result, " \
              "ex.score, ex.link, ex.retake_date " \
              "FROM exams ex " \
              "JOIN staffs s ON ex.user_id = s.id " \
              "JOIN stages st ON ex.stage_id = st.id " \
              "JOIN results r ON ex.result_id = r.id " \
              "WHERE document_id = %s"
        cur.execute(sql, (data,))
        result = cur.fetchone()
    return result


# Найти все опросы по ФИО стажера
async def name_search(data):
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT ex.id, ex.document_id, s.fullname, st.stage, r.result, " \
              "ex.score, ex.link, ex.retake_date " \
              "FROM exams ex " \
              "JOIN staffs s ON ex.user_id = s.id " \
              "JOIN stages st ON ex.stage_id = st.id " \
              "JOIN results r ON ex.result_id = r.id " \
              "WHERE s.fullname LIKE %s"
        cur.execute(sql, ('%' + data + '%',))
        result = cur.fetchall()
    return result


# Удалить запись об опросе
async def delete_exam(data):
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "DELETE FROM exams WHERE id = %s"
        cur.execute(sql, (data,))
        conn.commit()


# Повышение
async def get_raise_user(id: int):
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "UPDATE staffs " \
              "SET role_id = IF(role_id IN (7, 8), role_id -1, IF(role_id = 9, role_id + 1, role_id)) " \
              "WHERE id = %s"
        cur.execute(sql, (id,))
        conn.commit()


"""Запросы к таблицам сотрудника"""


async def chat_id_check():
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT chat_id FROM staffs WHERE active = 1"
        cur.execute(sql)
        result = cur.fetchone()
    return result


async def add_user(state):
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "INSERT INTO staffs (fullname, city, role_id, traineeship_id, profession, " \
          "start_year, end_year, phone, email, birthdate, username, chat_id, reg_date) VALUES " \
          "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
        cur.execute(sql, state)
        conn.commit()

async def get_user(name):
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT s.id, fullname, username, r.name, city, t.stage, profession, start_year, end_year, " \
              "phone, email FROM staffs s " \
              "JOIN traineeships t on t.id = s.traineeship_id " \
              "JOIN roles r on r.id = s.role_id " \
              "WHERE fullname = %s AND active = 1"
        cur.execute(sql, name)
        result = cur.fetchall()
    return result


async def active_users(data):
    with mysql_connection() as conn:
        cur = conn.cursor()
        if len(data) != 1:
            cur.execute(f"SELECT chat_id, username FROM staffs WHERE role_id IN {data}")
        else:
            cur.execute(f'SELECT chat_id, username FROM staffs WHERE role_id = {data[0]}')
        result = cur.fetchall()
    return result


async def get_current_roles(data):
    with mysql_connection() as conn:
        cur = conn.cursor()
        if len(data) != 1:
            cur.execute(f"SELECT name FROM roles WHERE id IN {data}")
        else:
            cur.execute(f'SELECT name FROM roles WHERE id = {data[0]}')
        result = cur.fetchall()
    return result
