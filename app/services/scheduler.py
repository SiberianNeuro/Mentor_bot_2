import asyncio
import aioschedule as schedule
from loguru import logger


async def db_ping():
    try:
        conn.ping(reconnect=True)
        logger.log("DATABASE", "Database ping succsessful")
    except Exception as e:
        logger.log("DATABASE", f"Database connection failed: {e}")

