import calendar
from datetime import datetime, timedelta
from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery


# setting callback_data prefix and parts
class CalendarCallback(CallbackData, prefix='simple_calendar'):
    act: str
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]


class SimpleCalendar:
    months = {
        'January': 'Январь',
        'February': 'Февраль',
        'March': 'Март',
        'April': 'Апрель',
        'May': 'Май',
        'June': 'Июнь',
        'July': 'Июль',
        'August': 'Август',
        'September': 'Сентябрь',
        'October': 'Октябрь',
        'November': 'Ноябрь',
        'December': 'Декабрь'
    }
    @staticmethod
    async def start_calendar(
            year: int = datetime.now().year,
            month: int = datetime.now().month
    ) -> InlineKeyboardMarkup:
        """
        Creates an inline keyboard with the provided year and month
        :param int year: Year to use in the calendar, if None the current year is used.
        :param int month: Month to use in the calendar, if None the current month is used.
        :return: Returns InlineKeyboardMarkup object with the calendar.
        """
        kb = KeyboardBuilder(button_type=InlineKeyboardButton)
        ignore_callback = CalendarCallback(act="IGNORE")  # for buttons with no answer
        # First row - Month and Year
        kb.row(
            InlineKeyboardButton(text="<<", callback_data=CalendarCallback(
                act="PREV-YEAR", year=year, month=month, day=1).pack()),
            InlineKeyboardButton(
                text=f'{SimpleCalendar.months[calendar.month_name[month]]} {str(year)}',
                callback_data=ignore_callback.pack()
            ),
            InlineKeyboardButton(text=">>", callback_data=CalendarCallback(
                act="NEXT-YEAR", year=year, month=month, day=1).pack())
        )
        # Second row - weekdays
        kb.row(
            *[InlineKeyboardButton(text=day, callback_data=ignore_callback.pack()) for day in
              ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]]
        )

        # Calendar rows - Days of month
        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            kb.row(
                *[
                    InlineKeyboardButton(
                        text=" " if day == 0 else day,
                        callback_data=ignore_callback.pack() if day == 0 else CalendarCallback(
                            act="DAY", year=year, month=month, day=day
                        ).pack()
                    ) for day in week
                ]
            )
        # Last row - Buttons
        kb.row(
            InlineKeyboardButton(text='<', callback_data=CalendarCallback(
                act="PREV-MONTH", year=year, month=month
            ).pack()),
            InlineKeyboardButton(text=" ", callback_data=ignore_callback.pack()),
            InlineKeyboardButton(text='>', callback_data=CalendarCallback(
                act="NEXT-MONTH", year=year, month=month
            ).pack())
        )
        return kb.as_markup()

    async def process_selection(self, query: CallbackQuery, data: CalendarCallback) -> tuple:
        """
        Process the callback_query. This method generates a new calendar if forward or
        backward is pressed. This method should be called inside a CallbackQueryHandler.
        :param query: callback_query, as provided by the CallbackQueryHandler
        :param data: callback_data, dictionary, set by calendar_callback
        :return: Returns a tuple (Boolean,datetime), indicating if a date is selected
                    and returning the date if so.
        """
        return_data = (False, None)
        temp_date = datetime(data.year, data.month, 1)
        # processing empty buttons, answering with no action
        if data.act == "IGNORE":
            await query.answer(cache_time=60)
        # user picked a day button, return date
        if data.act == "DAY":
            await query.message.delete_reply_markup()  # removing inline keyboard
            return_data = True, datetime(data.year, data.month, data.day)
        # user navigates to previous year, editing message with new calendar
        if data.act == "PREV-YEAR":
            prev_date = temp_date - timedelta(days=365)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next year, editing message with new calendar
        if data.act == "NEXT-YEAR":
            next_date = temp_date + timedelta(days=365)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        # user navigates to previous month, editing message with new calendar
        if data.act == "PREV-MONTH":
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(await self.start_calendar(int(prev_date.year), int(prev_date.month)))
        # user navigates to next month, editing message with new calendar
        if data.act == "NEXT-MONTH":
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(await self.start_calendar(int(next_date.year), int(next_date.month)))
        # at some point user clicks DAY button, returning date
        return return_data
