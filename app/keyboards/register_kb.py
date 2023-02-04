from typing import Optional

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

import sqlalchemy as sa
from app.models.user import Role, Traineeship


class RegisterCallback(CallbackData, prefix="register"):
    stage: str
    value: Optional[int]


async def get_register_button() -> InlineKeyboardMarkup:
    register_keyboard = InlineKeyboardBuilder()
    register_keyboard.button(text="Начать регистрацию",
                             callback_data=RegisterCallback(stage='register_start'))
    return register_keyboard.as_markup()


async def get_cancel_button() -> ReplyKeyboardMarkup:
    button = [[KeyboardButton(text='Отмена')]]
    cancel_keyboard = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)
    return cancel_keyboard


async def get_pos_keyboard(db) -> InlineKeyboardMarkup:
    async with db.begin() as session:
        roles = await session.execute(sa.select(Role.name, Role.id).where(Role.id.in_((6, 8, 9))))
    role_keyboard = InlineKeyboardBuilder()
    for role in roles:
        role_keyboard.button(text=role.name, callback_data=RegisterCallback(stage='position', value=role.id))
    role_keyboard.adjust(2)
    return role_keyboard.as_markup()


async def get_spec_keyboard() -> InlineKeyboardMarkup:
    spec_keyboard = InlineKeyboardBuilder()
    buttons_params = {
        'Не поступал и не собираюсь': 1,
        'Не поступал, но собираюсь': 2,
        'Учусь прямо сейчас': 3,
        'Закончил обучение': 4
    }

    for text, value in buttons_params.items():
        spec_keyboard.button(text=text, callback_data=RegisterCallback(stage='spec', value=value))
    spec_keyboard.adjust(1)
    return spec_keyboard.as_markup()


async def get_education_keyboard(db) -> InlineKeyboardMarkup:
    async with db.begin() as session:
        education_vars = await session.execute(
            sa.select(Traineeship.stage, Traineeship.id).where(Traineeship.id.in_((5, 6)))
        )

    education_keyboard = InlineKeyboardBuilder()
    for button in education_vars:
        education_keyboard.button(text=button.stage, callback_data=RegisterCallback(stage='education', value=button.id))
    return education_keyboard.as_markup()



