from dataclasses import dataclass

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data


@dataclass
class IsAdminFilter(BoundFilter):
    key = "is_admin"
    is_admin: bool

    async def check(self, obj) -> bool:
        data = ctx_data.get()
        is_admin = data['team']['team_id'] == 5
        return is_admin


@dataclass
class IsMentorFilter(BoundFilter):
    key = "is_mentor"
    is_mentor: bool

    async def check(self, obj) -> bool:
        data = ctx_data.get()
        is_mentor = data['team']['role_id'] in (4, 12, 1, 2, 3)
        return is_mentor


@dataclass
class IsL3SeniorFilter(BoundFilter):
    key = "is_l3_senior"
    is_l3_senior: bool

    async def check(self, obj) -> bool:
        data = ctx_data.get()
        is_l3_senior = data['team']['division_id'] == 1 and data['team']['role_id'] == 5
        return is_l3_senior


@dataclass
class IsL2Filter(BoundFilter):
    key = "is_l2"
    is_l2: bool

    async def check(self, obj) -> bool:
        data = ctx_data.get()
        is_l2 = data['team']['division_id'] == 2
        return is_l2


@dataclass
class IsL1Filter(BoundFilter):
    key = "is_l1"
    is_l1: bool

    async def check(self, obj) -> bool:
        data = ctx_data.get()
        is_l1 = data['team']['division_id'] == 3
        return is_l1


@dataclass
class IsL1SeniorFilter(BoundFilter):
    key = 'is_l1_senior'
    is_l1_senior: bool

    async def check(self, obj) -> bool:
        data = ctx_data.get()
        is_l1_senior = data['team']['division_id'] == 3 and data['team']['role_id'] == 11
        return is_l1_senior
