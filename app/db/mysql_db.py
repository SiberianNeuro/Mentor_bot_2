from loader import conn


"""Запросы от администратора"""
#Вытащить айдишник юзера
async def get_user_id(data):
    with conn.cursor() as cur:
        sql = "SELECT id FROM staffs WHERE fullname = %s"
        cur.execute(sql, (data,))
        result = cur.fetchall()
    return result

#Лист админских ИД
async def admins_ids():
    with conn.cursor() as cur:
        sql = "SELECT chat_id FROM admins"
        cur.execute(sql)
        result = [id[0] for id in cur.fetchall()]
    return result

# Добавить опрос в БД
async def append_exam(state):
    async with state.proxy() as data:
        with conn.cursor() as cur:
            sql = "INSERT INTO exams (document_id, " \
                  "user_id, stage_id, result_id, " \
                  "score, date, retake_date, link) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(sql, tuple(data.values()))
            conn.commit()


# Найти опрос по айдишнику документа
async def item_search(data):
    with conn.cursor() as cur:
        sql = "SELECT exams.id, exams.document_id, staffs.fullname, stages.stage, results.result, " \
              "exams.score, exams.link, exams.retake_date " \
              "FROM mentor_base.exams " \
              "JOIN mentor_base.staffs ON exams.user_id = staffs.id " \
              "JOIN mentor_base.stages ON exams.stage_id = stages.id " \
              "JOIN mentor_base.results ON exams.result_id = results.id " \
              "WHERE document_id = %s"
        cur.execute(sql, (data,))
        result = cur.fetchall()[0]
    return result


# Найти все опросы по ФИО стажера
async def name_search(data):
    with conn.cursor() as cur:
        sql = "SELECT exams.id, exams.document_id, staffs.fullname, stages.stage, results.result, " \
              "exams.score, exams.link, exams.retake_date " \
              "FROM mentor_base.exams " \
              "JOIN mentor_base.staffs ON exams.user_id = staffs.id " \
              "JOIN mentor_base.stages ON exams.stage_id = stages.id " \
              "JOIN mentor_base.results ON exams.result_id = results.id " \
              "WHERE staffs.fullname LIKE %s"
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
        sql = "UPDATE mentor_base.staffs " \
              "SET role_id = IF(role_id > 6, role_id -1, role_id) " \
              "WHERE id = %s"
        cur.execute(sql, (id,))
        conn.commit()


"""Запросы к таблицам сотрудника"""


async def chat_id_check():
    with conn.cursor() as cur:
        sql = "SELECT chat_id FROM staffs WHERE active = 1"
        cur.execute(sql)
        result = [id[0] for id in cur.fetchall()]
    return result


async def add_user(state):
    with conn.cursor() as cur:
        sql = "INSERT INTO staffs (fullname, city, role_id, traineeship_id, profession, " \
          "start_year, end_year, phone, email, birthdate, username, chat_id, reg_date) VALUES " \
          "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
        cur.execute(sql, state)
        conn.commit()

async def get_user(name):
    with conn.cursor() as cur:
        sql = "SELECT s.id, fullname, username, r.name, city, t.stage, profession, start_year, end_year " \
              "phone, email FROM mentor_base.staffs s " \
              "JOIN traineeships t on t.id = staffs.traineeship_id " \
              "JOIN roles r on r.id = staffs.role_id " \
              "WHERE fullname = %s AND active = 1"
        cur.execute(sql, name)
        result = cur.fetchall()
    return result


async def active_users(data):
    with conn.cursor() as cur:
        if len(data) != 1:
            cur.execute(f"SELECT chat_id FROM staffs WHERE role_id IN {data}")
        else:
            cur.execute(f'SELECT chat_id FROM staffs WHERE role_id = {data[0]}')
        result = [id[0] for id in cur.fetchall()]
    return result


async def get_current_roles(data):
    with conn.cursor() as cur:
        if len(data) != 1:
            cur.execute(f"SELECT name FROM roles WHERE id IN {data}")
        else:
            cur.execute(f'SELECT name FROM roles WHERE id = {data[0]}')
        result = cur.fetchall()
    return result
