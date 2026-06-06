from aiogram.filters import CommandStart
from aiogram.types import Message

from app.states import Reg, Mailing, AdminAdd
from aiogram.fsm.context import FSMContext
from app.contacts import teach_contact
from app.schedule import schedule
from config import admin, courses
from app.check import valid_group
from app.mailing import *
import database.requests as rq

import app.keyboards as kb

router = Router()

user, group_values, group_id = '', '', 0
users = []


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Reg.course)
    await message.answer(r"""
Меня звать Олежа, твой бот\-навигатор по МИИГАиК\.

Представься в интерактивном режиме\.
Для начала выбери год обучения:""", reply_markup=await kb.inline_courses())

@router.callback_query(lambda f: f.data in courses)
async def reg_course(callback: CallbackQuery, state: FSMContext):
    await callback.answer(r'Вы выбрали курс')
    await callback.message.edit_text(r'Теперь выбери факультет')
    await state.update_data(course=callback.data)
    await state.set_state(Reg.fac)

@router.message(Reg.fac)
async def reg_group(message: Message, state: FSMContext):
    await state.update_data(fac=message.text)
    await state.set_state(Reg.group)
    await message.answer(r'Теперь введи свою группу')

@router.message(Reg.group)
async def reg_done(message: Message, state: FSMContext):
    global users, user, group_values, group_id
    await state.update_data(group=message.text)
    data = await state.get_data()
    group_values = [i for i in data.values()]

    if type(valid_group(group_values)) == int: # О ГОСПОДИ УПАСИ
        group_id = valid_group(group_values)
        await rq.set_user(message.from_user.id, message.from_user.username, '-'.join(group_values), group_id)
        users = await rq.get_info()
        print(users)
        user_id, user, group_values, group_id = users[-1][0], users[-1][1], users[-1][2], users[-1][3]
        await message.answer(rf"""Регистрация завершена. Группа: {group_values}, ID: {group_id}.
Что желаешь выяснить?""", reply_markup=await kb.inline_options(message.from_user.username))
    else:
        await message.answer(valid_group(group_values), reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [kb.change_group]
        ]))
    await state.clear()


@router.callback_query(lambda f: f.data == 'Расписание')
async def schedule_func(callback: CallbackQuery):
    for day, sch in schedule(group_id).items():
        subjects = "\n".join(sch)
        await callback.message.answer(f"""
{day}
{subjects}""", reply_markup=await kb.go_back())

@router.callback_query(lambda f: f.data == 'Контакты преподавателей')
async def teach_contacts(callback: CallbackQuery):
    await callback.message.answer(await teach_contact(group_id), reply_markup=await kb.go_back())

@router.callback_query(lambda f: f.data == 'Рассылка')
async def mailing(callback: CallbackQuery):
    await callback.message.answer('СКОРО')

@router.callback_query(lambda f: f.data == 'Админ панель')
async def admin_panel(callback: CallbackQuery):
    await callback.answer(rf'Вы вошли в панель как: {user}')
    if user in admin:
        await callback.message.answer('Выберите:', reply_markup=await kb.admin_panel())
    else:
        await callback.message.answer('Отказано в доступе')

@router.callback_query(lambda f: f.data == 'Отправить сообщение')
async def message_sending(callback: CallbackQuery):
    await callback.message.answer('Выберите:', reply_markup=await kb.choice_1())

@router.callback_query(lambda f: f.data in ['В группу', 'Всем'])
async def message_sending(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст для рассылки:")
    if callback.data == 'В группу':
        group_members = await rq.get_users_from_group(group_values)
        await state.update_data(group_members=group_members)
        await state.set_state(Mailing.waiting_for_text)
    if callback.data == 'Всем':
        await state.update_data(group_members=[_[0] for _ in users])
        await state.set_state(Mailing.waiting_for_text)

@router.callback_query(lambda f: f.data == 'Управление админами')
async def admin_control(callback: CallbackQuery):
    await callback.message.answer("Выберите действие:", reply_markup=await kb.choice_2())

@router.callback_query(lambda f: f.data == 'Добавить админа')
async def add_admin(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Напишите тег админа, которого хотите добавить", reply_markup=await kb.choice_2())
    await state.set_state(AdminAdd.waiting_for_text)
    admin.append(callback.message.text)
    await callback.message.answer(f"Успешно добавлен тег админа: {callback.message.text}", reply_markup=await kb.go_back())
    await state.clear()

@router.callback_query(lambda f: f.data == 'Расписание')
async def schedule_func(callback: CallbackQuery):
    for day, sch in schedule(group_id).items():
        subjects = "\n".join(sch)
        await callback.message.answer(f"""
{day}
{subjects}""")

@router.callback_query(lambda f: f.data == 'change')
async def other(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg.course)

    await callback.message.answer(r""" 
Заполняем группу снова.
Выбери год обучения:""", reply_markup=await kb.inline_courses())

@router.callback_query(lambda f: f.data == 'back')
async def back_button(callback: CallbackQuery):
    await callback.message.answer('Выбери свой вариант:', reply_markup=await kb.inline_options(user))