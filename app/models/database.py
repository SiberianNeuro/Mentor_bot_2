import pymysql.cursors

from loader import config


def mysql_connection():
    conn = pymysql.connect(
                host=config.db.db_host,
                user=config.db.db_user,
                password=config.db.db_pass,
                database=config.db.db_name,
                cursorclass=pymysql.cursors.Cursor,
                charset="utf8mb4",
            )
    return conn


conn = mysql_connection()
cur = conn.cursor()