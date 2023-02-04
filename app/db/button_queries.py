


# # Форматы опроса
# async def get_stage_buttons() -> dict:
#     # with mysql_connection() as conn:
#     #     cur = conn.cursor()
#     sql = "SELECT * FROM lib_exam_stages"
#     cur.execute(sql)
#     result = cur.fetchall()
#     return result
#
#
# # Результат опроса
# async def get_result_buttons() -> dict:
#     # with mysql_connection() as conn:
#     #     cur = conn.cursor()
#     sql = "SELECT * FROM lib_exam_results"
#     cur.execute(sql)
#     result = cur.fetchall()
#     return result
#
#
# # Список должностей
# async def get_role_buttons() -> dict:
#     # with mysql_connection() as conn:
#     #     cur = conn.cursor()
#     sql = "SELECT id, name FROM lib_roles WHERE id BETWEEN 5 AND 11"
#     cur.execute(sql)
#     result = cur.fetchall()
#     return result
#
#
# async def get_education_buttons() -> dict:
#     # with mysql_connection() as conn:
#     #     cur = conn.cursor()
#     sql = "SELECT id, stage FROM lib_traineeships WHERE id IN (5, 6)"
#     cur.execute(sql)
#     result = cur.fetchall()
#     return result
#
#
# async def get_mentors_buttons() -> dict:
#     # with mysql_connection() as conn:
#     #     cur = conn.cursor()
#     sql = "SELECT id, fullname, role_id FROM admins " \
#           "WHERE role_id in (4, 12)"
#     cur.execute(sql)
#     result = cur.fetchall()
#     return result
#
#
# async def get_phone_buttons() -> dict:
#     # with mysql_connection() as conn:
#     #     cur = conn.cursor()
#     cur.execute("SELECT phone_name, phone_number FROM admin_phones ap")
#     result = cur.fetchall()
#     return result
#
#
# async def get_teams_buttons() -> dict:
#     cur.execute(
#         "SELECT t.name AS team_name, t.id AS team_id FROM lib_teams t"
#     )
#     result = cur.fetchall()
#     return result
#
