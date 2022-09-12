import asyncio
import aioschedule as schedule
from app.models.database import conn, cur
from loguru import logger


async def db_ping():
    try:
        conn.ping(reconnect=True)
        logger.log("DATABASE", "Database ping succsessful")
    except Exception as e:
        logger.log("DATABASE", f"Database connection failed: {e}")


async def scheduler():
    schedule.every(6).hours.do(db_ping)
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)

