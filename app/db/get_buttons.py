from app.models.database import mysql_connection


# Форматы опроса
async def get_stage_buttons():
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT * FROM stages"
        cur.execute(sql)
        result = cur.fetchall()
    return result


# Результат опроса
async def get_result_buttons():
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT * FROM results"
        cur.execute(sql)
        result = cur.fetchall()
    return result


# Список должностей
async def get_role_buttons():
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT id, name FROM roles WHERE id BETWEEN 5 AND 11"
        cur.execute(sql)
        result = cur.fetchall()
    return result


async def get_education_buttons():
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT id, stage FROM traineeships WHERE id IN (5, 6)"
        cur.execute(sql)
        result = cur.fetchall()
    return result


async def get_mentors_buttons():
    with mysql_connection() as conn:
        cur = conn.cursor()
        sql = "SELECT id, fullname, role_id FROM admins " \
              "WHERE role_id in (4, 12)"
        cur.execute(sql)
        result = cur.fetchall()
    return result


async def get_phone_buttons(admin_id):
    with mysql_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            query=f"SELECT phone_name, phone_number FROM admin_phones ap "
                  f"JOIN admins a ON a.id = ap.admin_id "
                  f"WHERE a.chat_id = {admin_id}"
        )
        result = cur.fetchall()
        return result

