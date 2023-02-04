from typing import Union, Optional, Sequence

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from app.models.user import User


class RoleFilter(BaseFilter):
    role: Optional[Union[Sequence, int]] = None
    team: Optional[Union[Sequence, int]] = None

    async def __call__(self, obj: TelegramObject, user: User) -> bool:
        if isinstance(user, User):
            if user.role_id == 1:
                return True

            if isinstance(self.role, Sequence):
                return user.role_id in self.role
            if isinstance(self.role, int):
                return user.role_id == self.role
            if isinstance(self.team, Sequence):
                return user.team_id in self.team
            if isinstance(self.team, int):
                return user.team_id == self.team
        return False

