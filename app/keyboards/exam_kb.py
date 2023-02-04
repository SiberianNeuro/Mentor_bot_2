from typing import Optional

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData


class ExamCallback(CallbackData, prefix='exam'):
    action: str
    param: Optional[str]
    value: Optional[int]


async def get_overload_keyboard() -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(text="Подтвердить ✅", callback_data=ExamCallback(action="overload", value=1).pack()),
        InlineKeyboardButton(text="Перезагрузить 🔄", callback_data=ExamCallback(action="overload", value=0).pack()),
            ]]
    overload_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return overload_keyboard

# mentor_callback = CallbackData('mentors', 'mentor_id', 'role_id', 'user_id')
# teams_callback = CallbackData('teams', 'team_id', 'user_id')
#
# # Стартовая админская клавиатура
# async def get_admin_kb() -> ReplyKeyboardMarkup:
#     buttons = [
#         KeyboardButton('Загрузить опрос ⏏'),
#         KeyboardButton('Найти опрос 👀'),
#         KeyboardButton('Рассылка тестов 🔊'),
#         KeyboardButton('Найти сотрудника 👨‍⚕'),
#         KeyboardButton('Звонки стажеров 📞')
#     ]
#     admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#     admin_keyboard.add(*buttons)
#     return admin_keyboard
#
#
# """Клавиатуры загрузки протоколов"""
#
#
# # Клавиатура подтверждения валидности опроса
# async def get_overload_keyboard() -> InlineKeyboardMarkup:
#     buttons = (
#         InlineKeyboardButton(text='Подтвердить ✅', callback_data=exam_callback.new(action='overload', action_data='1')),
#         InlineKeyboardButton(text='Перезагрузить 🔄',
#                              callback_data=exam_callback.new(action='overload', action_data='2'))
#     )
#     overload_keyboard = InlineKeyboardMarkup(row_width=1)
#     overload_keyboard.add(*buttons)
#     return overload_keyboard
#
#
# # Клавиатура загрузки формата опроса
# async def get_stage_keyboard() -> InlineKeyboardMarkup:
#     buttons = await get_stage_buttons()
#     format_keyboard = InlineKeyboardMarkup(row_width=2)
#     for button in buttons:
#         format_keyboard.insert(InlineKeyboardButton(
#             text=button['stage'], callback_data=exam_callback.new(action='format', action_data=button['id'])
#         ))
#     return format_keyboard
#
#
# # Клавиатура загрузки статуса опроса
# async def get_result_keyboard() -> InlineKeyboardMarkup:
#     buttons = await get_result_buttons()
#     result_keyboard = InlineKeyboardMarkup(row_width=1)
#     for button in buttons:
#         result_keyboard.insert(InlineKeyboardButton(
#             text=button['result'], callback_data=exam_callback.new(action='result', action_data=button['id'])
#         ))
#     return result_keyboard
#
#
# # Кнопка "удалить" под каждым протоколом
# async def get_delete_button(id: int) -> InlineKeyboardMarkup:
#     button = InlineKeyboardButton(
#         'Удалить аттестацию ❌', callback_data=exam_callback.new(action='delete', action_data=id))
#     delete_keyboard = InlineKeyboardMarkup(row_width=1)
#     delete_keyboard.add(button)
#     return delete_keyboard
#
#
# active_callback = CallbackData('change_active', 'active_action', 'user_id', 'active_now')
#
#
# async def change_active_button(id: int, active: int) -> InlineKeyboardMarkup:
#     button = InlineKeyboardButton(
#         text='Деактивировать ❌' if active == 1 else 'Активировать ✅',
#         callback_data=active_callback.new(active_action='change', user_id=id, active_now=active)
#     )
#     deactivate_keyboard = InlineKeyboardMarkup(row_width=1)
#     deactivate_keyboard.add(button)
#     return deactivate_keyboard
#
#
# """Клавиатуры рассылок"""
#
# mailing_callback = CallbackData('mailing', 'action', 'c_data')
#
#
# # Подтверждает или добавляет запись в рассылку
# async def get_mailing_keyboard() -> InlineKeyboardMarkup:
#     buttons = [
#         InlineKeyboardButton(text='Добавить', callback_data=mailing_callback.new(action='load', c_data=0)),
#         InlineKeyboardButton(text='Подтвердить', callback_data=mailing_callback.new(action='confirm', c_data=0))
#     ]
#     mailing_keyboard = InlineKeyboardMarkup(row_width=2)
#     mailing_keyboard.add(*buttons)
#     return mailing_keyboard
#
#
# # Переход от выбора ролей к добавлению тестов
# async def text_switch_button() -> InlineKeyboardMarkup:
#     button = InlineKeyboardButton(text='Загрузить текст(-ы)',
#                                   callback_data=mailing_callback.new(action='execute', c_data=0))
#     text_switch = InlineKeyboardMarkup(row_width=1)
#     text_switch.add(button)
#     return text_switch
#
#
# # Переход от тестов к рассылке
# async def get_execute_button() -> InlineKeyboardMarkup:
#     button = InlineKeyboardButton(text='Начать рассылку',
#                                   callback_data=mailing_callback.new(action='execute', c_data=0))
#     execute_button = InlineKeyboardMarkup(row_width=1)
#     execute_button.add(button)
#     return execute_button
#
#
# # Выбор участников рассылки
# async def get_roles_keyboard() -> InlineKeyboardMarkup:
#     buttons = await get_role_buttons()
#     roles_keyboard = InlineKeyboardMarkup(row_width=2)
#     for button in buttons:
#         roles_keyboard.insert(InlineKeyboardButton(text=button['name'],
#                                                    callback_data=mailing_callback.new(action='worker',
#                                                                                       c_data=button['id'])))
#     return roles_keyboard
#
#
# async def get_trainee_phones() -> InlineKeyboardMarkup:
#     buttons = await get_phone_buttons()
#     phones_keyboard = InlineKeyboardMarkup(row_width=2)
#     for button in buttons:
#         phones_keyboard.insert(InlineKeyboardButton(text=button['phone_name'],
#                                                     callback_data=exam_callback.new(action='phones', action_data=button[
#                                                         'phone_number'])))
#     return phones_keyboard
#
#
# """Клавиатура распределения"""
#
#
async def get_mentors_keyboard(obj) -> InlineKeyboardMarkup:
    buttons = await get_mentors_buttons()
    mentors_keyboard = InlineKeyboardMarkup(row_width=1)
    for button in buttons:
        mentors_keyboard.insert(InlineKeyboardButton(
            text=button['fullname'],
            callback_data=mentor_callback.new(mentor_id=button['id'], role_id=button['role_id'], user_id=obj)
        ))
    return mentors_keyboard
#
#
# async def get_clusters_keyboard(user_id) -> InlineKeyboardMarkup:
#     buttons = await get_teams_buttons()
#     cluster_keyboard = InlineKeyboardMarkup(row_width=5)
#     for button in buttons:
#         cluster_keyboard.insert(
#             InlineKeyboardButton(
#                 text=button['team_name'], callback_data=teams_callback.new(
#                     team_id=button['team_id'],
#                     user_id=user_id
#                 )
#             )
#         )
#     return cluster_keyboard