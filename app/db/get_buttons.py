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
        sql = "SELECT id, name FROM roles WHERE id > 4"
        cur.execute(sql)
        result = cur.fetchall()
    return result


# Список городов
async def get_city_buttons():
    with conn.cursor() as cur:
        sql = "SELECT id, city FROM cities"
        cur.execute(sql)
        result = cur.fetchall()
    return result