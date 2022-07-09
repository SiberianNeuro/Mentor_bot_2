from app.models.database import mysql_connection

from loguru import logger

"""Запросы от администратора"""


# Вытащить айдишник юзера
async def get_user_id(data):
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT id FROM staffs WHERE fullname = %s"
        cur.execute(sql, (data,))
        result = cur.fetchone()
    return result


# Лист админских ИД
async def admin_check(obj):
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT chat_id FROM admins WHERE chat_id = %s"
        cur.execute(sql, obj)
        result = cur.fetchone()
    return result


# Добавить опрос в БД
async def exam_processing(data: dict):
    with mysql_connection() as conn:
        cur = conn.cursor()
        insert_exam = "INSERT INTO exams (document_id, " \
                      "user_id, stage_id, result_id, " \
                      "score, date, retake_date, link) " \
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cur.execute(insert_exam, tuple(data.values()))
        conn.commit()

        if data['result_id'] == 3 and data['stage_id'] in (3, 4, 5):
            raise_user = "UPDATE staffs " \
                         "SET role_id = IF(role_id IN (7, 8), role_id -1, IF(role_id = 9, role_id + 1, role_id)) " \
                         "WHERE id = %s"
            cur.execute(raise_user, data['user_id'])
            conn.commit()

            user_info = "SELECT s.fullname, s.username, r.name FROM staffs s " \
                        "JOIN roles r on s.role_id = r.id " \
                        "WHERE s.id = %s"
            cur.execute(user_info, data['user_id'])
            user = cur.fetchone()
            logger.success(f'{user[0]} {user[1]} повышен(-а) до должности {user[2]}.')

        to_wrapper = "SELECT ex.id, ex.document_id, s.fullname, st.stage, r.result, " \
                     "ex.score, ex.link, ex.retake_date " \
                     "FROM exams ex " \
                     "JOIN staffs s ON ex.user_id = s.id " \
                     "JOIN stages st ON ex.stage_id = st.id " \
                     "JOIN results r ON ex.result_id = r.id " \
                     "WHERE document_id = %s"
        cur.execute(to_wrapper, data['document'])
        result = cur.fetchone()
        return result


# Найти все опросы по ФИО стажера
async def db_search_exam(data: str):
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
async def delete_exam(data: int):
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "DELETE FROM exams WHERE id = %s"
        cur.execute(sql, (data,))
        conn.commit()


"""Запросы к таблицам сотрудника"""


async def is_register(obj):
    with mysql_connection() as conn:
        cur = conn.cursor()

        cur.execute("SELECT chat_id FROM staffs WHERE active = 1 AND chat_id = %s", obj)

        if cur.fetchone() is not None:
            return True
        else:
            cur.execute("SELECT chat_id FROM admins WHERE active = 1 AND chat_id = %s", obj)

            if cur.fetchone() is not None:
                return True
            else:
                return False


async def user_db_roundtrip(state: tuple):
    with mysql_connection() as conn:
        cur = conn.cursor()
        append_user = "INSERT INTO staffs (fullname, city, role_id, traineeship_id, profession, " \
              "start_year, end_year, phone, email, birthdate, username, chat_id, reg_date) VALUES " \
              "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
        cur.execute(append_user, state)
        conn.commit()

        cur = conn.cursor()
        get_user = "SELECT s.id, fullname, username, r.name, city, t.stage, profession, start_year, end_year, " \
              "phone, email, s.role_id FROM staffs s " \
              "JOIN traineeships t on t.id = s.traineeship_id " \
              "JOIN roles r on r.id = s.role_id " \
              "WHERE chat_id = %s AND active = 1"
        cur.execute(get_user, state[-2])
        result = cur.fetchone()
        return result


async def get_user_info(user_name: str):
    with mysql_connection() as conn:
        cur = conn.cursor()
        get_user = "SELECT s.id, fullname, username, r.name, city, t.stage, profession, start_year, end_year, " \
                   "phone, email, s.role_id FROM staffs s " \
                   "JOIN traineeships t on t.id = s.traineeship_id " \
                   "JOIN roles r on r.id = s.role_id " \
                   "WHERE fullname LIKE %s AND active = 1"
        cur.execute(get_user, ('%' + user_name.title() + '%',))
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
