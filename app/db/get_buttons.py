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

