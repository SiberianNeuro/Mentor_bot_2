from loader import conn


# Форматы опроса
async def get_stage_buttons():
    with conn.cursor() as cur:
        sql = "SELECT * FROM stages"
        cur.execute(sql)
        result = cur.fetchall()
    return result


# Результат опроса
async def get_result_buttons():
    with conn.cursor() as cur:
        sql = "SELECT * FROM results"
        cur.execute(sql)
        result = cur.fetchall()
    return result


# Список должностей
async def get_role_buttons():
    with conn.cursor() as cur:
        sql = "SELECT id, name FROM roles WHERE level > 2"
        cur.execute(sql)
        result = cur.fetchall()
    return result


async def get_education_buttons():
    with conn.cursor() as cur:
        sql = "SELECT id, stage FROM stages WHERE id IN (5, 6)"
        cur.execute(sql)
        result = cur.fetchall()
    return result


async def get_mentors_buttons():
    with conn.cursor() as cur:
        sql = "SELECT id, fullname, role_id FROM mentor_base.admins " \
              "WHERE role_id IN (4, 12)"
        cur.execute(sql)
        result = cur.fetchall()
    return result

