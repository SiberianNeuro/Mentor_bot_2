from typing import Callable, Dict, Any, Awaitable, Union

from aiogram import types, BaseMiddleware

from app.models.user import User


class Middleware(BaseMiddleware):
    def __init__(self, config, db_session) -> None:
        self.config = config
        self.db_session = db_session

    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        async with self.db_session.begin() as ses:
            user: User = await ses.get(User, data['event_from_user'].id)
        print('conf')
        data['db'] = self.db_session
        data['config'] = self.config
        data['user'] = user if user and user.active == 1 else None
        return await handler(event, data)
