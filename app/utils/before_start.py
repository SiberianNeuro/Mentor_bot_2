# import asyncio
#
# import tenacity
# from loguru import logger
# from tenacity import _utils
#
# from app.services.config import load_config
# from app.models.redis import BaseRedis
# from app.models.database import mysql_connection
#
# config = load_config('.env')
#
# TIMEOUT_BETWEEN_ATTEMPTS = 2
# MAX_TIMEOUT = 30
#
#
# def before_log(retry_state):
#     if retry_state.outcome.failed:
#         verb, value = "raised", retry_state.outcome.exception()
#     else:
#         verb, value = "raised", retry_state.outcome.result()
#
#     logger.info(f'Retrying {_utils.get_callback_name(retry_state.fn)} '
#                 f'in {getattr(retry_state.next_action, "sleep")} seconds '
#                 f'as it {verb} {value}')
#
#
# def after_log(retry_state):
#     logger.info(
#         "Finished call to {callback!r} after {time:.2f}, this was the {attempt} time calling it.",
#         callback=_utils.get_callback_name(retry_state.fn),
#         time=retry_state.seconds_since_start,
#         attemt=_utils.to_ordinal(retry_state.attempt_number)
#     )
#
#
# @tenacity.retry(
#     wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
#     stop=tenacity.stop_after_delay(MAX_TIMEOUT),
#     before_sleep=before_log,
#     after=after_log,
# )
# async def wait_redis():
#     if config.tg_bot.use_redis:
#         connector = BaseRedis()
#         try:
#             await connector.connect()
#             info = await connector.redis.info()
#             logger.info("Connected to Redis server v{redis}", redis=info['server']['redis_version'])
#         finally:
#             await connector.disconnect()
#
#
# @tenacity.retry(
#     wait=tenacity.wait_fixed(TIMEOUT_BETWEEN_ATTEMPTS),
#     stop=tenacity.stop_after_delay(MAX_TIMEOUT),
#     before_sleep=before_log,
#     after=after_log,
# )
# async def wait_mysql():
#     with mysql_connection() as conn:
#         cur = conn.cursor()
#         cur.execute("SELECT version()")
#         logger.info(f'Connected to {cur.fetchone()}')
#
#
# async def main():
#     # logger.info("Wait for RedisDB...")
#     # try:
#     #     await wait_redis()
#     # except tenacity.RetryError:
#     #     logger.error("Failed to establish connection with RedisDB.")
#     #     exit(1)
#
#     logger.info("Wait for MySQL...")
#     try:
#         await wait_mysql()
#     except tenacity.RetryError:
#         logger.error("Failed to establish connection with MySQL.")
#     logger.info("Ready.")
#
#
# if __name__ == '__main__':
#     asyncio.run(main())
