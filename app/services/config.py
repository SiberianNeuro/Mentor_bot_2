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
    admin_ids: list
    use_redis: bool


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            db_host=env.str("DB_HOST"),
            db_user=env.str("DB_USER"),
            db_pass=env.str("DB_PASS"),
            db_name=env.str("DB_NAME")
        ),
        misc=Miscellaneous()
    )