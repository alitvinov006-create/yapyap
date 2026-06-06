from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config import *

group = ''


async def inline_courses():
    keyboard = InlineKeyboardBuilder()
    for course in courses:
        keyboard.add(InlineKeyboardButton(text=course, callback_data=course))
    return keyboard.adjust(4).as_markup()

async def inline_options(username: str):
    keyboard = InlineKeyboardBuilder()
    if username in admin:
        if r'Админ панель' not in options:
            options.append(r'Админ панель')
        else:
            pass
    for option in options:
        keyboard.add(InlineKeyboardButton(text=option, callback_data=option))
    keyboard.add(change_group)
    return keyboard.adjust(3).as_markup()

async def admin_panel():
    keyboard = InlineKeyboardBuilder()
    for option in admin_manage:
        keyboard.add(InlineKeyboardButton(text=option, callback_data=option))
    return keyboard.adjust(2).as_markup()

async def choice_1():
    keyboard = InlineKeyboardBuilder()
    for option in choice1:
        keyboard.add(InlineKeyboardButton(text=option, callback_data=option))
    return keyboard.adjust(2).as_markup()

async def choice_2():
    keyboard = InlineKeyboardBuilder()
    for option in choice2:
        keyboard.add(InlineKeyboardButton(text=option, callback_data=option))
    return keyboard.adjust(2).as_markup()

async def go_back():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Вернуться назад', callback_data='back')]])
    return keyboard

change_group = InlineKeyboardButton(text='Сменить указанную группу', callback_data='change')