from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    db_host: str
    db_user: str
    db_pass: str
    db_name: str


@dataclass
class TgBot:
    token: str
    use_redis: bool


@dataclass
class Miscellaneous:
    mentor_table: str
    doctors_chat: str
    headmaster_chat: str
    l1_chat: str
    kis_chat: str
    kor_chat: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


# Парсим .env и вытаскиваем оттуда конфиги
def load_config(path: str = None) -> Config:

    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            db_host=env.str("DB_HOST"),
            db_user=env.str("DB_USER"),
            db_pass=env.str("DB_PASS"),
            db_name=env.str("DB_NAME")
        ),
        misc=Miscellaneous(
            mentor_table=env.str("MENTORS_TABLE"),
            doctors_chat=env.str("DOCTORS_GROUP_CHAT_ID"),
            headmaster_chat=env.str("NASTYA_GROUP_CHAT_ID"),
            l1_chat=env.str("VALYA_GROUP_CHAT_ID"),
            kis_chat=env.str("DASHA_GROUP_CHAT_ID"),
            kor_chat=env.str("SASHA_GROUP_CHAT_ID")
        )
    )
