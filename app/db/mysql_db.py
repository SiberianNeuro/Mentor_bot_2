import pymysql.cursors
from loguru import logger
from typing import Union, Any

from app.models.database import mysql_connection
from app.models.database import conn, cur


"""Запросы от администратора"""


# Вытащить айдишник юзера
async def get_user_id(data: str) -> tuple:
    sql = "SELECT id FROM staffs WHERE fullname = %s"
    cur.execute(sql, (data,))
    result = cur.fetchone()
    return result


# Проверяем пользователя на администратора
async def admin_check(obj: Union[str, int]) -> bool:
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT chat_id FROM admins WHERE chat_id = %s AND active = 1"
        cur.execute(sql, obj)
        result = cur.fetchone()
    if result is None:
        return False
    else:
        return True


# Добавить опрос в БД
async def exam_processing(data: dict) -> tuple:
    with mysql_connection() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        insert_exam = "INSERT INTO exams (document_id, " \
                      "user_id, stage_id, result_id, " \
                      "score, date, retake_date, calls, link) " \
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cur.execute(insert_exam, tuple(data.values()))
        conn.commit()

        if data['result_id'] == 3:
            if data['stage_id'] == 3:
                raise_user = "UPDATE staffs " \
                             "SET role_id = IF(role_id = 8, 7, role_id) " \
                             "WHERE id = %s"
                cur.execute(raise_user, data.get('user_id'))
                conn.commit()
            if data['stage_id'] == 4:
                raise_user = "UPDATE staffs " \
                             "SET role_id = IF(role_id = 7, 6, role_id) " \
                             "WHERE id = %s"
                cur.execute(raise_user, data.get('user_id'))
                conn.commit()
            if data['stage_id'] == 5:
                raise_user = "UPDATE staffs " \
                             "SET role_id = IF(role_id = 9, 10, role_id) " \
                             "WHERE id = %s"
                cur.execute(raise_user, data.get('user_id'))
                conn.commit()

            user_info = "SELECT s.fullname, s.username, r.name FROM staffs s " \
                        "JOIN roles r on s.role_id = r.id " \
                        "WHERE s.id = %s"
            cur.execute(user_info, data.get('user_id'))
            user = cur.fetchone()
            logger.success(f'{user["fullname"]} {user["username"]} повышен(-а) до должности {user["name"]}.')

        cur.execute('SELECT ex.stage_id, ex.result_id, ex.id, ex.document_id, s.fullname, st.stage, r.result, '
                    'ex.score, ex.link, ex.calls, DATE_FORMAT(ex.retake_date, "%%d.%%m.%%Y") AS retake_date '
                    'FROM exams ex '
                    'JOIN staffs s ON ex.user_id = s.id '
                    'JOIN stages st ON ex.stage_id = st.id '
                    'JOIN results r ON ex.result_id = r.id '
                    'WHERE document_id = %s', data.get('document'))
        result = cur.fetchone()
        return result


# Найти все опросы по ФИО стажера
async def db_search_exam(data: str) -> tuple:
    with mysql_connection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT ex.id, ex.document_id, s.fullname, st.stage, r.result, '
                    'ex.score, ex.link, ex.calls, DATE_FORMAT(ex.retake_date, "%%d.%%m.%%Y") AS retake_date '
                    'FROM exams ex '
                    'JOIN staffs s ON ex.user_id = s.id '
                    'JOIN stages st ON ex.stage_id = st.id '
                    'JOIN results r ON ex.result_id = r.id '
                    'WHERE fullname LIKE %s', ('%' + data + '%',))
        result = cur.fetchall()
    return result


# Удалить запись об опросе
async def delete_exam(data: Union[str, int]):
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "DELETE FROM exams WHERE id = %s"
        cur.execute(sql, data)
        conn.commit()


async def change_user_active_status(user_id: Union[str, int], active: Union[str, int]) -> dict:
    with mysql_connection() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        if active == '1':
            cur.execute(f"UPDATE staffs SET active = 0 WHERE id = {user_id}")
            conn.commit()
        elif active == '0':
            cur.execute(f"UPDATE staffs SET active = 1 WHERE id = {user_id}")
            conn.commit()
        cur.execute(
            query="SELECT s.id, fullname, username, r.name, city, t.stage, profession, start_year, end_year, "
                  "phone, email, s.role_id, s.active AS active FROM staffs s "
                  "JOIN traineeships t on t.id = s.traineeship_id "
                  "JOIN roles r on r.id = s.role_id "
                  "WHERE s.id = %s",
            args=user_id
        )
        user_info = cur.fetchone()
        cur.execute(f'SELECT username FROM staffs WHERE id = {user_id}')
        user_fullname = cur.fetchone()
        result = {'user_info': user_info, 'user_fullname': user_fullname['username']}
        return result


"""Запросы к таблицам сотрудника"""


async def is_register(obj: Union[str, int]) -> bool:
    with mysql_connection() as conn:
        cur = conn.cursor()

        cur.execute("SELECT chat_id FROM staffs WHERE active = 1 AND chat_id = %s", str(obj))

        if cur.fetchone() is not None:
            return True
        else:
            cur.execute("SELECT chat_id FROM admins WHERE active = 1 AND chat_id = %s", obj)

            if cur.fetchone() is not None:
                return True
            else:
                return False


async def user_db_roundtrip(state: tuple) -> dict:
    with mysql_connection() as conn:
        cur = conn.cursor()
        append_user = "INSERT INTO staffs (fullname, city, role_id, traineeship_id, profession, " \
                      "start_year, end_year, phone, email, birthdate, username, chat_id, reg_date) VALUES " \
                      "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
        cur.execute(append_user, state)
        conn.commit()
        cur.close()

        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        get_user = "SELECT s.id, fullname, username, r.name, city, t.stage, profession, start_year, end_year, " \
                   "phone, email, s.role_id, IF(active = 1, 'Активирован', 'Деактивирован') AS active FROM staffs s " \
                   "JOIN traineeships t on t.id = s.traineeship_id " \
                   "JOIN roles r on r.id = s.role_id " \
                   "WHERE chat_id = %s AND active = 1"
        cur.execute(get_user, str(state[-1]))
        result = cur.fetchone()
        return result


async def get_user_info(user: Union[str, int]) -> dict:
    with mysql_connection() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        if type(user) is str:
            cur.execute(
                query="SELECT s.id, fullname, username, r.name, city, t.stage, profession, start_year, end_year, "
                      "phone, email, s.role_id, s.active AS active FROM staffs s "
                      "JOIN traineeships t on t.id = s.traineeship_id "
                      "JOIN roles r on r.id = s.role_id "
                      "WHERE fullname LIKE %s",
                args=('%' + user.title() + '%',)
            )
            result = cur.fetchall()
        elif type(user) is int:
            cur.execute(
                query="SELECT s.id, fullname, username, r.name, city, t.stage, profession, start_year, end_year, "
                      "phone, email, s.role_id, s.active AS active FROM staffs s "
                      "JOIN traineeships t on t.id = s.traineeship_id "
                      "JOIN roles r on r.id = s.role_id "
                      "WHERE chat_id = %s AND active = 1",
                args=str(user)
            )
            result = cur.fetchone()
    return result


async def active_users(data: tuple) -> dict:
    with mysql_connection() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cur.execute(f'SELECT chat_id, username FROM staffs '
                    f'WHERE role_id IN {(*data, "None")} AND active = 1 '
                    f'ORDER BY RAND()')
        result = cur.fetchall()
    return result


async def get_current_roles(data: tuple) -> tuple:
    with mysql_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT name FROM roles WHERE id IN {(*data, 'None')}")
        result = cur.fetchall()
    return result


async def get_admin(admin_id: int) -> dict:
    with mysql_connection() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        get_info = "SELECT fullname, username, chat_id FROM admins " \
                   "WHERE id = %s"
        cur.execute(get_info, admin_id)
        result = cur.fetchone()
    return result


async def get_chat_members(ids: list) -> dict:
    with mysql_connection() as conn:
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cur.execute(
            query=f"SELECT fullname, city FROM staffs "
                  f"WHERE chat_id IN {(*ids, 'None')}")
        result = cur.fetchall()
        return result



