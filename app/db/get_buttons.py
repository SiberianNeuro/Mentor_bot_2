from loader import conn


# Форматы опроса
def get_stage_buttons():
    with conn.cursor() as cur:
        sql = "SELECT * FROM stages"
        cur.execute(sql)
        result = cur.fetchall()
    return result


# Результат опроса
def get_result_buttons():
    with conn.cursor() as cur:
        sql = "SELECT * FROM results"
        cur.execute(sql)
        result = cur.fetchall()
    return result


# Список должностей
def get_role_buttons():
    with conn.cursor() as cur:
        sql = "SELECT id, name FROM roles"
        cur.execute(sql)
        result = cur.fetchall()
    return result

